from typing import Literal

from ..context import get_backend, get_control
from ..server import mcp
from ..services.search_orchestrator import SearchOrchestrator


@mcp.tool()
async def approach(
    target: Literal["object", "front_obstacle"],
    description: str | None = None,
    stop_distance_cm: float = 50,
) -> dict:
    """Aproxima e verifica a chegada a 50 cm (ou distância solicitada, mínimo 20 cm). object exige descrição e inclui busca. front_obstacle usa o obstáculo à frente, sem identificá-lo como parede. Para e informa bloqueios, sem contornar."""
    if target == "object" and not (description and description.strip()):
        return {"status": "failed", "reason": "description_required"}
    if not 20 <= stop_distance_cm <= 200:
        return {"status": "failed", "reason": "invalid_stop_distance"}
    return await get_control().run(
        lambda: SearchOrchestrator(get_backend()).approach(
            target, description, stop_distance_cm
        )
    )
