import json
import logging
import os
from typing import Any, Callable

from openai import OpenAI

from .mcp_client import MCPClient
from .messages import (
    append_assistant_message,
    append_tool_result,
    append_user_message,
    build_initial_messages,
    inject_camera_image,
    summarize_for_display,
)
from .prompt import build_tools_for_llm, get_system_prompt
from .tool_handler import (
    handle_camera,
    handle_go_to,
    handle_move,
    handle_proximity,
    handle_search_object,
)

logger = logging.getLogger(__name__)

EventCallback = Callable[[str, dict[str, Any]], None] | None


class ReActAgent:
    def __init__(
        self,
        mcp_client: MCPClient,
        tools: list[dict],
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        max_steps: int = 50,
        verbose: bool = False,
        on_event: EventCallback = None,
    ):
        self._mcp = mcp_client
        self._tools = tools
        self._max_steps = max_steps
        self._verbose = verbose
        self._on_event = on_event
        base_url = base_url or os.environ.get("LBOT_LLM_URL", "http://127.0.0.1:1234/v1")
        api_key = api_key or os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
        model = model or os.environ.get("LBOT_LLM_MODEL", "auto")
        self._llm = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._messages = build_initial_messages(get_system_prompt())
        self._cancelled = False

    @classmethod
    async def create(
        cls,
        mcp_client: MCPClient,
        **kwargs,
    ) -> "ReActAgent":
        raw_tools = await mcp_client.list_tools()
        tools = build_tools_for_llm(raw_tools)
        return cls(mcp_client, tools=tools, **kwargs)

    def _emit(self, event: str, data: dict[str, Any]) -> None:
        if self._on_event is not None:
            try:
                self._on_event(event, data)
            except Exception:
                pass

    def cancel(self) -> None:
        self._cancelled = True

    def reset(self) -> None:
        self._messages = build_initial_messages(get_system_prompt())
        self._cancelled = False

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._messages)

    async def run(self, goal: str, max_steps: int | None = None) -> str:
        steps = max_steps if max_steps is not None else self._max_steps
        self._cancelled = False
        self._messages = build_initial_messages(get_system_prompt())
        append_user_message(self._messages, goal)
        self._emit("goal", {"goal": goal})

        for step in range(1, steps + 1):
            if self._cancelled:
                self._emit("cancelled", {})
                return "Interrompido."
            self._emit("llm_request", {
                "step": step,
                "messages": summarize_for_display(self._messages),
            })
            try:
                response = self._llm.chat.completions.create(
                    model=self._model, messages=self._messages,
                    tools=self._tools, tool_choice="auto",
                )
            except Exception as e:
                logger.error("Erro ao chamar LLM: %s", e)
                self._emit("error", {"step": step, "error": str(e)})
                return f"Erro ao processar sua solicitação: {e}"

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            tool_calls_raw = message.tool_calls or []

            self._emit("llm_response", {
                "step": step, "finish_reason": finish_reason,
                "content": message.content,
                "tool_calls": [
                    {"id": tc.id, "name": tc.function.name,
                     "arguments": tc.function.arguments}
                    for tc in tool_calls_raw
                ],
            })

            if self._verbose:
                logger.info(
                    "[Step %d] finish_reason=%s, tool_calls=%s, content=%s",
                    step, finish_reason, bool(tool_calls_raw),
                    message.content[:100] if message.content else None,
                )

            if message.content and not tool_calls_raw:
                self._messages = append_assistant_message(self._messages, message.content)
                self._emit("final_answer", {"step": step, "content": message.content})
                return message.content

            if tool_calls_raw:
                self._messages = append_assistant_message(
                    self._messages, message.content,
                    [{
                        "id": tc.id, "type": "function",
                        "function": {"name": tc.function.name,
                                     "arguments": tc.function.arguments},
                    } for tc in tool_calls_raw],
                )
                for tc in tool_calls_raw:
                    tool_name = tc.function.name
                    try:
                        args = json.loads(tc.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    self._emit("tool_call", {
                        "step": step, "tool": tool_name, "arguments": args,
                    })
                    try:
                        if tool_name == "camera":
                            camera_data = await handle_camera(self._mcp)
                            if camera_data.get("image"):
                                append_tool_result(self._messages, tc.id, tool_name,
                                                   "Câmera capturada com sucesso.")
                                inject_camera_image(
                                    self._messages, camera_data["image"],
                                    camera_data.get("render_method", "unknown"),
                                    camera_data.get("robot_position"),
                                )
                                display = "[imagem]"
                            else:
                                append_tool_result(self._messages, tc.id, tool_name,
                                                   "Erro ao capturar imagem: dados inválidos.")
                                display = "Erro ao capturar imagem"
                        elif tool_name == "proximity":
                            result = await handle_proximity(self._mcp)
                            append_tool_result(self._messages, tc.id, tool_name, result)
                            display = result
                        elif tool_name == "move":
                            command = args.get("command", "")
                            result = await handle_move(self._mcp, command)
                            append_tool_result(self._messages, tc.id, tool_name, result)
                            display = result
                        elif tool_name == "go_to":
                            result = await handle_go_to(
                                self._mcp,
                                args.get("target", ""),
                                args.get("direction", "frente"),
                            )
                            append_tool_result(self._messages, tc.id, tool_name, result)
                            display = result
                        elif tool_name == "search_object":
                            result = await handle_search_object(
                                self._mcp, args.get("description", "")
                            )
                            append_tool_result(self._messages, tc.id, tool_name, result)
                            display = result
                        else:
                            result = await self._mcp.call_tool(tool_name, args)
                            append_tool_result(self._messages, tc.id, tool_name, result)
                            display = result
                    except Exception as e:
                        error_result = f"Erro: {e}"
                        logger.warning("[Step %d] Tool error: %s", step, e)
                        append_tool_result(self._messages, tc.id, tool_name, error_result)
                        display = error_result
                    display_str = display if isinstance(display, str) else str(display)
                    if len(display_str) > 200:
                        display_str = display_str[:200] + "..."
                    self._emit("tool_result", {
                        "step": step, "tool": tool_name, "result": display_str,
                    })
            else:
                if message.content:
                    self._messages = append_assistant_message(
                        self._messages, message.content,
                    )
                    self._emit(
                        "final_answer", {"step": step, "content": message.content},
                    )
                    return message.content
                return "Não consegui processar sua solicitação."

        self._emit("max_steps_reached", {"max_steps": steps})
        return (
            f"Não consegui completar a tarefa após {steps} passos. "
            "Tente reformular o pedido ou verificar se o ambiente está funcionando."
        )
