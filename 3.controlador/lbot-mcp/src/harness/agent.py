import asyncio
import base64
import json
import os
import time
import uuid
from pathlib import Path

import cv2
import numpy as np
from jsonschema import Draft202012Validator

from mcp_server.services.inference import InferenceClient, get_inference

from .messages import (
    append_assistant_message,
    append_tool_result,
    append_user_message,
    build_initial_messages,
    compact_history,
    inject_camera_image,
)
from .prompt import build_tools_for_llm, get_system_prompt
from .tool_handler import result_for_display, result_for_model


class ReActAgent:
    def __init__(
        self,
        mcp_client,
        tools,
        base_url=None,
        api_key=None,
        model=None,
        max_steps=24,
        verbose=False,
        on_event=None,
        inference=None,
    ):
        self._mcp = mcp_client
        self._tools = tools
        self._max_steps = max_steps
        self._on_event = on_event
        self._llm = inference or (
            InferenceClient(base_url, model) if base_url or model else get_inference()
        )
        self._messages = build_initial_messages(get_system_prompt())
        self._task = None
        self._cancelled = False
        self._schemas = {
            t["function"]["name"]: t["function"]["parameters"] for t in tools
        }
        self._compatible = False
        self.metrics = {}
        self.trace = []
        self.episode_id = None

    @classmethod
    async def create(cls, mcp_client, check_runtime=True, **kwargs):
        agent = cls(
            mcp_client, build_tools_for_llm(await mcp_client.list_tools()), **kwargs
        )
        if check_runtime:
            await agent.check_runtime()
        return agent

    async def check_runtime(self):
        """Only dummy tools: this compatibility check cannot move the robot."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "runtime_probe",
                    "description": "Confirma a compatibilidade do servidor.",
                    "parameters": {"type": "object", "properties": {}},
                },
            }
        ]
        messages = [{"role": "user", "content": "Chame runtime_probe agora."}]
        response = await self._llm.complete(
            messages=messages, tools=tools, tool_choice="auto"
        )
        message = response.choices[0].message
        if getattr(message, "reasoning_content", ""):
            raise RuntimeError("runtime_reasoning_not_disabled")
        if (
            not message.tool_calls
            or len(message.tool_calls) != 1
            or message.tool_calls[0].function.name != "runtime_probe"
        ):
            raise RuntimeError("runtime_tool_call_incompatible")
        tc = message.tool_calls[0]
        json.loads(tc.function.arguments)
        messages += [
            message.model_dump(exclude_none=True),
            {
                "role": "tool",
                "tool_call_id": tc.id,
                "content": '{"status":"completed","probe":"ok"}',
            },
        ]
        response = await self._llm.complete(messages=messages)
        if not response.choices[0].message.content:
            raise RuntimeError("runtime_continuation_incompatible")
        image = np.zeros((128, 128, 3), np.uint8)
        image[:] = (0, 0, 255)
        _, png = cv2.imencode(".png", image)
        response = await self._llm.complete(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Qual a cor da imagem? Responda uma palavra em português.",
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "data:image/png;base64,"
                                + base64.b64encode(png).decode()
                            },
                        },
                    ],
                }
            ]
        )
        if "vermelh" not in (response.choices[0].message.content or "").lower():
            raise RuntimeError("runtime_vision_incompatible")
        self._compatible = True
        self._emit("runtime_check", {"passed": True, "model": self._llm.model})

    def _emit(self, event, data):
        self.trace.append(
            {"event": event, "at": time.time(), "episode_id": self.episode_id, **data}
        )
        if self._on_event:
            try:
                self._on_event(event, data)
            except Exception:
                pass

    def cancel(self):
        self._cancelled = True
        if self._task and not self._task.done():
            self._task.cancel()

    def reset(self):
        self._messages = build_initial_messages(get_system_prompt())

    @property
    def history(self):
        return list(self._messages)

    async def run(self, goal, max_steps=None):
        if self._task and not self._task.done():
            return "Já estou executando uma tarefa."
        if not self._compatible:
            await self.check_runtime()
        self.trace = []
        self.episode_id = str(uuid.uuid4())
        self.metrics = {
            "llm_calls": 0,
            "tool_calls": 0,
            "invalid_calls": 0,
            "completed_operations": 0,
        }
        self._cancelled = False
        start = time.monotonic()
        self._task = asyncio.create_task(self._run(goal, max_steps or self._max_steps))
        try:
            return await asyncio.wait_for(
                self._task, float(os.getenv("LBOT_EPISODE_TIMEOUT", "300"))
            )
        except asyncio.CancelledError:
            result = await self._stop()
            self._emit("cancelled", {"stop_result": result})
            return "Interrompido. " + (
                "Parada confirmada."
                if result.get("status") == "completed"
                else "Não consegui confirmar a parada."
            )
        except asyncio.TimeoutError:
            result = await self._stop()
            self._emit("error", {"reason": "episode_timeout", "stop_result": result})
            return "Tempo da tarefa esgotado. " + (
                "Parada confirmada."
                if result.get("status") == "completed"
                else "Parada não confirmada."
            )
        except Exception as e:
            result = await self._stop()
            self._emit("error", {"reason": str(e), "stop_result": result})
            return f"Falha na tarefa: {e}"
        finally:
            self.metrics["elapsed_seconds"] = time.monotonic() - start
            self._emit("episode_summary", self.metrics)
            directory = Path(
                os.getenv(
                    "LBOT_TRACE_DIR", str(Path(__file__).resolve().parents[2] / "runs")
                )
            )
            directory.mkdir(parents=True, exist_ok=True)
            (directory / (self.episode_id + ".jsonl")).write_text(
                "\n".join(
                    json.dumps(x, ensure_ascii=False, default=str) for x in self.trace
                )
                + "\n"
            )
            self._task = None

    async def _stop(self):
        try:
            return await asyncio.wait_for(self._mcp.call_tool("stop", {}), 10)
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def _run(self, goal, steps):
        self._messages = build_initial_messages(get_system_prompt())
        append_user_message(self._messages, goal)
        self._emit("goal", {"goal": goal})
        repeats = {}
        corrections = 0
        evidence = []
        for step in range(1, steps + 1):
            compact_history(self._messages, self._tools)
            start = time.monotonic()
            response = await self._llm.complete(
                messages=self._messages, tools=self._tools, tool_choice="auto"
            )
            self.metrics["llm_calls"] += 1
            message = response.choices[0].message
            calls = message.tool_calls or []
            self._emit(
                "llm_response",
                {
                    "step": step,
                    "seconds": time.monotonic() - start,
                    "content": message.content,
                    "tool_calls": [tc.model_dump() for tc in calls],
                    "usage": response.usage.model_dump() if response.usage else None,
                },
            )
            if not calls:
                content = message.content or "Não consegui decidir uma ação."
                if (
                    "<tool_call" in content
                    or response.choices[0].finish_reason == "length"
                ):
                    if corrections >= 1:
                        return "Resposta do modelo inválida; nenhuma ação foi executada a partir desse texto."
                    corrections += 1
                    append_assistant_message(self._messages, content)
                    append_user_message(
                        self._messages,
                        "Use o protocolo de ferramentas válido; não escreva chamadas em texto.",
                    )
                    continue
                self._emit(
                    "final_answer", {"content": content, "execution_results": evidence}
                )
                return content
            append_assistant_message(
                self._messages, message.content, [tc.model_dump() for tc in calls]
            )
            images = []
            blocked = False
            failure_reason = None
            owns_motion = False
            for tc in calls:
                name = tc.function.name
                try:
                    args = json.loads(tc.function.arguments)
                    if name not in self._schemas:
                        raise ValueError("unknown_tool")
                    Draft202012Validator(self._schemas[name]).validate(args)
                except Exception as e:
                    self.metrics["invalid_calls"] += 1
                    corrections += 1
                    result = {
                        "status": "failed",
                        "reason": "invalid_arguments",
                        "detail": str(e)[:200],
                    }
                    args = {}
                else:
                    key = name + json.dumps(args, sort_keys=True)
                    if blocked and name != "stop":
                        result = {
                            "status": "cancelled",
                            "reason": "previous_call_failed",
                        }
                    elif repeats.get(key, 0) >= 3:
                        result = {"status": "failed", "reason": "no_progress"}
                    else:
                        self._emit("tool_call", {"tool": name, "arguments": args})
                        t = time.monotonic()
                        result = await self._mcp.call_tool(name, args)
                        self.metrics["tool_calls"] += 1
                        if name in ("move", "approach", "search_object") and result.get(
                            "reason"
                        ) not in {"busy", "stale_session"}:
                            owns_motion = True
                        # Count repetitions only when observations/outcomes have not progressed.
                        fingerprint = json.dumps(
                            {
                                k: result.get(k)
                                for k in (
                                    "status",
                                    "reason",
                                    "detected",
                                    "approached",
                                    "readings",
                                    "distance_cm",
                                )
                            },
                            sort_keys=True,
                        )
                        previous = repeats.get(key + "_result")
                        repeats[key] = (
                            repeats.get(key, 0) + 1 if previous == fingerprint else 1
                        )
                        repeats[key + "_result"] = fingerprint
                        self._emit(
                            "tool_timing",
                            {"tool": name, "seconds": time.monotonic() - t},
                        )
                safe = result_for_model(result)
                for field in ("commands", "steps"):
                    if field in safe:
                        safe[field + "_count"] = len(safe[field])
                        safe[field] = safe[field][-3:]
                append_tool_result(
                    self._messages, tc.id, name, json.dumps(safe, ensure_ascii=False)
                )
                if result.get("image"):
                    images.append(
                        (
                            result["image"],
                            {
                                k: result[k]
                                for k in (
                                    "frame_id",
                                    "session_id",
                                    "revision",
                                    "captured_at",
                                    "intrinsics",
                                )
                                if k in result
                            },
                        )
                    )
                if name in ("move", "approach", "search_object", "stop"):
                    evidence.append({"tool": name, **safe})
                    self.metrics["completed_operations"] += (
                        result.get("status") == "completed"
                    )
                self._emit(
                    "tool_result",
                    {
                        "tool": name,
                        "result": result_for_display(result),
                        "structured": safe,
                    },
                )
                failed = (
                    (
                        result.get("status") == "failed"
                        and result.get("reason") != "invalid_arguments"
                    )
                    or result.get("status") in ("blocked", "cancelled", "timed_out")
                    or result.get("reason") in ("execution_unknown", "no_progress")
                )
                if failed and not blocked:
                    failure_reason = result.get("reason", "erro operacional")
                blocked |= failed
            # All tool responses must precede multimodal user messages.
            for image, metadata in images:
                inject_camera_image(self._messages, image, metadata)
            if blocked or corrections > 1:
                if owns_motion and failure_reason not in {"busy", "stale_session"}:
                    await self._stop()
                return "Execução interrompida: " + str(
                    failure_reason or "argumentos inválidos"
                )
        await self._stop()
        return "Limite de decisões atingido; execução interrompida."
