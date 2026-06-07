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


async def handle_search_object(
    mcp_client: Any,
    description: str,
) -> str:
    result = await mcp_client.call_tool(
        "search_object", {"description": description}
    )

    try:
        data = json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return "Erro ao interpretar o resultado da busca."

    status = data.get("status", "error")

    if status == "found":
        obj_type = data.get("object_type", "objeto")
        obj_color = data.get("object_color")
        distancia = data.get("final_distance_cm")

        cor_str = f" {obj_color}" if obj_color else ""
        dist_str = f" a aproximadamente {int(distancia)}cm" if distancia is not None else ""
        return f"Encontrei o {obj_type}{cor_str}! Estou{dist_str} dele."

    if status == "not_found":
        obj_type = data.get("object_type", "objeto")
        obj_color = data.get("object_color")
        reason = data.get("reason", "")

        desc = f"{obj_color} {obj_type}" if obj_color else obj_type
        motivo_msg = {
            "could not center": "Nao consegui centralizar o objeto.",
            "obstacle too close": "O obstaculo esta muito proximo para aproximacao segura.",
            "object too far": "O objeto esta muito distante para aproximacao segura.",
            "lost tracking after rescan": "Perdi o rastreamento do objeto.",
            "max approach steps exceeded": "Nao consegui me aproximar o suficiente.",
        }.get(reason, "")

        if motivo_msg:
            return f"Nao encontrei o {desc}. {motivo_msg}"
        return f"Nao encontrei o {desc}."

    if status == "error":
        error_msg = data.get("error", "erro desconhecido")
        return f"Erro durante a busca: {error_msg}"

    return f"Resultado da busca: {result}"
