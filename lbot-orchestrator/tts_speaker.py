"""
tts_speaker.py — Offline text-to-speech using piper-tts.

Synthesises Portuguese text to audio and plays it through the system speakers
using sounddevice.  Uses piper (ONNX-based neural TTS) for high-quality,
low-latency speech synthesis that runs fully offline — ideal for Raspberry Pi.

Usage (standalone):
    python tts_speaker.py                          # default model
    python tts_speaker.py --model models/pt_BR-faber-medium.onnx
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from piper import PiperVoice
from piper.config import SynthesisConfig

_DEFAULT_MODEL = "models/pt_BR-faber-medium.onnx"


class TTSSpeaker:
    """Offline TTS speaker backed by piper-tts.

    Parameters
    ----------
    model_path : str | Path
        Path to the ``.onnx`` piper voice model.  The companion ``.onnx.json``
        config file must be alongside it (auto-discovered by piper).
    speaker_id : int | None
        Speaker index for multi-speaker models.  ``None`` = default speaker.
    """

    def __init__(
        self,
        model_path: str | Path = _DEFAULT_MODEL,
        speaker_id: Optional[int] = None,
    ) -> None:
        model_path = Path(model_path)
        if not model_path.exists():
            raise FileNotFoundError(
                f"Modelo TTS não encontrado: {model_path}\n"
                f"Execute:  bash setup_model.sh  para baixar o modelo."
            )

        print(f"⏳ Carregando modelo TTS '{model_path.stem}' ...")
        self._voice = PiperVoice.load(str(model_path), use_cuda=False)
        self._syn_config = SynthesisConfig(speaker_id=speaker_id)

        # Read sample rate from the loaded model config
        self._sample_rate: int = self._voice.config.sample_rate
        print(f"✔ TTS pronto (piper, {self._sample_rate} Hz)\n")

    def speak(self, text: str) -> None:
        """Synthesise *text* and play it through the default audio output.

        This method blocks until playback is complete.
        """
        text = text.strip()
        if not text:
            return

        # Synthesise — piper v1.4 returns AudioChunk objects with raw arrays
        chunks = list(self._voice.synthesize(text, self._syn_config))
        if not chunks:
            return

        audio = np.concatenate([c.audio_int16_array for c in chunks])
        sd.play(audio, samplerate=self._sample_rate)
        sd.wait()


# ── Standalone test ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Teste do TTS piper offline")
    parser.add_argument(
        "--model",
        default=_DEFAULT_MODEL,
        help=f"Caminho do modelo .onnx. Padrão: {_DEFAULT_MODEL}",
    )
    parser.add_argument(
        "--text",
        default="Olá! Eu sou o L-Bot, seu assistente robótico.",
        help="Texto para sintetizar.",
    )
    args = parser.parse_args()

    tts = TTSSpeaker(model_path=args.model)
    print(f"  🔊 \"{args.text}\"")
    tts.speak(args.text)
    print("  ✔ Reprodução concluída.")
