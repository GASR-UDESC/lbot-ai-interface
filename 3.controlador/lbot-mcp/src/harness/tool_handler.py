import json
from typing import Any


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
    return await mcp_client.call_tool("move", {"command": command_nl})


async def handle_go_to(
    mcp_client: Any,
    target: str,
    direction: str = "frente",
) -> str:
    result = await mcp_client.call_tool(
        "go_to", {"target": target, "direction": direction}
    )

    try:
        data = json.loads(result)
    except (json.JSONDecodeError, TypeError):
        return "Erro ao interpretar o resultado do go_to."

    status = data.get("status", "error")

    if status == "found":
        alvo = data.get("target", "objetivo")
        dir_str = data.get("direction", "frente")
        distancia = data.get("final_distance_cm")

        dir_nomes = {
            "frente": "frente",
            "esquerda": "esquerda",
            "direita": "direita",
            "tras": "tras",
        }
        dir_nl = dir_nomes.get(dir_str, dir_str)

        dist_str = f" a aproximadamente {int(distancia)}cm" if distancia is not None else ""
        if "parede" in alvo.lower() or "muro" in alvo.lower():
            dist_str = f" a aproximadamente {int(distancia)}cm da parede" if distancia is not None else ""
            return f"Cheguei na parede a {dir_nl}! Estou{dist_str}."

        return f"Cheguei ate o {alvo} a {dir_nl}! Estou{dist_str} dele."

    if status == "not_found":
        alvo = data.get("target", "objetivo")
        reason = data.get("reason", "")

        motivo_msg = {
            "target not visible in direction": f"Nao vi nenhum {alvo} nessa direcao.",
            "LLM confirmed but OpenCV could not detect": "Vi o objeto com a camera, mas nao consegui detecta-lo com precisao.",
            "could not center": "Nao consegui centralizar o objeto.",
            "obstacle too close": "O obstaculo esta muito proximo para aproximacao segura.",
            "lost tracking": "Perdi o rastreamento do objeto durante a aproximacao.",
            "no obstacle detected": "Nao detectei nenhum obstaculo nessa direcao.",
            "max approach steps exceeded": "Nao consegui me aproximar o suficiente.",
            "could not center after approach step": "Nao consegui manter o objeto centralizado apos avancar.",
        }.get(reason, "")

        if motivo_msg:
            return f"Nao consegui chegar ate o {alvo}. {motivo_msg}"
        return f"Nao consegui chegar ate o {alvo}."

    if status == "error":
        error_msg = data.get("error", "erro desconhecido")
        return f"Erro ao tentar ir ate o alvo: {error_msg}"

    return f"Resultado do go_to: {result}"


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
