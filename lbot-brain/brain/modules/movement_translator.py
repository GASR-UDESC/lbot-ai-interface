from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


class MovementTranslatorV7:
    """In-process adapter for lbot-v7 translator."""

    def __init__(self, model_path: str | Path | None = None) -> None:
        project_root = Path(__file__).resolve().parents[2]
        controller_root = project_root.parent / "lbot-natural-language-controller" / "lbot-v7"
        module_path = controller_root / "lbot_v7.py"
        resolved_model_path = Path(model_path or (controller_root / "lbot_translator_v7.pt")).resolve()

        if not module_path.exists():
            raise FileNotFoundError(f"lbot-v7 module not found: {module_path}")
        if not resolved_model_path.exists():
            raise FileNotFoundError(f"lbot-v7 model not found: {resolved_model_path}")

        module = self._load_module(module_path)
        self._bridge_torch_checkpoint_symbols(module)
        translator_cls = getattr(module, "LBotTranslatorV7", None)
        if translator_cls is None:
            raise RuntimeError("LBotTranslatorV7 class was not found in lbot_v7.py")

        self._translator = translator_cls(str(resolved_model_path))

    @staticmethod
    def _load_module(module_path: Path) -> ModuleType:
        spec = importlib.util.spec_from_file_location("lbot_v7_runtime", module_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Failed to load module spec from: {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    @staticmethod
    def _bridge_torch_checkpoint_symbols(module: ModuleType) -> None:
        """Expose lbot_v7 symbols in __main__ for legacy torch checkpoints."""
        main_module = sys.modules.get("__main__")
        if main_module is None:
            return

        for symbol in ("Seq2SeqConfig", "Vocabulary", "Seq2Seq"):
            if hasattr(module, symbol):
                setattr(main_module, symbol, getattr(module, symbol))

    def translate(self, text: str) -> str:
        """Translates natural language movement command to LBML."""
        normalized_text = text.strip()
        if not normalized_text:
            return ""
        return self._translator.translate(normalized_text)
