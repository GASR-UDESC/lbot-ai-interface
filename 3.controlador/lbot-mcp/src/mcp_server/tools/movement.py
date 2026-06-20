import httpx

from ..server import mcp
from ..context import get_backend, get_translator
from ..translator import TranslationError


@mcp.tool()
async def move(command: str) -> str:
    """Executa um movimento do robô. O comando deve ser em linguagem natural (português). Exemplos: 'ande 30cm para frente', 'vire 90 graus para direita', 'ande 15cm para frente, depois vire 180 graus'. O movimento é relativo à posição atual do robô."""
    try:
        translator = get_translator()
        lbml = translator.translate(command)
    except TranslationError:
        return (
            "Erro: não entendi o comando. Use frases como "
            "'ande 30cm para frente', 'vire 90 graus para direita'."
        )

    try:
        backend = get_backend()
        result = await backend.execute_lbml(lbml)

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
