import re
import json
import httpx

from ..server import mcp
from ..context import get_backend, get_translator
from ..translator import TranslationError

LBML_SEQUENCE_RE = re.compile(r"^(D\d+[FBLR];|R\d+[LR];)+$")
LBML_COMMAND_RE = re.compile(r"([DR])(\d+)([FBLR]);")


def _expand_lbml_steps(lbml: str) -> list[str]:
    steps: list[str] = []
    for command_type, value, direction in LBML_COMMAND_RE.findall(lbml):
        if command_type == "D" and direction in ("L", "R"):
            steps.append(f"R90{direction};")
            steps.append(f"D{value}F;")
            continue
        steps.append(f"{command_type}{value}{direction};")
    return steps


def _parse_distance_step(step: str) -> tuple[int, str] | None:
    match = LBML_COMMAND_RE.fullmatch(step)
    if not match:
        return None

    command_type, value, direction = match.groups()
    if command_type != "D" or direction not in ("F", "B"):
        return None

    return int(value), direction


def _get_blocked_distance_check(step: str, readings: dict) -> dict | None:
    parsed_step = _parse_distance_step(step)
    if parsed_step is None:
        return None

    requested_distance_cm, direction = parsed_step
    minimum_safe_distance_cm = readings.get("minimum_safe_distance_cm", 20)
    sensor_key = "front_cm" if direction == "F" else "rear_cm"
    safety_key = "safe_to_move_forward" if direction == "F" else "safe_to_move_backward"
    direction_label = "frente" if direction == "F" else "trás"
    available_distance_cm = readings.get(sensor_key)

    if available_distance_cm is None:
        return {
            "requested_distance_cm": requested_distance_cm,
            "available_distance_cm": None,
            "max_safe_travel_cm": 0,
            "minimum_safe_distance_cm": minimum_safe_distance_cm,
            "direction": direction_label,
            "reason": f"leitura do sensor de {direction_label} indisponível",
        }

    max_safe_travel_cm = max(float(available_distance_cm) - float(minimum_safe_distance_cm), 0.0)
    safe_to_move = readings.get(safety_key)

    if safe_to_move is False or requested_distance_cm > max_safe_travel_cm:
        return {
            "requested_distance_cm": requested_distance_cm,
            "available_distance_cm": available_distance_cm,
            "max_safe_travel_cm": round(max_safe_travel_cm, 2),
            "minimum_safe_distance_cm": minimum_safe_distance_cm,
            "direction": direction_label,
            "reason": (
                f"movimento de {requested_distance_cm} cm para {direction_label} deixaria o robô "
                f"a menos de {minimum_safe_distance_cm} cm do obstáculo"
            ),
        }

    return None


def _build_blocked_response(
    *,
    original: str,
    preprocessed: str,
    lbml: str,
    step: str,
    blocked_check: dict,
    readings: dict,
    executed_steps: list[str],
    last_result: dict | None,
) -> str:
    final_state = (last_result or {}).get("final_state") or readings.get("robot_position")
    return json.dumps(
        {
            "original_command": original,
            "preprocessed_command": preprocessed,
            "translated_lbml": lbml,
            "accepted": bool(executed_steps),
            "completed": False,
            "status": "blocked_by_proximity",
            "needs_reobservation": bool(executed_steps),
            "request_id": (last_result or {}).get("request_id"),
            "target_client_id": (last_result or {}).get("target_client_id"),
            "final_state": final_state,
            "message": blocked_check["reason"],
            "summary": "movimento bloqueado por proximidade",
            "executed_lbml_steps": executed_steps,
            "blocked_lbml_step": step,
            "proximity": {
                "front_cm": readings.get("front_cm"),
                "rear_cm": readings.get("rear_cm"),
                "minimum_safe_distance_cm": blocked_check["minimum_safe_distance_cm"],
                "requested_distance_cm": blocked_check["requested_distance_cm"],
                "available_distance_cm": blocked_check["available_distance_cm"],
                "max_safe_travel_cm": blocked_check["max_safe_travel_cm"],
                "direction": blocked_check["direction"],
            },
        },
        ensure_ascii=False,
    )


@mcp.tool()
async def move(command: str) -> str:
    """Move o robô de acordo com um comando em linguagem natural. O robô entende comandos como 'ande 30cm para frente', 'vire 90 graus para direita', ou sequências como 'ande 40cm para frente, depois vire 90 graus para esquerda'."""
    try:
        translator = get_translator()
        original, preprocessed, lbml = translator.translate_verbose(command)
    except TranslationError as e:
        return json.dumps(
            {
                "original_command": command,
                "accepted": False,
                "completed": False,
                "status": "translation_error",
                "needs_reobservation": False,
                "error": f"não entendi o comando '{command}'. Pode reformular? ({e})",
            },
            ensure_ascii=False,
        )

    if lbml == "ERRO" or not LBML_SEQUENCE_RE.match(lbml):
        return json.dumps(
            {
                "original_command": command,
                "accepted": False,
                "completed": False,
                "status": "translation_error",
                "needs_reobservation": False,
                "error": f"não entendi o comando '{command}'. Pode reformular?",
            },
            ensure_ascii=False,
        )

    try:
        backend = get_backend()
        execution_steps = _expand_lbml_steps(lbml)
        executed_steps: list[str] = []
        result = None

        for step in execution_steps:
            if _parse_distance_step(step) is not None:
                readings = await backend.get_proximity()
                blocked = _get_blocked_distance_check(step, readings)
                if blocked is not None:
                    return _build_blocked_response(
                        original=original,
                        preprocessed=preprocessed,
                        lbml=lbml,
                        step=step,
                        blocked_check=blocked,
                        readings=readings,
                        executed_steps=executed_steps,
                        last_result=result,
                    )

            result = await backend.execute_lbml(step)
            executed_steps.append(step)

            if not result.get("completed", False):
                break

        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "executed_lbml_steps": executed_steps,
                "accepted": result.get("accepted", False),
                "completed": result.get("completed", False),
                "status": result.get("status", "unknown"),
                "needs_reobservation": True,
                "request_id": result.get("request_id"),
                "target_client_id": result.get("target_client_id"),
                "final_state": result.get("final_state"),
                "message": result.get("message"),
                "summary": "movimento concluído" if result.get("completed") else "movimento aceito, mas sem confirmação final",
            },
            ensure_ascii=False,
        )

    except RuntimeError as e:
        error_str = str(e)
        if "409" in error_str:
            error_str = "o simulador não está conectado. Abra o simulador no navegador para executar movimentos."
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "execution_error",
                "needs_reobservation": False,
                "error": f"falha na execução — {error_str}",
            },
            ensure_ascii=False,
        )
    except httpx.TimeoutException:
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "timeout",
                "needs_reobservation": False,
                "error": "timeout ao executar movimento",
            },
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {
                "original_command": original,
                "preprocessed_command": preprocessed,
                "translated_lbml": lbml,
                "accepted": False,
                "completed": False,
                "status": "execution_error",
                "needs_reobservation": False,
                "error": f"falha na execução — {e}",
            },
            ensure_ascii=False,
        )
