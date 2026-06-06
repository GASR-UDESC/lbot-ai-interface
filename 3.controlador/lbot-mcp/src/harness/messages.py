from typing import Any


def build_initial_messages(system_prompt: str) -> list[dict[str, Any]]:
    return [{"role": "system", "content": system_prompt}]


def append_user_message(
    messages: list[dict[str, Any]], content: str
) -> list[dict[str, Any]]:
    messages.append({"role": "user", "content": content})
    return messages


def append_assistant_message(
    messages: list[dict[str, Any]],
    content: str,
    tool_calls: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    msg: dict[str, Any] = {"role": "assistant", "content": content}
    if tool_calls:
        msg["tool_calls"] = tool_calls
    messages.append(msg)
    return messages


def append_tool_result(
    messages: list[dict[str, Any]],
    tool_call_id: str,
    tool_name: str,
    content: str,
) -> list[dict[str, Any]]:
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call_id,
        "name": tool_name,
        "content": content,
    })
    return messages


def inject_camera_image(
    messages: list[dict[str, Any]],
    image_base64: str,
    render_method: str,
    robot_position: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    render_desc = ""
    if render_method == "2d":
        render_desc = (
            " A imagem é uma visão superior (mapa 2D) da arena — "
            "verde é o chão, marrom são paredes, azul é o robô."
        )
    elif render_method == "webgl":
        render_desc = (
            " A imagem é uma visão em primeira pessoa (3D) da "
            "câmera frontal do robô."
        )

    pos_text = ""
    if robot_position:
        pos_text = (
            f" Posição do robô: x={robot_position.get('x', 0):.1f}, "
            f"z={robot_position.get('z', 0):.1f}, "
            f"rotação={robot_position.get('rotation', 0):.1f}°."
        )

    messages.append({
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": (
                    f"Aqui está a imagem da câmera frontal do robô:"
                    f"{render_desc}{pos_text}"
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{image_base64}"
                },
            },
        ],
    })
    return messages


def summarize_for_display(
    messages: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    summarized: list[dict[str, Any]] = []
    for msg in messages:
        role = msg.get("role", "?")
        content = msg.get("content")
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        text = part.get("text", "")
                        if len(text) > 200:
                            text = text[:200] + "..."
                        parts.append(text)
                    elif part.get("type") == "image_url":
                        parts.append("[imagem]")
            summarized.append({
                "role": role,
                "content": " | ".join(parts) if parts else "(empty)",
            })
        elif isinstance(content, str):
            if len(content) > 200:
                content = content[:200] + "..."
            summarized.append({"role": role, "content": content})
        else:
            summarized.append({
                "role": role,
                "content": str(content)[:200],
            })
    return summarized
