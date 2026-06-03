import json

import httpx

from ..server import mcp
from ..context import get_backend


@mcp.tool()
async def proximity() -> str:
    """Lê os sensores de proximidade frontal e traseiro do robô."""
    MINIMUM_SAFE_DISTANCE_CM = 20

    try:
        backend = get_backend()
        readings = await backend.get_proximity()
        front_cm = readings.get("front_cm", readings.get("frente"))
        rear_cm = readings.get("rear_cm", readings.get("tras"))
        minimum_safe_distance_cm = readings.get(
            "minimum_safe_distance_cm", MINIMUM_SAFE_DISTANCE_CM
        )
        payload = {
            "front_cm": front_cm,
            "rear_cm": rear_cm,
            "safe_to_move_forward": readings.get(
                "safe_to_move_forward",
                front_cm is not None and front_cm >= minimum_safe_distance_cm,
            ),
            "safe_to_move_backward": readings.get(
                "safe_to_move_backward",
                rear_cm is not None and rear_cm >= minimum_safe_distance_cm,
            ),
            "minimum_safe_distance_cm": minimum_safe_distance_cm,
            "robot_position": readings.get("robot_position"),
            "summary": "leituras de proximidade atualizadas",
        }
        return json.dumps(payload, ensure_ascii=False)

    except RuntimeError as e:
        return json.dumps({"error": f"sensor de proximidade indisponível: {e}"}, ensure_ascii=False)
    except httpx.TimeoutException:
        return json.dumps({"error": "timeout ao ler sensores de proximidade"}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)
