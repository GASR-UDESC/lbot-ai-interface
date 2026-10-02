from ..context import get_backend, get_control, get_translator
from ..server import mcp
from ..services.movement import translate_and_move


@mcp.tool()
async def move(command: str) -> dict:
    """Executa movimentos concretos relativos ao robô, confirmados pelo executor. Use frases: 'ande 30 cm para frente', 'ande 10 cm para trás', 'vire 90 graus para direita'. Combine com 'depois'. Decomponha trajetórias em números; para chegar a um alvo use approach. Não use negações nem movimento lateral."""
    return await get_control().run(
        lambda: translate_and_move(get_backend(), get_translator(), command)
    )
