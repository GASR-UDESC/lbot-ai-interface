import asyncio
from time import monotonic
from inspect import isawaitable

import httpx

from .base import (
    LBotBackend,
    ERROR_CAMERA_UNAVAILABLE,
    ERROR_SENSOR_UNAVAILABLE,
    ERROR_COMMAND_FAILED,
    ERROR_BACKEND_UNREACHABLE,
    ERROR_INVALID_RESPONSE,
)


class SimulatorBackend(LBotBackend):

    def __init__(self, base_url: str = "http://localhost:3001", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._timeout = timeout

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=httpx.Timeout(self._timeout))
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get_camera(self) -> dict:
        try:
            response = await self.client.get(f"{self.base_url}/api/camera")
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"{ERROR_CAMERA_UNAVAILABLE}: {e}") from e

        if not data.get("connected") or data.get("image") is None:
            error = data.get("error", ERROR_CAMERA_UNAVAILABLE)
            raise RuntimeError(error)

        return {
            "image": data["image"],
            "render_method": data.get("renderMethod", "unknown"),
            "robot_position": data.get("robotPosition"),
            "observation_mode": data.get("observationMode", "unknown"),
            "warning": data.get("warning"),
        }

    async def get_proximity(self) -> dict:
        try:
            response = await self.client.get(f"{self.base_url}/api/sensors")
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"{ERROR_SENSOR_UNAVAILABLE}: {e}") from e

        if data.get("readings") is None:
            error = data.get("error", ERROR_SENSOR_UNAVAILABLE)
            raise RuntimeError(error)

        readings = data["readings"]
        front_cm = readings.get("frente")
        rear_cm = readings.get("tras")
        minimum_safe_distance_cm = data.get("minimumSafeDistanceCm", 20)
        return {
            "front_cm": front_cm,
            "rear_cm": rear_cm,
            "safe_to_move_forward": data.get(
                "safeToMoveForward",
                front_cm is not None and front_cm >= minimum_safe_distance_cm,
            ),
            "safe_to_move_backward": data.get(
                "safeToMoveBackward",
                rear_cm is not None and rear_cm >= minimum_safe_distance_cm,
            ),
            "minimum_safe_distance_cm": minimum_safe_distance_cm,
            "robot_position": data.get("robotPosition"),
        }

    async def execute_lbml(self, lbml: str) -> dict:
        previous_state = await self.get_state()
        try:
            response = await self.client.post(
                f"{self.base_url}/api/commands",
                json={"command": lbml, "source": "http"},
            )
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError as e:
            raise RuntimeError(f"{ERROR_COMMAND_FAILED}: {e}") from e

        if not data.get("accepted"):
            error = data.get("error", ERROR_COMMAND_FAILED)
            raise RuntimeError(error)

        request_id = data.get("requestId")
        completion = None
        if request_id:
            completion = await self._wait_for_command_completion(request_id)

        return {
            "accepted": data["accepted"],
            "command": data.get("command", lbml),
            "request_id": request_id,
            "status": (completion or {}).get("status", "accepted_without_confirmation"),
            "completed": (completion or {}).get("completed", False),
            "message": (completion or {}).get("message"),
            "target_client_id": data.get("targetClientId"),
            "initial_state": previous_state,
            "final_state": (completion or {}).get("state"),
        }

    async def get_state(self) -> dict | None:
        try:
            response = await self.client.get(f"{self.base_url}/api/state")
            response.raise_for_status()
            data = response.json()
            if isawaitable(data):
                data = await data
        except Exception:
            return None

        if not isinstance(data, dict):
            return None

        state = data.get("state")
        if state is None:
            return None
        return {
            "x": state.get("x"),
            "z": state.get("z"),
            "rotation": state.get("rotation"),
            "current_command": state.get("currentCommand"),
            "is_animating": state.get("isAnimating"),
            "updated_at": state.get("updatedAt"),
            "last_request_id": state.get("lastRequestId"),
            "last_command_status": state.get("lastCommandStatus"),
            "last_command_message": state.get("lastCommandMessage"),
        }

    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def _wait_for_command_completion(self, request_id: str) -> dict:
        deadline = monotonic() + max(self._timeout, 5.0)
        last_state = None

        while monotonic() < deadline:
            state = await self.get_state()
            if state is not None:
                last_state = state
                if state.get("last_request_id") == request_id and not state.get("is_animating"):
                    status = state.get("last_command_status") or "completed"
                    return {
                        "completed": status == "completed",
                        "status": status,
                        "message": state.get("last_command_message"),
                        "state": state,
                    }
            await asyncio.sleep(0.2)

        return {
            "completed": False,
            "status": "timeout_waiting_completion",
            "message": "tempo limite aguardando conclusão do comando",
            "state": last_state,
        }
