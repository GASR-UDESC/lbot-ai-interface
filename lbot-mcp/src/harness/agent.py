import json
import logging
import os
from typing import Any

from openai import OpenAI

from .mcp_client import MCPClient
from .personality import SYSTEM_PROMPT, get_tools_description

logger = logging.getLogger(__name__)


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
