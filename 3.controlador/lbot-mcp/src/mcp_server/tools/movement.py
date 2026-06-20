import re
import httpx

from ..server import mcp
from ..context import get_backend

LBML_SEQUENCE_RE = re.compile(r"^(D\d+[FBLR];|R\d+[LR];)+$")


@mcp.tool()
async def move(command: str) -> str:
    """Executa um movimento do robô. O comando deve ser em linguagem natural (português). Exemplos: 'ande 30cm para frente', 'vire 90 graus para direita', 'ande 15cm para frente, depois vire 180 graus'. O movimento é relativo à posição atual do robô."""
    if not LBML_SEQUENCE_RE.match(command):
        return (
            "Erro: formato LBML invalido. "
            "Use o formato 'D30F;R90L;' "
            "(D=deslocamento em cm, R=rotacao em graus; "
            "F=frente, B=tras, L=esquerda, R=direita)."
        )

    try:
        backend = get_backend()
        result = await backend.execute_lbml(command)

        if result.get("accepted"):
            return f"Comando executado: {command}"
        else:
            error_msg = result.get("error", "falha na execucao")
            return f"Erro: falha na execucao — {error_msg}"

    except RuntimeError as e:
        error_str = str(e)
        if "409" in error_str:
            return "Erro: o simulador nao esta conectado. Abra o simulador no navegador para executar movimentos."
        return f"Erro: falha na execucao — {e}"
    except httpx.TimeoutException:
        return "Erro: timeout ao executar movimento."
    except Exception as e:
        return f"Erro: falha na execucao — {e}"
