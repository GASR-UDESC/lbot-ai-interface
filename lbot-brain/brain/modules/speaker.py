from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import sounddevice as sd
from piper import PiperVoice
from piper.config import SynthesisConfig


class Speaker:
    """Encapsulates text-to-speech with piper-tts."""

    def __init__(
        self,
        model_path: str | Path,
        speaker_id: Optional[int] = None,
    ) -> None:
        resolved_model_path = Path(model_path).expanduser().resolve()
        if not resolved_model_path.exists():
            raise FileNotFoundError(
                f"TTS model not found: {resolved_model_path}. "
                "Use --tts-model to set a valid model path."
            )

        self._voice = PiperVoice.load(str(resolved_model_path), use_cuda=False)
        self._syn_config = SynthesisConfig(speaker_id=speaker_id)
        self._sample_rate = self._voice.config.sample_rate

    def speak(self, text: str) -> None:
        """Synthesizes text and blocks until playback ends."""
        clean_text = text.strip()
        if not clean_text:
            return

        chunks = list(self._voice.synthesize(clean_text, self._syn_config))
        if not chunks:
            return

        audio = np.concatenate([chunk.audio_int16_array for chunk in chunks])
        sd.play(audio, samplerate=self._sample_rate)
        sd.wait()
