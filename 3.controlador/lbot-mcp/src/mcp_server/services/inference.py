import asyncio
import os
import time

from openai import AsyncOpenAI

from .telemetry import record


class InferenceClient:
    def __init__(self, base_url=None, model=None):
        self.model = model or os.getenv("LBOT_LLM_MODEL", "qwen3.5-4b")
        if self.model == "auto":
            raise ValueError(
                "Configure LBOT_LLM_MODEL explicitly; auto is not supported"
            )
        self.client = AsyncOpenAI(
            base_url=base_url or os.getenv("LBOT_LLM_URL", "http://127.0.0.1:1234/v1"),
            api_key=os.getenv("LBOT_LLM_API_KEY", "lm-studio"),
            timeout=float(os.getenv("LBOT_INFERENCE_TIMEOUT", "60")),
            max_retries=0,
        )
        self._lock = asyncio.Lock()

    async def complete(self, **kwargs):
        async with self._lock:
            started = time.monotonic()
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model=self.model,
                    temperature=kwargs.pop("temperature", 0.2),
                    max_tokens=768,
                    extra_body={"reasoning_effort": "none"},
                    seed=42,
                    **kwargs,
                ),
                float(os.getenv("LBOT_INFERENCE_TIMEOUT", "60")),
            )

            record(
                "inference",
                "completed",
                {
                    "model": self.model,
                    "seconds": time.monotonic() - started,
                    "usage": response.usage.model_dump() if response.usage else None,
                },
            )
            return response

    async def close(self):
        await self.client.close()


_instance = None


def get_inference():
    global _instance
    if _instance is None:
        _instance = InferenceClient()
    return _instance


async def close_inference():
    global _instance
    if _instance is not None:
        await _instance.close()
        _instance = None
