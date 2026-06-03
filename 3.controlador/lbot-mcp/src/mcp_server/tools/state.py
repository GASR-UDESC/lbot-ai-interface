import json

import httpx

from ..context import get_backend
from ..server import mcp


@mcp.tool()
async def state() -> str:
    try:
        backend = get_backend()
        data = await backend.get_state()
        if data is None:
            return json.dumps({"error": "estado indisponivel"}, ensure_ascii=False)
        return json.dumps(data, ensure_ascii=False)
    except RuntimeError as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
    except httpx.TimeoutException:
        return json.dumps({"error": "timeout ao consultar estado do robo"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
