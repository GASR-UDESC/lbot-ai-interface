import base64
import json
import logging
import os
import re
from typing import Any, Callable

from openai import OpenAI

from .mcp_client import MCPClient
from .personality import SYSTEM_PROMPT, get_tools_description

logger = logging.getLogger(__name__)

_BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]+=*$')

_MAX_CONTEXT_TOKENS = int(os.environ.get("LBOT_MAX_CONTEXT_TOKENS", "4000"))
_APPROX_CHARS_PER_TOKEN = 4

EventCallback = Callable[[str, dict[str, Any]], None] | None

# ---------------------------------------------------------------------------
# LBML helpers — parsing, inspection, modification
# ---------------------------------------------------------------------------

_LBML_CMD_RE = re.compile(r"([DR])(\d+)([FBLR]);")


def _parse_lbml_command(command_str: str) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for match in _LBML_CMD_RE.finditer(command_str):
        commands.append({
            "type": match.group(1),
            "value": int(match.group(2)),
            "direction": match.group(3),
        })
    return commands


def _is_forward_command(parsed: list[dict[str, Any]]) -> bool:
    return any(c["type"] == "D" and c["direction"] == "F" for c in parsed)


def _is_rotation_command(parsed: list[dict[str, Any]]) -> bool:
    if not parsed:
        return False
    return all(c["type"] == "R" for c in parsed)


def _reduce_step(parsed: list[dict[str, Any]], max_distance: int) -> list[dict[str, Any]]:
    result = []
    for cmd in parsed:
        copy = dict(cmd)
        if cmd["type"] == "D" and cmd["direction"] == "F" and cmd["value"] > max_distance:
            copy["value"] = max_distance
        result.append(copy)
    return result


def _parsed_to_lbml(parsed: list[dict[str, Any]]) -> str:
    return "".join(f"{c['type']}{c['value']}{c['direction']};" for c in parsed)


_PROXIMITY_TEXT_RE = re.compile(
    r"Frente:\s*([\d.]+)\s*cm.*?Tr[áa]s:\s*([\d.]+)\s*cm",
    re.IGNORECASE | re.DOTALL,
)


def _extract_proximity_from_messages(messages: list[dict[str, Any]]) -> dict[str, float] | None:
    for msg in reversed(messages):
        content = msg.get("content", "")

        if isinstance(content, str):
            m = _PROXIMITY_TEXT_RE.search(content)
            if m:
                return {"frente": float(m.group(1)), "tras": float(m.group(2))}

            try:
                data = json.loads(content)
                if isinstance(data, dict):
                    proximity = data.get("proximity")
                    if isinstance(proximity, dict):
                        frente = proximity.get("frente")
                        tras = proximity.get("tras")
                        if frente is not None and tras is not None:
                            return {"frente": float(frente), "tras": float(tras)}
            except (json.JSONDecodeError, TypeError):
                pass

        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict) and part.get("type") == "text":
                    text = part.get("text", "")
                    m = _PROXIMITY_TEXT_RE.search(text)
                    if m:
                        return {"frente": float(m.group(1)), "tras": float(m.group(2))}
    return None


def _summarize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return a copy of messages with base64 images truncated for display."""
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
                        url = part.get("image_url", {}).get("url", "")
                        if url.startswith("data:image"):
                            parts.append("[imagem]")
                        else:
                            parts.append(url[:80])
            summarized.append({"role": role, "content": " | ".join(parts) if parts else "(empty)"})
        elif isinstance(content, str):
            if len(content) > 200:
                content = content[:200] + "..."
            summarized.append({"role": role, "content": content})
        else:
            summarized.append({"role": role, "content": str(content)[:200]})
    return summarized


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


def _estimate_tokens(messages: list[dict[str, Any]]) -> int:
    total = 0
    for msg in messages:
        content = msg.get("content")
        if isinstance(content, str):
            total += len(content) // _APPROX_CHARS_PER_TOKEN
        elif isinstance(content, list):
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        total += len(part.get("text", "")) // _APPROX_CHARS_PER_TOKEN
                    elif part.get("type") == "image_url":
                        total += 500
        if msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                fn = tc.get("function", {})
                total += len(fn.get("name", "")) // _APPROX_CHARS_PER_TOKEN
                total += len(fn.get("arguments", "")) // _APPROX_CHARS_PER_TOKEN
    return total


def _collect_tool_call_ids(messages: list[dict[str, Any]]) -> set[str]:
    ids = set()
    for msg in messages:
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            for tc in msg["tool_calls"]:
                tc_id = tc.get("id")
                if tc_id:
                    ids.add(tc_id)
    return ids


def _trim_messages(messages: list[dict[str, Any]], max_tokens: int) -> list[dict[str, Any]]:
    if not messages:
        return messages
    if messages[0].get("role") == "system":
        system_msg = messages[0]
        rest = messages[1:]
    else:
        system_msg = None
        rest = list(messages)

    while rest and _estimate_tokens([system_msg] + rest if system_msg else rest) > max_tokens:
        cut = 1
        while cut < len(rest):
            r = rest[cut]
            if r.get("role") == "user" and not isinstance(r.get("content"), list):
                break
            if r.get("role") == "user" and isinstance(r.get("content"), list):
                break
            cut += 1
            if cut >= len(rest):
                break
        if cut >= len(rest):
            break
        rest = rest[cut:]

    if system_msg:
        rest = [system_msg] + rest

    return _sanitize_messages(rest)


def _sanitize_messages(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not messages:
        return messages

    result: list[dict[str, Any]] = []
    valid_tool_call_ids = _collect_tool_call_ids(messages)

    for msg in messages:
        role = msg.get("role")

        if role == "system":
            if not any(m.get("role") == "system" for m in result):
                result.append(msg)
            continue

        if role == "tool":
            tc_id = msg.get("tool_call_id", "")
            if tc_id not in valid_tool_call_ids:
                continue

            has_matching_assistant = False
            for prev in reversed(result):
                if prev.get("role") == "assistant" and prev.get("tool_calls"):
                    for tc in prev["tool_calls"]:
                        if tc.get("id") == tc_id:
                            has_matching_assistant = True
                            break
                    break
                if prev.get("role") in ("user", "system", "assistant"):
                    break
            if not has_matching_assistant:
                continue

        if role == "user" and isinstance(msg.get("content"), list):
            has_camera_context = False
            for prev in reversed(result):
                if prev.get("role") == "tool" and "imagem" in prev.get("content", ""):
                    has_camera_context = True
                    break
                if prev.get("role") in ("user", "system"):
                    break
            if not has_camera_context:
                text_parts = []
                for part in msg["content"]:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part.get("text", ""))
                    elif isinstance(part, dict) and part.get("type") == "image_url":
                        text_parts.append("[imagem da câmera]")
                if text_parts:
                    msg = {"role": "user", "content": " ".join(text_parts)}

        if role == "assistant" and result and result[-1].get("role") == "assistant":
            prev_had_calls = bool(result[-1].get("tool_calls"))
            curr_has_calls = bool(msg.get("tool_calls"))
            if prev_had_calls and not curr_has_calls:
                result.pop()
            elif not prev_had_calls and not curr_has_calls:
                continue

        result.append(msg)

    has_user = any(m.get("role") == "user" for m in result)
    if not has_user:
        result.append({"role": "user", "content": "Continuando a conversa."})

    return result


class ReActAgent:
    def __init__(
        self,
        mcp_client: MCPClient,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        max_steps: int = 50,
        verbose: bool = False,
        on_event: EventCallback = None,
    ):
        self._mcp = mcp_client
        self._max_steps = max_steps
        self._verbose = verbose
        self._cancelled = False
        self._on_event = on_event
        self._messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
        ]

        base_url = base_url or os.environ.get(
            "LBOT_LLM_URL", "http://127.0.0.1:1234/v1"
        )
        api_key = api_key or os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
        model = model or os.environ.get("LBOT_LLM_MODEL", "auto")

        self._llm = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._tools = get_tools_description()

        self._last_front_proximity: float | None = None
        self._last_back_proximity: float | None = None
        self._last_position: dict | None = None
        self._consecutive_rotations: int = 0
        self._object_was_centered: bool = False
        self._goal_achieved: bool = False

    def _emit(self, event: str, data: dict[str, Any]) -> None:
        if self._on_event is not None:
            try:
                self._on_event(event, data)
            except Exception:
                pass

    def cancel(self):
        self._cancelled = True

    def reset(self):
        self._messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        self._last_front_proximity = None
        self._last_back_proximity = None
        self._last_position = None
        self._consecutive_rotations = 0
        self._object_was_centered = False
        self._goal_achieved = False

    def _validate_and_adjust_move(self, command: str) -> tuple[str | None, str | None]:
        proximity = _extract_proximity_from_messages(self._messages)
        if proximity is None:
            return (command, None)

        parsed = _parse_lbml_command(command)
        if not parsed:
            return (command, None)

        frente = proximity["frente"]

        if frente <= 20 and _is_forward_command(parsed):
            return (
                None,
                f"Bloqueado: distancia frontal e de {frente:.0f}cm, "
                "ja esta dentro da faixa de aproximacao (15-25cm). Objetivo alcancado.",
            )

        if not _is_forward_command(parsed):
            return (command, None)

        original_command = command
        if 20 < frente <= 40:
            reduced = _reduce_step(parsed, 10)
            new_command = _parsed_to_lbml(reduced)
            if new_command != original_command:
                return (
                    new_command,
                    f"Comando ajustado: {original_command} reduzido para {new_command} "
                    "(proximo ao alvo, passo reduzido por seguranca)",
                )
        elif 40 < frente <= 80:
            reduced = _reduce_step(parsed, 15)
            new_command = _parsed_to_lbml(reduced)
            if new_command != original_command:
                return (
                    new_command,
                    f"Comando ajustado: {original_command} reduzido para {new_command} "
                    "(proximo ao alvo, passo reduzido por seguranca)",
                )

        return (command, None)

    def _detect_object_loss(self, current_front: float, previous_front: float | None) -> str | None:
        if previous_front is None:
            return None

        if previous_front <= 25 and current_front > 30:
            self._object_was_centered = False
            self._consecutive_rotations = 0
            return (
                f"**[CONTROLE AUTOMATICO]** ALERTA DE PERDA DE OBJETO: "
                f"A distancia frontal saltou de {previous_front:.0f}cm para {current_front:.0f}cm "
                f"(aumento > 5cm a partir da zona de aproximacao). "
                f"Voce pode ter passado do objeto ou ele saiu do seu campo de visao. "
                f"Protocolo de recuperacao: (1) Recue 20cm com D20B; "
                f"(2) Faca observe() para re-localizar o objeto; "
                f"(3) Se encontrado, centralize e retome a aproximacao com passos de no maximo 10cm; "
                f"(4) Se nao encontrado apos 360 graus de busca, informe que o objeto foi perdido."
            )
        return None

    def _check_proximity_goal(self) -> str | None:
        proximity = _extract_proximity_from_messages(self._messages)
        if proximity is None:
            return None

        frente = proximity["frente"]

        previous_front = self._last_front_proximity
        loss_msg = self._detect_object_loss(frente, previous_front)

        self._last_front_proximity = frente
        self._last_back_proximity = proximity["tras"]

        if loss_msg:
            return loss_msg

        if 15 <= frente <= 25:
            self._goal_achieved = True
            return (
                f"**[CONTROLE AUTOMATICO]** Proximidade frontal: {frente:.0f}cm "
                f"(faixa alvo: 15-25cm). Voce chegou perto o suficiente do objeto. "
                f"Declare sucesso e informe o usuario que o objetivo foi alcancado."
            )
        elif frente < 15:
            if self._object_was_centered:
                self._object_was_centered = False
                self._consecutive_rotations = 0
                return (
                    f"**[CONTROLE AUTOMATICO]** ALERTA DE PERDA DE OBJETO: "
                    f"Proximidade frontal {frente:.0f}cm — voce passou do alvo "
                    f"(overshooting). Protocolo de recuperacao: (1) Recue 20cm "
                    f"com D20B; (2) Faca observe() para re-localizar o objeto; "
                    f"(3) Se encontrado, centralize e retome a aproximacao com "
                    f"passos de no maximo 10cm; (4) Se nao encontrado apos "
                    f"360 graus de busca, informe que o objeto foi perdido."
                )
            else:
                return (
                    f"Cuidado: muito perto de um obstaculo ({frente:.0f}cm). "
                    f"Recue um pouco e tente centralizar o alvo na camera."
                )
        return None

    def _check_rotation_loop(self, command: str, parsed: list[dict]) -> str | None:
        if not parsed:
            return None

        if _is_rotation_command(parsed):
            self._consecutive_rotations += 1
        else:
            self._consecutive_rotations = 0

        if self._consecutive_rotations >= 10:
            self._consecutive_rotations = 0
            return (
                "**[CONTROLE AUTOMATICO]** Voce executou 10 rotacoes consecutivas sem "
                "mudanca significativa de posicao. Voce pode estar em um loop de rotacao. "
                "Tente uma estrategia diferente: recue 20cm, faca um observe(), ou gire "
                "em angulos maiores (ex: 30-45 graus)."
            )
        return None

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._messages)

    @property
    def history_summary(self) -> str:
        lines = []
        for i, msg in enumerate(self._messages):
            role = msg.get("role", "?")
            content = msg.get("content", "")
            if isinstance(content, list):
                parts = []
                for part in content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            parts.append(part.get("text", "")[:80])
                        elif part.get("type") == "image_url":
                            parts.append("[imagem]")
                content = " | ".join(parts)
            elif isinstance(content, str):
                content = content[:80]
            else:
                content = str(content)[:80]

            if role == "tool":
                name = msg.get("name", "")
                lines.append(f"  [{i}] tool({name}): {content}")
            elif role == "assistant":
                tc = msg.get("tool_calls")
                if tc:
                    names = [t.get("function", {}).get("name", "?") for t in tc]
                    lines.append(f"  [{i}] assistant → chamou {', '.join(names)}")
                else:
                    lines.append(f"  [{i}] assistant: {content}")
            else:
                lines.append(f"  [{i}] {role}: {content}")
        return "\n".join(lines)

    async def run(self, goal: str, max_steps: int | None = None) -> str:
        max_steps = max_steps if max_steps is not None else self._max_steps
        self._cancelled = False

        self._last_front_proximity = None
        self._last_back_proximity = None
        self._last_position = None
        self._consecutive_rotations = 0
        self._object_was_centered = False
        self._goal_achieved = False

        self._messages.append({"role": "user", "content": goal})
        self._messages = _trim_messages(self._messages, _MAX_CONTEXT_TOKENS)

        self._emit("goal", {"goal": goal})

        step = 0
        while step < max_steps:
            if self._cancelled:
                self._emit("cancelled", {})
                return "Interrompido."

            step += 1
            messages = self._messages

            self._emit(
                "llm_request",
                {"step": step, "messages": _summarize_messages(messages)},
            )

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
                    messages_no_image = _strip_images(messages)
                    self._emit(
                        "llm_request_retry",
                        {"step": step, "reason": "modelo não suporta imagem"},
                    )
                    try:
                        response = self._llm.chat.completions.create(
                            model=self._model,
                            messages=messages_no_image,
                            tools=self._tools,
                            tool_choice="auto",
                        )
                    except Exception as e2:
                        logger.error("Erro ao chamar LLM (tentativa sem imagem): %s", e2)
                        self._emit("error", {"step": step, "error": str(e2)})
                        return f"Erro ao processar sua solicitação: {e2}"
                else:
                    logger.error("Erro ao chamar LLM: %s", e)
                    self._emit("error", {"step": step, "error": str(e)})
                    return f"Erro ao processar sua solicitação: {e}"

            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            if message.content and not self._object_was_centered:
                centered_keywords = [
                    "centralizado", "centralizei", "no centro",
                    "esta centralizado", "objeto esta no centro",
                ]
                content_lower = message.content.lower()
                if any(kw in content_lower for kw in centered_keywords):
                    self._object_was_centered = True

            self._emit(
                "llm_response",
                {
                    "step": step,
                    "finish_reason": finish_reason,
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                        for tc in (message.tool_calls or [])
                    ],
                },
            )

            if self._verbose:
                logger.info(
                    "[Step %d] finish_reason=%s, tool_calls=%s, content=%s",
                    step,
                    finish_reason,
                    bool(message.tool_calls),
                    message.content[:100] if message.content else None,
                )

            if message.content and not message.tool_calls:
                self._messages.append({"role": "assistant", "content": message.content})
                self._emit("final_answer", {"step": step, "content": message.content})
                return message.content

            if message.tool_calls:
                self._messages.append({
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

                    self._emit(
                        "tool_call",
                        {"step": step, "tool": tool_name, "arguments": raw_args},
                    )
                    logger.info("[Step %d] Chamando tool: %s(%s)", step, tool_name, raw_args)

                    try:
                        if tool_name == "move":
                            command = raw_args.get("command", "")
                            parsed = _parse_lbml_command(command)

                            loop_msg = self._check_rotation_loop(command, parsed)
                            if loop_msg:
                                self._messages.append({"role": "user", "content": loop_msg})

                            adjusted_command, info_msg = self._validate_and_adjust_move(command)
                            if adjusted_command is None:
                                result = info_msg or "Comando bloqueado."
                            else:
                                result = await self._mcp.call_tool(
                                    "move", {"command": adjusted_command}
                                )
                                if info_msg:
                                    result = info_msg + "\n" + result
                        else:
                            result = await self._mcp.call_tool(tool_name, raw_args)
                    except Exception as e:
                        result = f"Erro: {e}"
                        logger.warning("[Step %d] Tool error: %s", step, e)

                    display_result = result
                    if isinstance(result, str) and len(result) > 200:
                        display_result = result[:200] + "..."

                    self._emit(
                        "tool_result",
                        {
                            "step": step,
                            "tool": tool_name,
                            "result": display_result,
                        },
                    )

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
                            if robot_position:
                                self._last_position = robot_position
                        elif isinstance(result, str) and _is_valid_base64(result):
                            image_base64 = result

                        if camera_error:
                            self._messages.append({
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

                            self._messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Imagem capturada com sucesso.",
                            })

                            image_content: list[dict[str, Any]] = [
                                {"type": "text", "text": f"Aqui está a imagem da câmera frontal do robô:{render_desc}{pos_text}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                            ]

                            self._messages.append({
                                "role": "user",
                                "content": image_content,
                            })
                        else:
                            self._messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Erro: a imagem capturada não pôde ser processada (dados de imagem inválidos ou ausentes).",
                            })
                    elif tool_name == "observe":
                        observe_data = {}
                        try:
                            observe_data = json.loads(result)
                        except (json.JSONDecodeError, TypeError):
                            pass

                        if isinstance(observe_data, dict):
                            camera_error = observe_data.get("camera_error")
                            prox_error = observe_data.get("proximity_error")
                            image_base64 = observe_data.get("image", "")
                            proximity = observe_data.get("proximity")
                            render_method = observe_data.get("render_method", "unknown")
                            robot_position = observe_data.get("robot_position")
                            if robot_position:
                                self._last_position = robot_position

                            parts: list[str] = []

                            if camera_error and prox_error:
                                self._messages.append({
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "content": f"Erro no observe: câmera indisponível ({camera_error}), proximidade indisponível ({prox_error})",
                                })
                            elif camera_error:
                                parts.append(f"Erro ao capturar imagem: {camera_error}")

                                if proximity:
                                    frente = proximity.get("frente", "N/A")
                                    tras = proximity.get("tras", "N/A")
                                    parts.append(f"Proximidade — Frente: {frente} cm | Trás: {tras} cm")
                                elif prox_error:
                                    parts.append(f"Proximidade indisponível: {prox_error}")

                                self._messages.append({
                                    "role": "tool",
                                    "tool_call_id": tc.id,
                                    "content": " | ".join(parts),
                                })
                            elif prox_error:
                                if _is_valid_base64(image_base64):
                                    render_desc = ""
                                    if render_method == "2d":
                                        render_desc = " A imagem é uma visão superior (mapa 2D) da arena — verde é o chão, marrom são paredes, azul é o robô."
                                    elif render_method == "webgl":
                                        render_desc = " A imagem é uma visão em primeira pessoa (3D) da câmera frontal do robô."

                                    pos_text = ""
                                    if robot_position:
                                        pos_text = (
                                            f" Posição do robô: x={robot_position.get('x', 0):.1f}, "
                                            f"z={robot_position.get('z', 0):.1f}, "
                                            f"rotação={robot_position.get('rotation', 0):.1f}°."
                                        )

                                    self._messages.append({
                                        "role": "tool",
                                        "tool_call_id": tc.id,
                                        "content": f"Imagem capturada com sucesso. Proximidade indisponível: {prox_error}",
                                    })

                                    observe_img_content: list[dict[str, Any]] = [
                                        {"type": "text", "text": f"Aqui está a imagem da câmera frontal do robô:{render_desc}{pos_text} (Proximidade indisponível: {prox_error})"},
                                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                                    ]

                                    self._messages.append({
                                        "role": "user",
                                        "content": observe_img_content,
                                    })
                                else:
                                    self._messages.append({
                                        "role": "tool",
                                        "tool_call_id": tc.id,
                                        "content": f"Proximidade indisponível: {prox_error}",
                                    })
                            else:
                                if _is_valid_base64(image_base64):
                                    render_desc = ""
                                    if render_method == "2d":
                                        render_desc = " A imagem é uma visão superior (mapa 2D) da arena — verde é o chão, marrom são paredes, azul é o robô."
                                    elif render_method == "webgl":
                                        render_desc = " A imagem é uma visão em primeira pessoa (3D) da câmera frontal do robô."

                                    pos_text = ""
                                    if robot_position:
                                        pos_text = (
                                            f" Posição do robô: x={robot_position.get('x', 0):.1f}, "
                                            f"z={robot_position.get('z', 0):.1f}, "
                                            f"rotação={robot_position.get('rotation', 0):.1f}°."
                                        )

                                    prox_text = ""
                                    if proximity:
                                        frente = proximity.get("frente", "N/A")
                                        tras = proximity.get("tras", "N/A")
                                        prox_text = f" Proximidade — Frente: {frente} cm | Trás: {tras} cm."

                                    self._messages.append({
                                        "role": "tool",
                                        "tool_call_id": tc.id,
                                        "content": f"Imagem capturada com sucesso.{prox_text}",
                                    })

                                    observe_img_content_ok: list[dict[str, Any]] = [
                                        {"type": "text", "text": f"Aqui está a imagem da câmera frontal do robô:{render_desc}{pos_text}{prox_text}"},
                                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                                    ]

                                    self._messages.append({
                                        "role": "user",
                                        "content": observe_img_content_ok,
                                    })
                                elif proximity:
                                    frente = proximity.get("frente", "N/A")
                                    tras = proximity.get("tras", "N/A")
                                    prox_text = f"Proximidade — Frente: {frente} cm | Trás: {tras} cm"

                                    self._messages.append({
                                        "role": "tool",
                                        "tool_call_id": tc.id,
                                        "content": f"Imagem não disponível. {prox_text}",
                                    })
                                else:
                                    self._messages.append({
                                        "role": "tool",
                                        "tool_call_id": tc.id,
                                        "content": "Erro: observe não retornou dados válidos.",
                                    })
                        else:
                            self._messages.append({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": result,
                            })
                    else:
                        self._messages.append({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                goal_msg = self._check_proximity_goal()
                if goal_msg:
                    self._messages.append({"role": "user", "content": goal_msg})
            else:
                if message.content:
                    self._messages.append({"role": "assistant", "content": message.content})
                    self._emit("final_answer", {"step": step, "content": message.content})
                    return message.content
                return "Não consegui processar sua solicitação."

        self._emit("max_steps_reached", {"max_steps": max_steps})
        return (
            f"Nao consegui completar a tarefa apos {max_steps} passos. "
            "Tente reformular o pedido ou verificar se o ambiente esta funcionando."
        )