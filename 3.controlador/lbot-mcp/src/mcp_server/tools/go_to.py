import json
import os

import httpx
from openai import OpenAI

from ..server import mcp
from ..context import get_backend
from ..services.go_to_orchestrator import (
    GoToOrchestrator,
    DIRECTION_ANGLES,
)


def _build_llm_client() -> tuple[OpenAI, str]:
    base_url = os.environ.get("LBOT_LLM_URL", "http://127.0.0.1:1234/v1")
    api_key = os.environ.get("LBOT_LLM_API_KEY", "lm-studio")
    model = os.environ.get("LBOT_LLM_MODEL", "auto")
    return OpenAI(base_url=base_url, api_key=api_key), model


@mcp.tool()
async def go_to(target: str, direction: str = "frente") -> str:
    """Vai ate um alvo especifico em uma direcao cardinal.

    O robo gira para a direcao indicada, confirma o alvo via camera e LLM,
    e se move ate ele. Para paredes, para a ~20cm. Para objetos, usa
    OpenCV para centralizar e se aproxima ate ~50cm.

    Args:
        target: Descricao do alvo. Ex: 'parede', 'cubo vermelho', 'esfera azul', 'cone'.
        direction: Direcao cardinal. Valores: 'frente' (padrao), 'esquerda', 'direita', 'tras'.

    Retorna:
        JSON com status (found/not_found/error), target, direction,
        final_distance_cm e steps_taken.
    """
    if not target or not isinstance(target, str) or not target.strip():
        return json.dumps({
            "status": "error",
            "error": "alvo nao pode ser vazio",
        })

    target = target.strip()
    direction = (direction or "frente").strip().lower()

    if direction not in DIRECTION_ANGLES:
        return json.dumps({
            "status": "error",
            "error": f"direcao invalida: '{direction}'. Use: frente, esquerda, direita, tras",
        })

    try:
        backend = get_backend()
        llm_client, llm_model = _build_llm_client()
        orchestrator = GoToOrchestrator(
            backend, llm_client=llm_client, llm_model=llm_model,
        )
        result = await orchestrator.run(target, direction)
        return json.dumps(result)
    except RuntimeError as e:
        return json.dumps({"status": "error", "error": str(e)})
    except httpx.TimeoutException:
        return json.dumps({"status": "error", "error": "timeout ao comunicar com o backend"})
    except Exception as e:
        return json.dumps({"status": "error", "error": str(e)})
