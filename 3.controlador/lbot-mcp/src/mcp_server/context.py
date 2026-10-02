from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .backends.base import LBotBackend
    from .translator import TranslatorWrapper

backend: "LBotBackend | None" = None


def get_backend() -> "LBotBackend":
    if backend is None:
        raise RuntimeError(
            "Backend não configurado. O servidor MCP não foi inicializado corretamente."
        )
    return backend


def get_translator() -> "TranslatorWrapper":
    from .translator import TranslatorWrapper

    return TranslatorWrapper()


_control = None


def get_control():
    global _control
    from .services.control import ControlService

    current = get_backend()
    if _control is None or _control.backend is not current:
        _control = ControlService(current)
    return _control
