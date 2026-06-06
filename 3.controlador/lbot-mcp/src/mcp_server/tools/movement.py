import re
import httpx

from ..server import mcp
from ..context import get_backend, get_translator
from ..translator import TranslationError

LBML_SEQUENCE_RE = re.compile(r"^(D\d+[FBLR];|R\d+[LR];)+$")


@mcp.tool()
async def move(command: str) -> str:
    """Move o robô de acordo com um comando. Aceita tanto linguagem natural (ex: 'ande 30cm para frente') quanto LBML direto (ex: 'D30F;R90L;')."""
    is_lbml_direct = bool(LBML_SEQUENCE_RE.match(command))

    if is_lbml_direct:
        lbml = command
    else:
        try:
            translator = get_translator()
            original, preprocessed, lbml = translator.translate_verbose(command)
        except TranslationError as e:
            return f"Erro: não entendi o comando '{command}'. Pode reformular? ({e})"

        if lbml == "ERRO" or not LBML_SEQUENCE_RE.match(lbml):
            return f"Erro: não entendi o comando '{command}'. Pode reformular?"

    try:
        backend = get_backend()
        result = await backend.execute_lbml(lbml)

        if result.get("accepted"):
            if is_lbml_direct:
                return f"Comando executado: {command} (LBML direto)"
            else:
                return f"Comando executado: {lbml} ({preprocessed})"
        else:
            error_msg = result.get("error", "falha na execução")
            return f"Erro: falha na execução — {error_msg}"

    except RuntimeError as e:
        error_str = str(e)
        if "409" in error_str:
            return "Erro: o simulador não está conectado. Abra o simulador no navegador para executar movimentos."
        return f"Erro: falha na execução — {e}"
    except httpx.TimeoutException:
        return "Erro: timeout ao executar movimento."
    except Exception as e:
        return f"Erro: falha na execução — {e}"
