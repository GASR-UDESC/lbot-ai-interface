import base64
import json
import logging
import os
import re
from typing import Any

from openai import OpenAI

from .mcp_client import MCPClient
from .personality import SYSTEM_PROMPT, get_tools_description

logger = logging.getLogger(__name__)

_BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]+=*$')


def _is_valid_base64(s: str) -> bool:
    if not s or len(s) < 100:
        return False
    try:
        decoded = base64.b64decode(s)
        return decoded[:4] == b'\x89PNG'
    except Exception:
        return False


def _strip_images(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    stripped = []
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, list):
            new_parts = []
            had_image = False
            for part in content:
                if isinstance(part, dict) and part.get("type") == "image_url":
                    had_image = True
                else:
                    new_parts.append(part)
            if had_image and new_parts:
                text_parts = [p for p in new_parts if isinstance(p, dict) and p.get("type") == "text"]
                combined = " ".join(p.get("text", "") for p in text_parts)
                stripped.append({**msg, "content": combined + " (imagem removida — modelo não suporta entrada de imagem)"})
            elif had_image:
                stripped.append({**msg, "content": "(imagem removida — modelo não suporta entrada de imagem)"})
            else:
                stripped.append(msg)
        else:
            stripped.append(msg)
    return stripped


class ReActAgent:
    def __init__(
        self,
        mcp_client: MCPClient,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        max_steps: int = 20,
        verbose: bool = False,
    ):
        self._mcp = mcp_client
        self._max_steps = max_steps
        self._verbose = verbose
        self._cancelled = False

        base_url = base_url or os.environ.get(
            "LBOT_LLM_URL", "http://127.0.0.1:1234/v1"
        )
        api_key = api_key or os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
        model = model or os.environ.get("LBOT_LLM_MODEL", "auto")

        self._llm = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._tools = get_tools_description()

    def cancel(self):
        self._cancelled = True

    async def run(self, goal: str, max_steps: int | None = None) -> str:
        max_steps = max_steps if max_steps is not None else self._max_steps
        self._cancelled = False

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": goal},
        ]

        step = 0
        while step < max_steps:
            if self._cancelled:
                return "Interrompido."

            step += 1

            try:
                response = self._llm.chat.completions.create(
                    model=self._model,
                    messages=messages,
                    tools=self._tools,
                    tool_choice="auto",
                )
            except Exception as e:
                error_msg = str(e)
                if "does not support image" in error_msg.lower() or "image input" in error_msg.lower():
                    logger.warning("Modelo não suporta imagem, removendo conteúdo de imagem e tentando novamente: %s", error_msg)
                    messages_no_image = self._strip_images(messages)
                    try:
                        response = self._llm.chat.completions.create(
                            model=self._model,
                            messages=messages_no_image,
                            tools=self._tools,
                            tool_choice="auto",
                        )
                    except Exception as e2:
                        logger.error("Erro ao chamar LLM (tentativa sem imagem): %s", e2)
                        return f"Erro ao processar sua solicitação: {e2}"
                else:
                    logger.error("Erro ao chamar LLM: %s", e)
                    return f"Erro ao processar sua solicitação: {e}"

            message = response.choices[0].message

            if self._verbose:
                logger.info(
                    "[Step %d] finish_reason=%s, tool_calls=%s, content=%s",
                    step,
                    response.choices[0].finish_reason,
                    bool(message.tool_calls),
                    message.content[:100] if message.content else None,
                )

            if message.content and not message.tool_calls:
                return message.content

            if message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments,
                            },
                        }
                        for tc in message.tool_calls
                    ],
                })

                for tc in message.tool_calls:
                    tool_name = tc.function.name
                    try:
                        raw_args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        raw_args = {}

                    logger.info("[Step %d] Chamando tool: %s(%s)", step, tool_name, raw_args)

                    try:
                        if tool_name == "move":
                            result = await self._mcp.call_tool(
                                "move", {"command": raw_args.get("command", "")}
                            )
                        else:
                            result = await self._mcp.call_tool(tool_name, raw_args)
                    except Exception as e:
                        result = f"Erro: {e}"
                        logger.warning("[Step %d] Tool error: %s", step, e)

                    if self._verbose:
                        logger.info("[Step %d] Tool result: %s", step, result[:200])

                    if tool_name == "camera":
                        camera_data = {}
                        try:
                            camera_data = json.loads(result)
                        except (json.JSONDecodeError, TypeError):
                            pass

                        image_base64 = ""
                        render_method = "unknown"
                        robot_position = None
                        camera_error = None

                        if isinstance(camera_data, dict):
                            image_base64 = camera_data.get("image", "")
                            render_method = camera_data.get("render_method", "unknown")
                            robot_position = camera_data.get("robot_position")
                            camera_error = camera_data.get("error")
                        elif isinstance(result, str) and _is_valid_base64(result):
                            image_base64 = result

                        if camera_error:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": f"Erro ao capturar imagem: {camera_error}",
                            })
                        elif _is_valid_base64(image_base64):
                            pos_text = ""
                            if robot_position:
                                pos_text = (
                                    f" Posição do robô: x={robot_position.get('x', 0):.1f}, "
                                    f"z={robot_position.get('z', 0):.1f}, "
                                    f"rotação={robot_position.get('rotation', 0):.1f}°."
                                )
                            render_desc = ""
                            if render_method == "2d":
                                render_desc = " A imagem é uma visão superior (mapa 2D) da arena — verde é o chão, marrom são paredes, azul é o robô."
                            elif render_method == "webgl":
                                render_desc = " A imagem é uma visão em primeira pessoa (3D) da câmera frontal do robô."

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Imagem capturada com sucesso.",
                            })

                            image_content: list[dict[str, Any]] = [
                                {"type": "text", "text": f"Aqui está a imagem da câmera frontal do robô:{render_desc}{pos_text}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                            ]

                            messages.append({
                                "role": "user",
                                "content": image_content,
                            })
                        else:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Erro: a imagem capturada não pôde ser processada (dados de imagem inválidos ou ausentes).",
                            })
                    else:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
            else:
                if message.content:
                    return message.content
                return "Não consegui processar sua solicitação."

        return (
            "Atingi o número máximo de passos sem concluir o objetivo. "
            "Tente reformular o pedido ou verificar se o ambiente está funcionando."
        )
