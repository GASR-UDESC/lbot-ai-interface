import json
import os

import httpx
from openai import OpenAI

from ..server import mcp
from ..context import get_backend
from ..services.search_orchestrator import SearchOrchestrator


def _build_llm_client() -> tuple[OpenAI, str]:
    base_url = os.environ.get("LBOT_LLM_URL", "http://127.0.0.1:1234/v1")
    api_key = os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
    model = os.environ.get("LBOT_LLM_MODEL", "auto")
    return OpenAI(base_url=base_url, api_key=api_key), model


@mcp.tool()
async def search_object(description: str) -> str:
    """Busca um objeto na arena de forma autonoma.

    O robo faz varredura 360 graus usando LLM com visao para detectar
    o objeto, centraliza via OpenCV e se aproxima ate ~50cm.

    Args:
        description: Descricao do objeto a buscar (ex: 'cubo vermelho', 'esfera azul', 'cone').

    Retorna:
        JSON com status (found/not_found), object_type, object_color,
        bounding_box, final_distance_cm e steps_taken.
        Fases: scan com LLM (4 rotacoes) -> center via OpenCV -> approach.
    """
    if not description or not isinstance(description, str) or not description.strip():
        return json.dumps({
            "status": "error",
            "error": "descricao do objeto nao pode ser vazia",
        })

    try:
        backend = get_backend()
        llm_client, llm_model = _build_llm_client()
        orchestrator = SearchOrchestrator(
            backend, llm_client=llm_client, llm_model=llm_model,
        )
        result = await orchestrator.run(description.strip())
        return json.dumps(result)
    except RuntimeError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except httpx.TimeoutException:
        return json.dumps({"status": "error", "error": "timeout ao comunicar com o backend"})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})
