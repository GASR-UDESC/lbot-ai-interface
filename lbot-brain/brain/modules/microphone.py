from __future__ import annotations

import collections
import queue
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


BLOCK_SIZE = 2_400
DEFAULT_SAMPLE_RATE = 16_000
MIN_SPEECH_DURATION = 0.4
PRE_BUFFER_CHUNKS = 4
INITIAL_PROMPT = (
    "Comando para o robo L-Bot: andar para frente, virar a esquerda, "
    "virar a direita, parar, mover para tras, girar, levantar braco, "
    "abaixar braco, velocidade, graus, centimetros, metros, abrir garra, "
    "fechar garra, ligar, desligar, posicao inicial, sensor, distancia, "
    "angulo, repetir, esperar, seguir linha, desviar obstaculo."
)


class Microphone:
    """Encapsulates microphone capture and STT transcription."""

    def __init__(
        self,
        model_size: str = "small",
        sample_rate: int = DEFAULT_SAMPLE_RATE,
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
        self.silence_threshold = silence_threshold
        self._silence_chunks_needed = max(
            1, int(silence_duration * sample_rate / BLOCK_SIZE)
        )

        self._audio_q: queue.Queue[np.ndarray] = queue.Queue()
        self._on_result = on_result or self._default_result
        self._on_partial = on_partial or self._default_partial

        self._pre_buffer: collections.deque[np.ndarray] = collections.deque(
            maxlen=PRE_BUFFER_CHUNKS
        )

        self._active = threading.Event()
        self._active.set()

        self._model = WhisperModel(model_size, device="cpu", compute_type="int8")

    def set_on_result(self, callback: Callable[[str], None]) -> None:
        self._on_result = callback

    def set_on_partial(self, callback: Callable[[str], None]) -> None:
        self._on_partial = callback

    def pause(self) -> None:
        self._active.clear()

    def resume(self) -> None:
        while not self._audio_q.empty():
            try:
                self._audio_q.get_nowait()
            except queue.Empty:
                break
        self._pre_buffer.clear()
        self._active.set()

    def listen(self) -> None:
        if self.silence_threshold is None:
            self._calibrate_threshold()

        audio_buffer: list[np.ndarray] = []
        silence_counter = 0
        speaking = False

        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=BLOCK_SIZE,
            device=self.device,
            dtype="float32",
            channels=1,
            callback=self._audio_callback,
        ):
            while True:
                chunk = self._audio_q.get()

                if not self._active.is_set():
                    continue

                if not self._is_silent(chunk):
                    if not speaking:
                        speaking = True
                        audio_buffer = list(self._pre_buffer)

                    silence_counter = 0
                    audio_buffer.append(chunk)
                    self._on_partial("ouvindo ...")
                else:
                    self._pre_buffer.append(chunk)

                    if speaking:
                        silence_counter += 1
                        audio_buffer.append(chunk)

                        if silence_counter >= self._silence_chunks_needed:
                            audio_np = np.concatenate(audio_buffer)
                            audio_buffer = []
                            silence_counter = 0
                            speaking = False

                            duration = len(audio_np) / self.sample_rate
                            if duration < MIN_SPEECH_DURATION:
                                self._on_partial("")
                                continue

                            self._on_partial("transcrevendo ...")
                            text = self._transcribe(audio_np)
                            self._on_result(text)

    def _audio_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time_info: dict,
        status: sd.CallbackFlags,
    ) -> None:
        del frames, time_info, status
        self._audio_q.put(indata[:, 0].copy())

    @staticmethod
    def _rms(chunk: np.ndarray) -> float:
        return float(np.sqrt(np.mean(chunk ** 2)))

    def _is_silent(self, chunk: np.ndarray) -> bool:
        return self._rms(chunk) < self.silence_threshold

    def _calibrate_threshold(self) -> None:
        calibration_chunks: list[float] = []
        calibration_samples = int(1.5 * self.sample_rate / BLOCK_SIZE)

        with sd.InputStream(
            samplerate=self.sample_rate,
            blocksize=BLOCK_SIZE,
            device=self.device,
            dtype="float32",
            channels=1,
            callback=self._audio_callback,
        ):
            for _ in range(calibration_samples):
                chunk = self._audio_q.get()
                calibration_chunks.append(self._rms(chunk))

        while not self._audio_q.empty():
            try:
                self._audio_q.get_nowait()
            except queue.Empty:
                break

        ambient_rms = float(np.mean(calibration_chunks))
        self.silence_threshold = max(0.005, min(0.08, ambient_rms * 2.5))

    @staticmethod
    def _normalise(audio: np.ndarray) -> np.ndarray:
        peak = np.max(np.abs(audio))
        if peak < 1e-6:
            return audio
        target = 10 ** (-1.0 / 20.0)
        return audio * (target / peak)

    def _transcribe(self, audio: np.ndarray) -> str:
        audio = self._normalise(audio)
        segments, _ = self._model.transcribe(
            audio,
            language=self.language,
            beam_size=8,
            best_of=3,
            patience=1.5,
            initial_prompt=INITIAL_PROMPT,
            vad_filter=True,
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
        for segment in segments:
            text = segment.text.strip()
            if text and segment.no_speech_prob < 0.7:
                parts.append(text)
        return " ".join(parts)

    @staticmethod
    def _default_partial(text: str) -> None:
        if text:
            print(f"[STT] {text}")

    @staticmethod
    def _default_result(text: str) -> None:
        clean_text = text.strip()
        if clean_text:
            print(f"[STT] {clean_text}")
