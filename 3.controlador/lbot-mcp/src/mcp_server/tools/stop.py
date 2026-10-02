from ..context import get_control
from ..server import mcp


@mcp.tool()
async def stop() -> dict:
    """Para imediatamente o movimento e cancela a habilidade em andamento."""
    try:
        return await get_control().stop()
    except Exception as e:
        return {"status": "failed", "reason": str(e)}
