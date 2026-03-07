"""
voice_listener.py — Continuous speech-to-text using faster-whisper + sounddevice.

Captures audio from the microphone, detects speech segments via energy-based VAD,
and transcribes each segment with faster-whisper (CTranslate2 backend, int8).

Designed to run on Raspberry Pi — int8 quantisation gives 4-6× speed-up over
float32 on CPU with minimal accuracy loss.

Usage (standalone):
    python voice_listener.py          # base model, default mic
    python voice_listener.py --help
"""

from __future__ import annotations

import queue
import sys
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


# ── constants ──────────────────────────────────────────────────────────────────

_BLOCK_SIZE = 4_000       # audio frames per callback chunk (~250 ms at 16 kHz)
_SAMPLE_RATE = 16_000     # Hz — Whisper's native rate


class VoiceListener:
    """Streams audio from a microphone and transcribes speech with faster-whisper.

    The listener uses a simple energy-based silence detector to segment the
    audio into speech chunks.  Each chunk is passed to Whisper once a pause is
    detected.

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
    silence_threshold : float
        RMS amplitude below which audio is considered silent (0–1 scale on
        normalised float32 audio).  Lower = more sensitive.
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
        model_size: str = "base",
        sample_rate: int = _SAMPLE_RATE,
        device: Optional[int] = None,
        language: str = "pt",
        silence_threshold: float = 0.015,
        silence_duration: float = 1.2,
        on_result: Optional[Callable[[str], None]] = None,
        on_partial: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.sample_rate = sample_rate
        self.device = device
        self.language = language
        self.silence_threshold = silence_threshold
        self._silence_chunks_needed = max(
            1, int(silence_duration * sample_rate / _BLOCK_SIZE)
        )

        self._audio_q: queue.Queue[np.ndarray] = queue.Queue()
        self._on_result = on_result or self._default_result
        self._on_partial = on_partial or self._default_partial

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
    def _is_silent(self, chunk: np.ndarray) -> bool:
        rms = float(np.sqrt(np.mean(chunk ** 2)))
        return rms < self.silence_threshold

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
        segments, _ = self._model.transcribe(
            audio,
            language=self.language,
            beam_size=5,
            vad_filter=True,        # built-in Silero VAD — skips silence
            vad_parameters={
                "min_silence_duration_ms": 300,
                "speech_pad_ms": 200,
            },
        )
        return " ".join(seg.text.strip() for seg in segments)

    # -- public API ---------------------------------------------------------
    def listen(self) -> None:
        """Start listening (blocking).  Press Ctrl-C to stop."""
        device_label = "padrão" if self.device is None else str(self.device)
        print(
            f"🎤 Escutando no dispositivo [{device_label}] "
            f"@ {self.sample_rate} Hz  —  Ctrl-C para parar\n"
        )

        audio_buffer: list[np.ndarray] = []
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
                        speaking = True
                        silence_counter = 0
                        audio_buffer.append(chunk)
                        self._on_partial("ouvindo ...")

                    else:
                        if speaking:
                            silence_counter += 1
                            audio_buffer.append(chunk)   # include trailing silence

                            if silence_counter >= self._silence_chunks_needed:
                                # ── speech segment ended — transcribe ──────
                                audio_np = np.concatenate(audio_buffer)
                                audio_buffer = []
                                silence_counter = 0
                                speaking = False

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
