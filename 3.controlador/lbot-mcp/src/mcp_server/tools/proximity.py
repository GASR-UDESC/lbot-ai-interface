from ..context import get_backend
from ..server import mcp


@mcp.tool()
async def proximity() -> dict:
    """Mede obstáculos à frente e atrás em centímetros. Uma leitura indisponível não significa caminho livre."""
    try:
        return {"status": "completed", **await get_backend().get_proximity()}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
