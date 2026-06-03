import re
import json
import httpx

from ..server import mcp
from ..context import get_backend, get_translator
from ..translator import TranslationError

LBML_SEQUENCE_RE = re.compile(r"^(D\d+[FBLR];|R\d+[LR];)+$")


@mcp.tool()
async def move(command: str) -> str:
    """Move o robô de acordo com um comando em linguagem natural. O robô entende comandos como 'ande 30cm para frente', 'vire 90 graus para direita', ou sequências como 'ande 40cm para frente, depois vire 90 graus para esquerda'."""
    try:
        translator = get_translator()
        original, preprocessed, lbml = translator.translate_verbose(command)
    except TranslationError as e:
        return json.dumps(
            {
                "original_command": command,
                "accepted": False,
                "completed": False,
                "status": "translation_error",
                "needs_reobservation": False,
                "error": f"não entendi o comando '{command}'. Pode reformular? ({e})",
            },
            ensure_ascii=False,
        )

    if lbml == "ERRO" or not LBML_SEQUENCE_RE.match(lbml):
        return json.dumps(
            {
                "original_command": command,
                "accepted": False,
                "completed": False,
                "status": "translation_error",
                "needs_reobservation": False,
                "error": f"não entendi o comando '{command}'. Pode reformular?",
            },
            ensure_ascii=False,
        )

    try:
        backend = get_backend()
        result = await backend.execute_lbml(lbml)
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": result.get("accepted", False),
                "completed": result.get("completed", False),
                "status": result.get("status", "unknown"),
                "needs_reobservation": True,
                "request_id": result.get("request_id"),
                "target_client_id": result.get("target_client_id"),
                "final_state": result.get("final_state"),
                "message": result.get("message"),
                "summary": "movimento concluído" if result.get("completed") else "movimento aceito, mas sem confirmação final",
            },
            ensure_ascii=False,
        )

    except RuntimeError as e:
        error_str = str(e)
        if "409" in error_str:
            error_str = "o simulador não está conectado. Abra o simulador no navegador para executar movimentos."
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "execution_error",
                "needs_reobservation": False,
                "error": f"falha na execução — {error_str}",
            },
            ensure_ascii=False,
        )
    except httpx.TimeoutException:
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "timeout",
                "needs_reobservation": False,
                "error": "timeout ao executar movimento",
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "execution_error",
                "needs_reobservation": False,
                "error": f"falha na execução — {e}",
            },
            ensure_ascii=False,
        )
