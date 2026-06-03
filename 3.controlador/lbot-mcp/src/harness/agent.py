import base64
import json
import logging
import os
import re
import unicodedata
from copy import deepcopy
from typing import Any, Callable

from openai import OpenAI

from .mcp_client import MCPClient
from .personality import SYSTEM_PROMPT, get_tools_description

logger = logging.getLogger(__name__)

_BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]+=*$')

_MAX_CONTEXT_TOKENS = int(os.environ.get("LBOT_MAX_CONTEXT_TOKENS", "4000"))
_APPROX_CHARS_PER_TOKEN = 4
_MINIMUM_SAFE_DISTANCE_CM = 20

EventCallback = Callable[[str, dict[str, Any]], None] | None


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


def _try_parse_json(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _format_float(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.1f}"
    return "desconhecido"


def _normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii").lower()


def _extract_visual_direction(text: str | None) -> str | None:
    if not text:
        return None
    normalized = _normalize_text(text)
    left_patterns = [
        r"esta a esquerda",
        r"esta a esquerda da imagem",
        r"visivel a esquerda",
        r"objeto a esquerda",
        r"alvo a esquerda",
        r"esfera .* a esquerda",
    ]
    right_patterns = [
        r"esta a direita",
        r"esta a direita da imagem",
        r"visivel a direita",
        r"objeto a direita",
        r"alvo a direita",
        r"esfera .* a direita",
    ]
    if any(re.search(pattern, normalized) for pattern in left_patterns):
        return "left"
    if any(re.search(pattern, normalized) for pattern in right_patterns):
        return "right"
    if "esquerda" in normalized and "direita" not in normalized:
        return "left"
    if "direita" in normalized and "esquerda" not in normalized:
        return "right"
    return None


def _extract_rotation_direction(command: str | None) -> str | None:
    if not command:
        return None
    normalized = _normalize_text(command)
    if not any(keyword in normalized for keyword in ("gire", "girar", "vire", "virar")):
        return None
    if "esquerda" in normalized and "direita" not in normalized:
        return "left"
    if "direita" in normalized and "esquerda" not in normalized:
        return "right"
    return None


def _build_alignment_guardrail_error(visual_direction: str, command: str) -> str:
    side = "esquerda" if visual_direction == "left" else "direita"
    correction = "esquerda" if visual_direction == "left" else "direita"
    return json.dumps(
        {
            "accepted": False,
            "completed": False,
            "status": "guardrail_blocked",
            "needs_reobservation": False,
            "error": (
                f"Inconsistencia de centralizacao: voce disse que o alvo esta a {side} da imagem, "
                f"mas tentou executar '{command}'. Se o alvo esta a {side}, o giro correto para centralizar "
                f"e para a {correction}. Corrija o sentido do giro, use um angulo pequeno e observe novamente."
            ),
        },
        ensure_ascii=False,
    )


def _is_forward_motion_command(command: str | None) -> bool:
    if not command:
        return False
    normalized = _normalize_text(command)
    has_forward = any(keyword in normalized for keyword in ("frente", "avancar", "avance", "andar para frente", "ande para frente"))
    has_move = any(keyword in normalized for keyword in ("ande", "andar", "avance", "avancar", "mova", "ir"))
    return has_forward and has_move


def _is_strictly_centered_text(text: str | None) -> bool:
    if not text:
        return False
    normalized = _normalize_text(text)
    positive_patterns = [
        r"estritamente centraliz",
        r"totalmente centraliz",
        r"dentro do reticulo",
        r"alinhad[oa] de forma inequivoca com o reticulo",
        r"no centro do reticulo",
        r"centralizad[oa] no reticulo",
        r"alinhad[oa] com o reticulo central",
        r"esta alinhad[oa] com o reticulo central",
        r"esta no centro do reticulo",
        r"esta totalmente dentro do reticulo",
    ]
    negative_patterns = [
        r"a esquerda",
        r"a direita",
        r"ainda nao esta centraliz",
        r"nao esta centraliz",
        r"fora do reticulo",
        r"parcialmente fora",
        r"mais proxima do centro",
        r"aproximadamente centraliz",
        r"parece estar alinhad",
        r"parece alinhad",
        r"parece estar no centro",
    ]
    if any(re.search(pattern, normalized) for pattern in negative_patterns):
        return False
    return any(re.search(pattern, normalized) for pattern in positive_patterns)


def _mentions_visual_target_alignment(text: str | None) -> bool:
    if not text:
        return False
    normalized = _normalize_text(text)
    keywords = (
        "reticulo",
        "imagem",
        "camera",
        "centraliz",
        "alinh",
        "esfera",
        "objeto",
        "alvo",
        "visao",
    )
    return any(keyword in normalized for keyword in keywords)


def _build_forward_alignment_guardrail_error(command: str) -> str:
    return json.dumps(
        {
            "accepted": False,
            "completed": False,
            "status": "guardrail_blocked",
            "needs_reobservation": True,
            "error": (
                f"Avanco bloqueado por seguranca visual: voce tentou executar '{command}', mas nao comprovou "
                "que o alvo esta estritamente centralizado dentro do reticulo. Se houver qualquer desvio lateral, "
                "o sensor frontal pode estar apontando para a parede. Reobserve com a camera, confirme alinhamento "
                "estrito e so entao avance."
            ),
        },
        ensure_ascii=False,
    )


def _build_continuation_prompt(partial_content: str | None) -> str:
    base_prompt = (
        "Seu passo anterior foi interrompido por limite de tokens antes de concluir a tarefa. "
        "Continue exatamente de onde parou. Se a tarefa ainda nao terminou, nao encerre cedo: "
        "observe, mova e valide quantas vezes forem necessarias ate concluir ou declarar claramente "
        "que nao foi possivel concluir."
    )
    if partial_content:
        return f"{base_prompt} Ultimo texto interrompido: {partial_content}"
    return base_prompt


def _is_continuation_prompt(msg: dict[str, Any]) -> bool:
    return msg.get("role") == "user" and isinstance(msg.get("content"), str) and msg.get(
        "content", ""
    ).startswith("Seu passo anterior foi interrompido por limite de tokens")


class ReActAgent:
    def __init__(
        self,
        mcp_client: MCPClient,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        max_steps: int = 100,
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
        self._operational_state = self._new_operational_state()
        self._pending_camera_message: dict[str, Any] | None = None

        base_url = base_url or os.environ.get(
            "LBOT_LLM_URL", "http://127.0.0.1:1234/v1"
        )
        api_key = api_key or os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
        model = model or os.environ.get("LBOT_LLM_MODEL", "auto")

        self._llm = OpenAI(base_url=base_url, api_key=api_key)
        self._model = model
        self._tools = get_tools_description()

    def _new_operational_state(self) -> dict[str, Any]:
        return {
            "current_goal": None,
            "safety_distance_cm": _MINIMUM_SAFE_DISTANCE_CM,
            "goal_requires_vision": False,
            "last_pose": None,
            "last_proximity": None,
            "last_camera": None,
            "last_visual_summary": None,
            "last_action": None,
            "last_action_result": None,
            "recent_actions": [],
            "observations_stale": False,
        }

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
        self._operational_state = self._new_operational_state()
        self._pending_camera_message = None

    def _record_action(self, tool_name: str, summary: str, raw: Any) -> None:
        entry = {"tool": tool_name, "summary": summary}
        recent_actions = self._operational_state["recent_actions"]
        recent_actions.append(entry)
        if len(recent_actions) > 6:
            del recent_actions[:-6]
        self._operational_state["last_action"] = tool_name
        self._operational_state["last_action_result"] = raw

    def _update_pose(self, pose: dict[str, Any] | None) -> None:
        if not isinstance(pose, dict):
            return
        self._operational_state["last_pose"] = {
            "x": pose.get("x"),
            "z": pose.get("z"),
            "rotation": pose.get("rotation"),
            "current_command": pose.get("current_command"),
            "is_animating": pose.get("is_animating"),
            "updated_at": pose.get("updated_at"),
            "last_request_id": pose.get("last_request_id"),
            "last_command_status": pose.get("last_command_status"),
            "last_command_message": pose.get("last_command_message"),
        }

    def _update_camera_state(self, camera_data: dict[str, Any]) -> None:
        self._operational_state["last_camera"] = {
            "render_method": camera_data.get("render_method"),
            "observation_mode": camera_data.get("observation_mode"),
            "warning": camera_data.get("warning"),
        }
        self._update_pose(camera_data.get("robot_position"))
        self._operational_state["observations_stale"] = False

    def _set_visual_summary(self, summary: str) -> None:
        self._operational_state["last_visual_summary"] = summary[:240]

    def _compact_history(self) -> None:
        compacted: list[dict[str, Any]] = []
        latest_continuation: dict[str, Any] | None = None
        for msg in self._messages:
            if _is_continuation_prompt(msg):
                latest_continuation = msg
                continue
            compacted.append(msg)

        if latest_continuation is not None:
            compacted.append(latest_continuation)

        self._messages = _trim_messages(compacted, _MAX_CONTEXT_TOKENS)

    def _append_message(self, message: dict[str, Any], *, compact: bool = True) -> None:
        self._messages.append(message)
        if compact:
            self._compact_history()

    def _consume_pending_camera_message(self) -> dict[str, Any] | None:
        pending = self._pending_camera_message
        self._pending_camera_message = None
        return pending

    def _clear_pending_camera_message(self) -> None:
        self._pending_camera_message = None

    def _update_proximity_state(self, proximity_data: dict[str, Any]) -> None:
        self._operational_state["last_proximity"] = {
            "front_cm": proximity_data.get("front_cm"),
            "rear_cm": proximity_data.get("rear_cm"),
            "safe_to_move_forward": proximity_data.get("safe_to_move_forward"),
            "safe_to_move_backward": proximity_data.get("safe_to_move_backward"),
            "minimum_safe_distance_cm": proximity_data.get(
                "minimum_safe_distance_cm", _MINIMUM_SAFE_DISTANCE_CM
            ),
        }
        self._update_pose(proximity_data.get("robot_position"))
        self._operational_state["observations_stale"] = False

    def _update_move_state(self, move_data: dict[str, Any]) -> None:
        self._update_pose(move_data.get("final_state"))
        self._operational_state["observations_stale"] = move_data.get(
            "needs_reobservation", True
        )

    def _build_operational_context(self) -> dict[str, Any]:
        state = deepcopy(self._operational_state)
        pose = state.get("last_pose")
        proximity = state.get("last_proximity")
        camera = state.get("last_camera")
        visual_summary = state.get("last_visual_summary")

        pose_text = "Pose desconhecida."
        if pose:
            pose_text = (
                f"Pose: x={_format_float(pose.get('x'))}, "
                f"z={_format_float(pose.get('z'))}, "
                f"rotacao={_format_float(pose.get('rotation'))}°."
            )

        proximity_text = "Sem leitura recente de proximidade."
        if proximity:
            proximity_text = (
                f"Proximidade: frente={_format_float(proximity.get('front_cm'))} cm, "
                f"tras={_format_float(proximity.get('rear_cm'))} cm, "
                f"seguro_frente={proximity.get('safe_to_move_forward')}, "
                f"seguro_tras={proximity.get('safe_to_move_backward')}."
            )

        camera_text = "Sem leitura recente de camera."
        if camera:
            warning = camera.get("warning")
            camera_text = (
                f"Camera: modo={camera.get('observation_mode')}, "
                f"render={camera.get('render_method')}"
                + (f", aviso={warning}" if warning else "")
                + "."
            )
            if visual_summary:
                camera_text += f" Resumo visual: {visual_summary}."

        recent_actions = state.get("recent_actions") or []
        actions_text = "; ".join(
            f"{entry.get('tool')}: {entry.get('summary')}" for entry in recent_actions
        ) or "Nenhuma acao recente."

        stale_text = (
            "Observacoes anteriores podem estar desatualizadas porque houve movimento recente. "
            "Reavalie com proximity() antes de decidir novo deslocamento. "
            "Use camera() apenas se a tarefa depender de visao ou se houver duvida sobre o ambiente."
            if state.get("observations_stale")
            else "Observacoes atuais estao frescas ou nao ha movimento recente."
        )

        return {
            "role": "system",
            "content": (
                "Resumo operacional atual:\n"
                f"- Objetivo: {state.get('current_goal') or 'nao definido'}\n"
                f"- Distancia minima de seguranca: {state.get('safety_distance_cm')} cm\n"
                f"- {pose_text}\n"
                f"- {proximity_text}\n"
                f"- {camera_text}\n"
                f"- Ultimas acoes: {actions_text}\n"
                f"- {stale_text}\n"
                "- Nunca avance ou recue se isso violar a margem de 20 cm."
            ),
        }

    def _messages_for_llm(self) -> list[dict[str, Any]]:
        messages = list(self._messages)
        operational_context = self._build_operational_context()["content"]

        if messages and messages[0].get("role") == "system":
            messages[0] = {
                **messages[0],
                "content": f"{messages[0].get('content', '')}\n\n{operational_context}",
            }
        else:
            messages.insert(0, {"role": "system", "content": operational_context})

        pending_camera_message = self._consume_pending_camera_message()
        if pending_camera_message is not None:
            messages.append(pending_camera_message)
        return messages

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

    def _goal_requires_vision(self, goal: str) -> bool:
        normalized = _normalize_text(goal)
        vision_keywords = (
            "procure", "encontre", "ache", "camera", "olhe", "descreva",
            "foto", "aproxime", "chegue perto", "va ate", "va para",
            "o que ha", "qual a distancia", "identifique", "reconheca",
            "localize", "centralize", "alinhe", "objeto", "esfera",
            "cubo", "cone", "parede", "alvo", "cor ", "cor:",
            "amarelo", "azul", "vermelho", "verde", "laranja", "roxo",
        )
        return any(keyword in normalized for keyword in vision_keywords)

    async def run(
        self, goal: str, max_steps: int | None = None, requires_vision: bool | None = None
    ) -> str:
        max_steps = max_steps if max_steps is not None else self._max_steps
        self._cancelled = False
        self._operational_state["current_goal"] = goal
        if requires_vision is None:
            requires_vision = self._goal_requires_vision(goal)
        self._operational_state["goal_requires_vision"] = requires_vision

        self._append_message({"role": "user", "content": goal})

        self._emit("goal", {"goal": goal})

        step = 0
        while step < max_steps:
            if self._cancelled:
                self._emit("cancelled", {})
                return "Interrompido."

            step += 1
            messages = self._messages_for_llm()

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

            if finish_reason == "length" and not message.tool_calls:
                if message.content:
                    self._append_message({"role": "assistant", "content": message.content})
                self._append_message({
                    "role": "user",
                    "content": _build_continuation_prompt(message.content),
                })
                self._emit(
                    "llm_request_retry",
                    {"step": step, "reason": "resposta truncada por limite de tokens"},
                )
                continue

            if message.content and not message.tool_calls:
                self._append_message({"role": "assistant", "content": message.content})
                self._emit("final_answer", {"step": step, "content": message.content})
                return message.content

            if message.tool_calls:
                if message.content:
                    normalized_content = _normalize_text(message.content)
                    if "esfera azul" in normalized_content and "esquerda" in normalized_content:
                        self._set_visual_summary("esfera azul visivel a esquerda do reticulo")
                    elif "esfera azul" in normalized_content and "direita" in normalized_content:
                        self._set_visual_summary("esfera azul visivel a direita do reticulo")

                self._append_message({
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
                            result = await self._mcp.call_tool(
                                "move", {"command": raw_args.get("command", "")}
                            )
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

                    structured_result = _try_parse_json(result)

                    if tool_name == "camera":
                        camera_data = {}
                        if structured_result is not None:
                            camera_data = structured_result

                        image_base64 = ""
                        render_method = "unknown"
                        robot_position = None
                        camera_error = None
                        observation_mode = "unknown"
                        warning = None

                        if isinstance(camera_data, dict):
                            image_base64 = camera_data.get("image", "")
                            render_method = camera_data.get("render_method", "unknown")
                            robot_position = camera_data.get("robot_position")
                            camera_error = camera_data.get("error")
                            observation_mode = camera_data.get("observation_mode", "unknown")
                            warning = camera_data.get("warning")
                        elif isinstance(result, str) and _is_valid_base64(result):
                            image_base64 = result

                        if camera_error:
                            self._record_action("camera", f"erro: {camera_error}", camera_data or result)
                            self._append_message({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": f"Erro ao capturar imagem: {camera_error}",
                            })
                        elif _is_valid_base64(image_base64):
                            self._update_camera_state({
                                "render_method": render_method,
                                "robot_position": robot_position,
                                "observation_mode": observation_mode,
                                "warning": warning,
                            })
                            pos_text = ""
                            if robot_position:
                                pos_text = (
                                    f" Posição do robô: x={robot_position.get('x', 0):.1f}, "
                                    f"z={robot_position.get('z', 0):.1f}, "
                                    f"rotação={robot_position.get('rotation', 0):.1f}°."
                                )
                            render_desc = ""
                            if observation_mode == "topdown_simplified":
                                render_desc = " A imagem e uma visao superior simplificada da arena. Use para orientacao geral, nao para centralizacao fina."
                            elif render_method == "webgl":
                                render_desc = " A imagem é uma visão em primeira pessoa (3D) da câmera frontal do robô."
                            if warning:
                                render_desc += f" Aviso: {warning}"

                            if self._operational_state.get("goal_requires_vision"):
                                visual_summary = (
                                    f"Observacao visual recente em modo {observation_mode or render_method}."
                                    f"{pos_text} Use a cruz de referencia para decidir alinhamento antes de usar front_cm como distancia ao objeto de interesse."
                                )
                            else:
                                visual_summary = (
                                    f"Observacao visual recente em modo {observation_mode or render_method}."
                                    f"{pos_text}"
                                )
                            self._set_visual_summary(visual_summary)
                            self._record_action(
                                "camera",
                                f"captura ok em modo {observation_mode or render_method}",
                                camera_data,
                            )

                            self._append_message({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Imagem capturada com sucesso.",
                            })

                            image_content: list[dict[str, Any]] = [
                                {"type": "text", "text": f"Aqui está a imagem da câmera frontal do robô:{render_desc}{pos_text}"},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}},
                            ]

                            self._pending_camera_message = {
                                "role": "user",
                                "content": image_content,
                            }
                            self._append_message({
                                "role": "user",
                                "content": f"Aqui está a observação visual mais recente do robô.{render_desc}{pos_text} [imagem da câmera disponível apenas nesta rodada]",
                            })
                        else:
                            self._record_action("camera", "imagem invalida", camera_data or result)
                            self._append_message({
                                "role": "tool",
                                "tool_call_id": tc.id,
                                "content": "Erro: a imagem capturada não pôde ser processada (dados de imagem inválidos ou ausentes).",
                            })
                    elif tool_name == "proximity":
                        if structured_result is not None and not structured_result.get("error"):
                            self._update_proximity_state(structured_result)
                            front = structured_result.get("front_cm")
                            rear = structured_result.get("rear_cm")
                            self._record_action(
                                "proximity",
                                f"frente={front} cm, tras={rear} cm",
                                structured_result,
                            )
                        else:
                            self._record_action(
                                "proximity",
                                f"erro: {(structured_result or {}).get('error', result)}",
                                structured_result or result,
                            )
                        self._append_message({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                    elif tool_name == "move":
                        if structured_result is not None and not structured_result.get("error"):
                            self._update_move_state(structured_result)
                            status = structured_result.get("status", "unknown")
                            summary = structured_result.get("summary") or status
                            self._record_action("move", summary, structured_result)
                            self._clear_pending_camera_message()
                        else:
                            self._record_action(
                                "move",
                                f"erro: {(structured_result or {}).get('error', result)}",
                                structured_result or result,
                            )
                        self._append_message({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                    elif tool_name == "state":
                        if structured_result is not None and not structured_result.get("error"):
                            self._update_pose(structured_result)
                            self._record_action(
                                "state",
                                f"pose x={structured_result.get('x')} z={structured_result.get('z')} rot={structured_result.get('rotation')}",
                                structured_result,
                            )
                        else:
                            self._record_action(
                                "state",
                                f"erro: {(structured_result or {}).get('error', result)}",
                                structured_result or result,
                            )
                        self._append_message({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
                    else:
                        self._record_action(tool_name, "resultado recebido", structured_result or result)
                        self._append_message({
                            "role": "tool",
                            "tool_call_id": tc.id,
                            "content": result,
                        })
            else:
                if message.content:
                    self._append_message({"role": "assistant", "content": message.content})
                    self._emit("final_answer", {"step": step, "content": message.content})
                    return message.content
                return "Não consegui processar sua solicitação."

        self._emit("max_steps_reached", {"max_steps": max_steps})
        return (
            "Atingi o número máximo de passos sem concluir o objetivo. "
            "Tente reformular o pedido ou verificar se o ambiente está funcionando."
        )
