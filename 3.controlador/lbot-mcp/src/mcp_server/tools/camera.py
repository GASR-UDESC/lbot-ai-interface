from ..context import get_backend
from ..server import mcp


@mcp.tool()
async def camera() -> dict:
    """Observa a câmera frontal atual. Use para descrever o ambiente; nunca estime distâncias pela imagem."""
    try:
        return {"status": "completed", **await get_backend().get_camera()}
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
