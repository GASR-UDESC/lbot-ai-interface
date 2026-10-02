import json


def build_initial_messages(system_prompt):
    return [{"role": "system", "content": system_prompt}]


def append_user_message(messages, content):
    messages.append({"role": "user", "content": content})
    return messages


def append_assistant_message(messages, content, tool_calls=None):
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls
    messages.append(message)
    return messages


def append_tool_result(messages, tool_call_id, tool_name, content):
    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": tool_name,
            "content": content,
        }
    )
    return messages


def inject_camera_image(messages, image_base64, metadata):
    messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Observação da câmera frontal (não é nova instrução): "
                    + json.dumps(metadata, ensure_ascii=False),
                },
                {
                    "type": "image_url",
                    "image_url": {"url": "data:image/png;base64," + image_base64},
                },
            ],
        }
    )
    return messages


def compact_history(messages, tools=None, max_bytes=14000):
    """Drop images and completed turns together; never orphan tool-call results."""
    camera_messages = [m for m in messages if isinstance(m.get("content"), list)]
    for message in camera_messages[:-2]:
        message["content"] = [p for p in message["content"] if p["type"] != "image_url"]

    def cost():
        # Conservative UTF-8 text estimate plus a reserve for each camera image.
        copy = []
        images = 0
        for m in messages:
            if isinstance(m.get("content"), list):
                images += sum(p["type"] == "image_url" for p in m["content"])
                copy.append(
                    {
                        **m,
                        "content": [
                            p for p in m["content"] if p["type"] != "image_url"
                        ],
                    }
                )
            else:
                copy.append(m)
        return (
            len(json.dumps(copy, ensure_ascii=False).encode())
            + images * 2400
            + len(json.dumps(tools or []).encode())
        )

    while cost() > max_bytes:
        # Keep initial system/goal and the entire most recent assistant/tool/image turn.
        starts = [
            i for i, m in enumerate(messages) if i >= 2 and m["role"] == "assistant"
        ]
        if len(starts) > 1:
            del messages[starts[0] : starts[1]]
        else:
            images = [
                m
                for m in messages
                if isinstance(m.get("content"), list)
                and any(p["type"] == "image_url" for p in m["content"])
            ]
            if len(images) > 1:
                images[0]["content"] = [
                    p for p in images[0]["content"] if p["type"] != "image_url"
                ]
            else:
                break
    if cost() > max_bytes:
        raise RuntimeError("context_budget_exceeded")
    return messages


def summarize_for_display(messages):
    return [
        {
            "role": m["role"],
            "content": "[imagem]"
            if isinstance(m.get("content"), list)
            else str(m.get("content", ""))[:200],
        }
        for m in messages
    ]
