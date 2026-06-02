import os
import sys
import logging

logger = logging.getLogger(__name__)

_current_dir = os.path.dirname(os.path.abspath(__file__))
_lbot_mcp_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_current_dir))))
_translator_dir = os.path.join(_lbot_mcp_root, "lbot-natural-language-controller", "lbot-v7")

if _translator_dir not in sys.path:
    sys.path.insert(0, _translator_dir)

_MODEL_PATH = os.path.join(_translator_dir, "lbot_translator_v7.pt")


class TranslationError(Exception):
    pass


class TranslatorWrapper:
    _instance: "TranslatorWrapper | None" = None
    _translator = None

    def __new__(cls) -> "TranslatorWrapper":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def is_loaded(self) -> bool:
        return self._translator is not None

    def _ensure_loaded(self):
        if self._translator is not None:
            return

        try:
            import lbot_v7
            from lbot_v7 import LBotTranslatorV7
        except ImportError as e:
            raise TranslationError(
                f"Não foi possível importar o LBotTranslatorV7. "
                f"Verifique se o diretório '{_translator_dir}' está acessível."
            ) from e

        if not os.path.exists(_MODEL_PATH):
            raise TranslationError(
                f"Modelo não encontrado em '{_MODEL_PATH}'. "
                f"Execute o treinamento primeiro."
            )

        import __main__

        _patch_main = [
            "Seq2SeqConfig",
            "Seq2Seq",
            "Encoder",
            "Decoder",
            "BahdanauAttention",
            "Vocabulary",
        ]
        for name in _patch_main:
            if hasattr(lbot_v7, name):
                setattr(__main__, name, getattr(lbot_v7, name))

        try:
            self._translator = LBotTranslatorV7(model_path=_MODEL_PATH)
        finally:
            for name in _patch_main:
                if hasattr(__main__, name):
                    delattr(__main__, name)

        logger.info(
            "Tradutor carregado: device=%s, params=%s",
            self._translator.device,
            sum(p.numel() for p in self._translator.model.parameters()),
        )

    def translate(self, command: str) -> str:
        self._ensure_loaded()
        result = self._translator.translate(command)
        if result == "ERRO":
            raise TranslationError(f"Não entendi o comando: '{command}'")
        return result

    def translate_verbose(self, command: str) -> tuple[str, str, str]:
        self._ensure_loaded()
        return self._translator.translate_verbose(command)
