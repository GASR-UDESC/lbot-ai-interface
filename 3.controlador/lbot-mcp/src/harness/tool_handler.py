import json
from typing import Any


class TranslationError(Exception):
    pass


async def handle_camera(
    mcp_client: Any,
) -> dict[str, Any]:
    result = await mcp_client.call_tool("camera", {})
    try:
        data = json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return {
            "image": "",
            "render_method": "unknown",
            "robot_position": None,
        }

    if isinstance(data, dict):
        return {
            "image": data.get("image", ""),
            "render_method": data.get("render_method", "unknown"),
            "robot_position": data.get("robot_position"),
        }
    return {"image": "", "render_method": "unknown", "robot_position": None}


async def handle_proximity(
    mcp_client: Any,
) -> str:
    return await mcp_client.call_tool("proximity", {})


async def handle_move(
    mcp_client: Any,
    command_nl: str,
) -> str:
    translate_result = await mcp_client.call_tool(
        "translate", {"command": command_nl}
    )

    lbml_text = translate_result.strip()
    if lbml_text == "ERRO" or not lbml_text:
        raise TranslationError(
            f"Não foi possível traduzir o comando: '{command_nl}'"
        )

    return await mcp_client.call_tool("move", {"command": lbml_text})
