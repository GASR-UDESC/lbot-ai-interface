import httpx

from ..server import mcp
from ..context import get_backend


@mcp.tool()
async def proximity() -> str:
    """Lê os sensores de proximidade frontal e traseiro do robô. Retorna as distâncias em centímetros até o obstáculo mais próximo."""
    MAX_DISTANCE = 400

    try:
        backend = get_backend()
        readings = await backend.get_proximity()

        frente = readings.get("frente")
        tras = readings.get("tras")

        def fmt(val):
            if val is None or val >= MAX_DISTANCE:
                return f"sem obstáculo (>{MAX_DISTANCE}cm)"
            return f"{val} cm"

        return f"Frente: {fmt(frente)} | Trás: {fmt(tras)}"

    except RuntimeError as e:
        return f"Erro: sensor de proximidade indisponível. ({e})"
    except httpx.TimeoutException:
        return "Erro: timeout ao ler sensores de proximidade."
    except Exception as e:
        return f"Erro: {e}"
