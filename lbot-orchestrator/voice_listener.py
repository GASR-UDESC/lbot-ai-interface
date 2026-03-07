"""
voice_listener.py — Continuous speech-to-text using faster-whisper + sounddevice.

Captures audio from the microphone, detects speech segments via energy-based VAD
with adaptive threshold + pre-buffering, and transcribes each segment with
faster-whisper (CTranslate2 backend, int8).

Improvements over v0.2:
    • Ring-buffer pre-capture (~500 ms) so the start of speech is never clipped.
    • Adaptive RMS threshold based on ambient noise floor (auto-calibrated).
    • Audio normalisation before transcription (peak-normalise to –1 dBFS).
    • Whisper initial_prompt with domain-specific robot vocabulary → fewer
      hallucinations and better accuracy for Portuguese commands.
    • Larger default beam_size (8) and tuned Silero VAD parameters.
    • Default model upgraded from "base" to "small" for higher accuracy.
    • Minimum speech duration filter to discard very short noise bursts.

Designed to run on Raspberry Pi — int8 quantisation gives 4-6× speed-up over
float32 on CPU with minimal accuracy loss.

Usage (standalone):
    python voice_listener.py          # small model, default mic
    python voice_listener.py --help
"""

from __future__ import annotations

import collections
import queue
import sys
import time
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


# ── constants ──────────────────────────────────────────────────────────────────

_BLOCK_SIZE = 2_400       # audio frames per callback chunk (~150 ms at 16 kHz)
_SAMPLE_RATE = 16_000     # Hz — Whisper's native rate

# Minimum speech duration in seconds to be worth transcribing.
# Anything shorter (clicks, pops, etc.) is discarded.
_MIN_SPEECH_DURATION = 0.4

# Number of pre-buffer chunks to keep (~500 ms of audio before speech starts)
_PRE_BUFFER_CHUNKS = 4

# Domain-specific prompt that primes Whisper for the robot vocabulary.
# This dramatically reduces hallucinations and improves accuracy for
# domain-specific terms that Whisper would otherwise mis-transcribe.
_INITIAL_PROMPT = (
    "Comando para o robô L-Bot: andar para frente, virar à esquerda, "
    "virar à direita, parar, mover para trás, girar, levantar braço, "
    "abaixar braço, velocidade, graus, centímetros, metros, abrir garra, "
    "fechar garra, ligar, desligar, posição inicial, sensor, distância, "
    "ângulo, repetir, esperar, seguir linha, desviar obstáculo."
)


class VoiceListener:
    """Streams audio from a microphone and transcribes speech with faster-whisper.

    The listener uses an adaptive energy-based silence detector with a ring-
    buffer pre-capture to segment the audio into speech chunks.  Each chunk
    is peak-normalised and passed to Whisper once a pause is detected.

    Parameters
    ----------
    model_size : str
        Whisper model variant: ``"tiny"`` (~75 MB), ``"base"`` (~145 MB) or
        ``"small"`` (~244 MB).  Models are auto-downloaded on first use.
    sample_rate : int
        Audio sample rate in Hz (default 16 000).
    device : int | None
        ``sounddevice`` device index.  ``None`` = system default input.
    language : str
        BCP-47 language code for Whisper.  Default ``"pt"`` (Portuguese).
    silence_threshold : float | None
        RMS amplitude below which audio is considered silent (0–1 scale on
        normalised float32 audio).  ``None`` = auto-calibrate from ambient
        noise on startup (recommended).
    silence_duration : float
        Seconds of silence required to conclude a speech segment and trigger
        transcription.
    on_result : callable(str) | None
        Called with the final transcription of each speech segment.
    on_partial : callable(str) | None
        Called when speech is detected but not yet transcribed (status hint).
    """

    def __init__(
        self,
        model_size: str = "small",
        sample_rate: int = _SAMPLE_RATE,
        device: Optional[int] = None,
        language: str = "pt",
        silence_threshold: Optional[float] = None,
        silence_duration: float = 1.0,
        on_result: Optional[Callable[[str], None]] = None,
        on_partial: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self.language = language
        self.silence_threshold = silence_threshold  # None → auto-calibrate
        self._silence_chunks_needed = max(
            1, int(silence_duration * sample_rate / _BLOCK_SIZE)
        )
        self._min_speech_chunks = max(
            1, int(_MIN_SPEECH_DURATION * sample_rate / _BLOCK_SIZE)
        )

        self._audio_q: queue.Queue[np.ndarray] = queue.Queue()
        self._on_result = on_result or self._default_result
        self._on_partial = on_partial or self._default_partial

        # Ring buffer to keep the last N chunks of audio (pre-buffer).
        # This ensures we never clip the beginning of a speech segment.
        self._pre_buffer: collections.deque[np.ndarray] = collections.deque(
            maxlen=_PRE_BUFFER_CHUNKS
        )

        # Load model --------------------------------------------------------
        print(
            f"⏳ Carregando modelo Whisper '{model_size}' "
            f"(primeira execução realiza download automático) ..."
        )
        self._model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print(f"✔ Modelo '{model_size}' pronto\n")

    # -- sounddevice callback (runs in a C audio thread) --------------------
    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        if status:
            print(f"[AUDIO] {status}", file=sys.stderr)
        self._audio_q.put(indata[:, 0].copy())   # keep only channel 0 → 1-D

    # -- silence detection --------------------------------------------------
    @staticmethod
    def _rms(chunk: np.ndarray) -> float:
        """Compute RMS energy of an audio chunk."""
        return float(np.sqrt(np.mean(chunk ** 2)))

    def _is_silent(self, chunk: np.ndarray) -> bool:
        return self._rms(chunk) < self.silence_threshold

    # -- ambient noise calibration ------------------------------------------
    def _calibrate_threshold(self) -> None:
        """Record ~1.5 s of ambient noise and set threshold adaptively.

        The threshold is set to 2.5× the mean ambient RMS so that normal
        background noise is classified as silence while speech (usually 5-15×
        louder) is reliably detected.
        """
        print("🔇 Calibrando ruído ambiente — fique em silêncio por 1.5 s ...")
        calibration_chunks: list[float] = []
        calibration_samples = int(1.5 * self.sample_rate / _BLOCK_SIZE)

        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=_BLOCK_SIZE,
            device=self.device,
            dtype="float32",
            channels=1,
            callback=self._audio_callback,
        ):
            for _ in range(calibration_samples):
                chunk = self._audio_q.get()
                calibration_chunks.append(self._rms(chunk))

        # Drain any leftover chunks from the queue
        while not self._audio_q.empty():
            try:
                self._audio_q.get_nowait()
            except queue.Empty:
                break

        ambient_rms = float(np.mean(calibration_chunks))
        # Set threshold to 2.5× ambient noise; clamp to a sensible range
        self.silence_threshold = max(0.005, min(0.08, ambient_rms * 2.5))
        print(
            f"   Ruído ambiente RMS: {ambient_rms:.4f}  →  "
            f"threshold: {self.silence_threshold:.4f}\n"
        )

    # -- audio normalisation ------------------------------------------------
    @staticmethod
    def _normalise(audio: np.ndarray) -> np.ndarray:
        """Peak-normalise audio to –1 dBFS (≈ 0.89 amplitude).

        This ensures Whisper always receives audio at a consistent level
        regardless of microphone gain settings.
        """
        peak = np.max(np.abs(audio))
        if peak < 1e-6:
            return audio                       # silence — nothing to do
        target = 10 ** (-1.0 / 20.0)          # –1 dBFS ≈ 0.891
        return audio * (target / peak)

    # -- default display callbacks ------------------------------------------
    @staticmethod
    def _default_partial(text: str) -> None:
        print(f"\r\033[90m  🎙  {text}\033[0m", end="", flush=True)

    @staticmethod
    def _default_result(text: str) -> None:
        if text.strip():
            print(f"\r\033[K\033[1m  >> {text.strip()}\033[0m")

    # -- transcription ------------------------------------------------------
    def _transcribe(self, audio: np.ndarray) -> str:
        # Normalise volume before sending to Whisper
        audio = self._normalise(audio)

        segments, info = self._model.transcribe(
            audio,
            language=self.language,
            beam_size=8,
            best_of=3,
            patience=1.5,
            initial_prompt=_INITIAL_PROMPT,
            vad_filter=True,        # built-in Silero VAD — skips silence
            vad_parameters={
                "min_silence_duration_ms": 250,
                "speech_pad_ms": 300,
                "threshold": 0.35,
            },
            condition_on_previous_text=False,
            no_speech_threshold=0.5,
            compression_ratio_threshold=2.4,
        )

        parts: list[str] = []
        for seg in segments:
            text = seg.text.strip()
            # Skip very short or low-confidence segments that are likely noise
            if text and seg.no_speech_prob < 0.7:
                parts.append(text)
        return " ".join(parts)

    # -- public API ---------------------------------------------------------
    def listen(self) -> None:
        """Start listening (blocking).  Press Ctrl-C to stop."""
        # Auto-calibrate silence threshold if not explicitly set
        if self.silence_threshold is None:
            self._calibrate_threshold()

        device_label = "padrão" if self.device is None else str(self.device)
        print(
            f"🎤 Escutando no dispositivo [{device_label}] "
            f"@ {self.sample_rate} Hz  —  Ctrl-C para parar\n"
        )

        audio_buffer: list[np.ndarray] = []
        speech_chunks_count = 0
        silence_counter = 0
        speaking = False

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                blocksize=_BLOCK_SIZE,
                device=self.device,
                dtype="float32",
                channels=1,
                callback=self._audio_callback,
            ):
                while True:
                    chunk = self._audio_q.get()

                    if not self._is_silent(chunk):
                        if not speaking:
                            # ── Speech just started — prepend pre-buffer ──
                            # This recovers audio from BEFORE the threshold
                            # was crossed, so we never clip the first syllable.
                            speaking = True
                            audio_buffer = list(self._pre_buffer)
                            speech_chunks_count = 0

                        silence_counter = 0
                        speech_chunks_count += 1
                        audio_buffer.append(chunk)
                        self._on_partial("ouvindo ...")

                    else:
                        # Always feed the pre-buffer (even during silence)
                        self._pre_buffer.append(chunk)

                        if speaking:
                            silence_counter += 1
                            audio_buffer.append(chunk)   # include trailing silence

                            if silence_counter >= self._silence_chunks_needed:
                                # ── speech segment ended — transcribe ──────
                                audio_np = np.concatenate(audio_buffer)
                                audio_buffer = []
                                silence_counter = 0
                                speaking = False
                                speech_chunks_count = 0

                                # Skip very short bursts (clicks, bumps, etc.)
                                duration = len(audio_np) / self.sample_rate
                                if duration < _MIN_SPEECH_DURATION:
                                    self._on_partial("")
                                    continue

                                self._on_partial("transcrevendo ...")
                                text = self._transcribe(audio_np)
                                self._on_result(text)

        except KeyboardInterrupt:
            # Flush any remaining audio
            if audio_buffer and speaking:
                audio_np = np.concatenate(audio_buffer)
                text = self._transcribe(audio_np)
                self._on_result(text)
            print("\n\n⏹  Parado.")
        except Exception as exc:
            sys.exit(f"[ERRO] {exc}")
