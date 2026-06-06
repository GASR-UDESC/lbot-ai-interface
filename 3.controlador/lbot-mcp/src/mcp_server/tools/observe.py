import asyncio
import json

import httpx

from ..server import mcp
from ..context import get_backend


@mcp.tool()
async def observe() -> str:
    """Retorna simultaneamente a imagem da camera e os dados de proximidade (frente e tras). Destinada ao uso durante Tarefas (busca, aproximacao, navegacao condicional)."""
    backend = get_backend()

    async def _safe_camera():
        try:
            return await backend.get_camera()
        except (RuntimeError, httpx.TimeoutException, Exception) as e:
            return {"_error": str(e)}

    async def _safe_proximity():
        try:
            return await backend.get_proximity()
        except (RuntimeError, httpx.TimeoutException, Exception) as e:
            return {"_error": str(e)}

    camera_result, prox_result = await asyncio.gather(
        _safe_camera(), _safe_proximity()
    )

    camera_ok = "_error" not in camera_result
    prox_ok = "_error" not in prox_result

    if not camera_ok and not prox_ok:
        return json.dumps({
            "camera_error": camera_result["_error"],
            "proximity_error": prox_result["_error"],
        })

    result = {}

    if camera_ok:
        result["image"] = camera_result.get("image")
        result["render_method"] = camera_result.get("render_method", "unknown")
        result["robot_position"] = camera_result.get("robot_position")
    else:
        result["camera_error"] = camera_result["_error"]

    if prox_ok:
        result["proximity"] = prox_result
    else:
        result["proximity_error"] = prox_result["_error"]

    return json.dumps(result)
