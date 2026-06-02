import httpx

from ..server import mcp
from ..context import get_backend


@mcp.tool()
async def camera() -> str:
    """Captura uma imagem da câmera frontal do robô. Retorna a imagem em formato PNG codificada em base64."""
    try:
        backend = get_backend()
        image = await backend.get_camera()
        return image
    except RuntimeError as e:
        return f"Erro: câmera indisponível — não foi possível capturar a imagem. ({e})"
    except httpx.TimeoutException:
        return "Erro: timeout ao capturar imagem da câmera."
    except Exception as e:
        return f"Erro: {e}"
