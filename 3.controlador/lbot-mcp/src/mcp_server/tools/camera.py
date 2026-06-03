import json

import httpx

from ..server import mcp
from ..context import get_backend


@mcp.tool()
async def camera() -> str:
    try:
        backend = get_backend()
        data = await backend.get_camera()
        return json.dumps(data)
    except RuntimeError as e:
        return json.dumps({"error": str(e)})
    except httpx.TimeoutException:
        return json.dumps({"error": "timeout ao capturar imagem da câmera"})
    except Exception as e:
        return json.dumps({"error": str(e)})