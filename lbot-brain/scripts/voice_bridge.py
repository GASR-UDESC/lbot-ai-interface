#!/usr/bin/env python3

import argparse
import contextlib
import json
import logging
import os
import sys
import tempfile
import time
import wave
from collections import deque


def emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def parse_device(value: str):
    trimmed = value.strip()
    if not trimmed:
        return None

    try:
        return int(trimmed)
    except ValueError:
        return trimmed


class VoiceBridge:
    sample_rate = 16000
    frame_duration_ms = 30

    def __init__(self, args):
        self.args = args

        if not os.path.exists(args.stt_model):
            raise RuntimeError(
                f"Whisper model not found at {args.stt_model}. Set LBOT_STT_MODEL to a local faster-whisper model directory."
            )

        if not os.path.exists(args.tts_model):
            raise RuntimeError(
                f"Piper voice model not found at {args.tts_model}. Set LBOT_TTS_MODEL_PATH to a local .onnx voice file."
            )

        if not os.path.exists(f"{args.tts_model}.json"):
            raise RuntimeError(
                f"Piper voice config not found at {args.tts_model}.json. Piper requires the .onnx.json file next to the model."
            )

        try:
            import numpy as np
            import sounddevice as sd
            import webrtcvad
            from faster_whisper import WhisperModel
            from piper import PiperVoice
            from piper.config import SynthesisConfig
        except ImportError as error:
            raise RuntimeError(
                "Voice mode dependencies are missing. Install faster-whisper, piper-tts, sounddevice and webrtcvad in the configured Python environment."
            ) from error

        self.np = np
        self.sd = sd
        self.SynthesisConfig = SynthesisConfig
        self.vad = webrtcvad.Vad(args.stt_vad_mode)
        self.whisper_model = WhisperModel(
            args.stt_model,
            device=args.stt_device,
            compute_type=args.stt_compute_type,
        )
        self.voice = PiperVoice.load(args.tts_model)
        self.tts_config = SynthesisConfig(
            speaker_id=self.resolve_speaker_id(args.tts_speaker),
            length_scale=args.tts_length_scale,
            noise_scale=args.tts_noise_scale,
            noise_w_scale=args.tts_noise_w_scale,
            volume=args.tts_volume if args.tts_volume is not None else 1.0,
        )
        self.input_device = parse_device(args.audio_input_device)
        self.output_device = parse_device(args.audio_output_device)
        self.frame_samples = int(self.sample_rate * self.frame_duration_ms / 1000)
        self.preroll_frames = max(0, args.stt_preroll_ms // self.frame_duration_ms)

    def resolve_speaker_id(self, speaker_value: str):
        trimmed = speaker_value.strip()

        if not trimmed:
            return None

        try:
            return int(trimmed)
        except ValueError:
            speaker_id = self.voice.config.speaker_id_map.get(trimmed)
            if speaker_id is None:
                raise RuntimeError(
                    f"Unknown Piper speaker '{trimmed}'. Available speakers: {sorted(self.voice.config.speaker_id_map)}"
                )

            return speaker_id

    def listen_once(self):
        start_deadline = time.monotonic() + (self.args.stt_start_timeout_ms / 1000)
        silence_seconds = self.args.stt_silence_ms / 1000
        max_utterance_seconds = self.args.stt_max_utterance_ms / 1000
        captured_frames = []
        preroll_buffer = deque(maxlen=self.preroll_frames)
        heard_speech = False
        speech_started_at = None
        last_speech_at = None

        with self.sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_samples,
            channels=1,
            dtype="int16",
            device=self.input_device,
        ) as stream:
            while True:
                frame, overflowed = stream.read(self.frame_samples)
                if overflowed:
                    logging.debug("Audio input overflowed while listening.")

                frame_bytes = bytes(frame)
                is_speech = self.vad.is_speech(frame_bytes, self.sample_rate)
                now = time.monotonic()

                if not heard_speech:
                    preroll_buffer.append(frame_bytes)

                    if is_speech:
                        heard_speech = True
                        speech_started_at = now
                        last_speech_at = now
                        captured_frames.extend(preroll_buffer)
                        preroll_buffer.clear()
                        continue

                    if now >= start_deadline:
                        return {
                            "transcript": "",
                            "timedOut": True,
                            "heardSpeech": False,
                        }

                    continue

                captured_frames.append(frame_bytes)

                if is_speech:
                    last_speech_at = now
                elif last_speech_at is not None and (now - last_speech_at) >= silence_seconds:
                    break

                if speech_started_at is not None and (now - speech_started_at) >= max_utterance_seconds:
                    break

        transcript = self.transcribe_audio(b"".join(captured_frames))

        return {
            "transcript": transcript,
            "timedOut": False,
            "heardSpeech": True,
        }

    def transcribe_audio(self, audio_bytes: bytes) -> str:
        if not audio_bytes:
            return ""

        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            with wave.open(temp_file.name, "wb") as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_bytes)

            segments, _ = self.whisper_model.transcribe(
                temp_file.name,
                language=self.args.stt_language or None,
                beam_size=1,
                vad_filter=False,
                condition_on_previous_text=False,
            )

            return " ".join(segment.text.strip() for segment in segments if segment.text.strip()).strip()

    def speak(self, text: str):
        normalized = text.strip()
        if not normalized:
            return

        chunks = list(self.voice.synthesize(normalized, syn_config=self.tts_config))
        if not chunks:
            return

        audio = self.np.concatenate([chunk.audio_float_array for chunk in chunks]).astype(self.np.float32)
        self.sd.play(audio, self.voice.config.sample_rate, device=self.output_device, blocking=True)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Persistent stdin/stdout bridge for local voice mode")
    parser.add_argument("--stt-model", required=True)
    parser.add_argument("--stt-language", default="pt")
    parser.add_argument("--stt-device", default="cpu")
    parser.add_argument("--stt-compute-type", default="int8")
    parser.add_argument("--stt-start-timeout-ms", type=int, default=15000)
    parser.add_argument("--stt-silence-ms", type=int, default=900)
    parser.add_argument("--stt-max-utterance-ms", type=int, default=20000)
    parser.add_argument("--stt-vad-mode", type=int, default=2)
    parser.add_argument("--stt-preroll-ms", type=int, default=300)
    parser.add_argument("--audio-input-device", default="")
    parser.add_argument("--audio-output-device", default="")
    parser.add_argument("--tts-model", required=True)
    parser.add_argument("--tts-speaker", default="")
    parser.add_argument("--tts-length-scale", type=float)
    parser.add_argument("--tts-noise-scale", type=float)
    parser.add_argument("--tts-noise-w-scale", type=float)
    parser.add_argument("--tts-volume", type=float)
    return parser


def main() -> int:
    parser = build_argument_parser()
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

    with contextlib.redirect_stdout(sys.stderr):
        bridge = VoiceBridge(args)

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        request_id = None

        try:
            payload = json.loads(line)
            request_id = payload.get("id")
            request_type = payload.get("type")

            if request_type == "listen_once":
                with contextlib.redirect_stdout(sys.stderr):
                    result = bridge.listen_once()

                emit({
                    "id": request_id,
                    "ok": True,
                    **result,
                })
                continue

            if request_type == "speak":
                text = payload.get("text")
                if not isinstance(text, str):
                    raise ValueError("Speak request requires a string 'text' field.")

                with contextlib.redirect_stdout(sys.stderr):
                    bridge.speak(text)

                emit({
                    "id": request_id,
                    "ok": True,
                })
                continue

            raise ValueError(f"Unsupported voice request type: {request_type}")
        except Exception as error:
            emit({
                "id": request_id,
                "ok": False,
                "error": str(error),
            })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
