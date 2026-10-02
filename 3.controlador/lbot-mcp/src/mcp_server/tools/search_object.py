from ..context import get_backend, get_control
from ..server import mcp
from ..services.search_orchestrator import SearchOrchestrator


@mcp.tool()
async def search_object(description: str) -> dict:
    """Procura um objeto por descrição (ex.: 'cubo vermelho'). Pode girar e explorar com movimentos curtos verificados. Não aproxima do alvo. detected=false significa que não o localizou na busca limitada, não ausência em toda a arena."""
    if not description.strip():
        return {"status": "failed", "reason": "empty_description"}
    return await get_control().run(
        lambda: SearchOrchestrator(get_backend()).run(description.strip())
    )
