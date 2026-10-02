import asyncio
import re

from ..lbml import validate_lbml

# A deliberately narrow executor grammar; the brain decomposes unrestricted user language.
ATOM = re.compile(
    r"(?:ande|avance|recue|vire|gire)\s+(\d+)\s*(?:cm|cent[ií]metros|graus)\s+(?:para\s+)?(?:a\s+)?(?:o\s+)?(frente|tr[aá]s|direita|esquerda)",
    re.I,
)


def expected_lbml(command):
    text = command.strip().lower()
    matches = list(ATOM.finditer(text))
    residue = ATOM.sub("", text)
    if not matches or re.sub(r"[\s,;.]|\b(?:e|depois|ent[aã]o)\b", "", residue):
        raise ValueError("unsupported_concrete_command")
    parts = []
    for m in matches:
        atom = m.group(0)
        amount = int(m.group(1))
        direction = m.group(2)
        rotation = atom.startswith(("vire", "gire"))
        if rotation != ("graus" in atom):
            raise ValueError("invalid_movement_unit")
        if (atom.startswith("recue") and direction not in ("trás", "tras")) or (
            atom.startswith("avance") and direction != "frente"
        ):
            raise ValueError("conflicting_movement_direction")
        if rotation and direction not in ("direita", "esquerda"):
            raise ValueError("invalid_rotation_direction")
        if not rotation and direction not in ("frente", "trás", "tras"):
            raise ValueError("use_rotation_before_sideways_motion")
        if not 0 < amount <= (720 if rotation else 400):
            raise ValueError("invalid_movement_amount")
        parts.append(
            f"{'R' if rotation else 'D'}{amount}{('R' if direction == 'direita' else 'L') if rotation else ('F' if direction == 'frente' else 'B')};"
        )
    return "".join(parts)


async def translate_and_move(backend, translator, command):
    expected = expected_lbml(command)
    lbml = await asyncio.to_thread(translator.translate, command)
    if not validate_lbml(lbml) or lbml != expected:
        return {
            "status": "failed",
            "reason": "translation_mismatch",
            "requested_lbml": expected,
            "translated_lbml": lbml,
        }
    # Segment movements, and check sensors before each segment. Rotations use the backend collision guard.
    records = []
    initial = await backend.get_proximity()
    session = initial.get("session_id")
    if session is None:
        raise RuntimeError("invalid_observation")
    for kind, amount, direction in re.findall(r"([DR])(\d+)([FBLR]);", lbml):
        remaining = int(amount)
        while remaining:
            step = min(20 if kind == "D" else 45, remaining)
            if kind == "D":
                sensor = await backend.get_proximity()
                if sensor.get("session_id") != session:
                    raise RuntimeError("stale_session")
                name = "frente" if direction == "F" else "tras"
                value = sensor.get("readings", {}).get(name)
                if (
                    value is None
                    or sensor.get("validity", {}).get(name) == "unavailable"
                ):
                    return {
                        "status": "failed",
                        "reason": "sensor_unavailable",
                        "commands": records,
                    }
                if value - step < 20:
                    return {
                        "status": "blocked",
                        "reason": "obstacle_blocked",
                        "commands": records,
                    }
            record = await backend.execute_lbml(
                f"{kind}{step}{direction};", wait=True, session_id=session
            )
            records.append(record)
            if record["status"] != "completed":
                return {
                    "status": record["status"],
                    "reason": record.get("reason"),
                    "commands": records,
                }
            remaining -= step
    verification = await backend.get_proximity()
    if verification.get("session_id") != session:
        raise RuntimeError("stale_session")
    return {
        "status": "completed",
        "verification": verification,
        "lbml": lbml,
        "commands": records,
        "distance_cm": sum(r.get("distance_cm", 0) for r in records),
        "rotation_degrees": sum(r.get("rotation_degrees", 0) for r in records),
    }
