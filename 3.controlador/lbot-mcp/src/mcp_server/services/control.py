import asyncio
import os
import uuid
from collections.abc import Awaitable, Callable

from .telemetry import record


class ControlService:
    """Exclusive, cancellable robot operation; all tools and skills share this owner."""

    def __init__(self, backend):
        self.backend = backend
        self._task = None

    async def run(self, action: Callable[[], Awaitable[dict]]) -> dict:
        if self._task is not None and not self._task.done():
            return {"status": "failed", "reason": "busy"}
        operation_id = str(uuid.uuid4())
        record("core", "operation_started", {"operation_id": operation_id})

        async def invoke():
            return await action()

        task = self._task = asyncio.create_task(invoke())
        try:
            result = await asyncio.wait_for(
                task, float(os.getenv("LBOT_SKILL_TIMEOUT", "180"))
            )
        except asyncio.CancelledError:
            result = {
                "status": "cancelled",
                "reason": "stop_requested",
                "stop_result": await self._stop_backend(),
            }
        except asyncio.TimeoutError:
            result = {
                "status": "timed_out",
                "reason": "skill_timeout",
                "stop_result": await self._stop_backend(),
            }
        except Exception as e:
            result = {
                "status": "blocked"
                if str(e) in {"obstacle_blocked", "collision", "no_progress"}
                else "failed",
                "reason": str(e),
            }
            if str(e) not in {"busy", "stale_session"}:
                result["stop_result"] = await self._stop_backend()
        finally:
            if self._task is task:
                self._task = None
        result["operation_id"] = operation_id
        record("core", "operation_finished", result)
        return result

    async def _stop_backend(self):
        try:
            return await self.backend.stop()
        except Exception as e:
            return {"status": "failed", "reason": str(e)}

    async def stop(self):
        task = self._task
        if task and not task.done():
            task.cancel()
        result = await self._stop_backend()
        if task:
            await asyncio.gather(task, return_exceptions=True)
        return {
            "status": "completed" if result.get("status") == "completed" else "failed",
            "reason": "stop_requested",
            "backend": result,
        }
