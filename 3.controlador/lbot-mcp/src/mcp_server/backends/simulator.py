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
        }

    async def get_proximity_sensor(self) -> dict:
        """Retorna leituras numericas brutas dos sensores frontal e traseiro."""
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
        return {
            "frente": float(readings.get("frente", 400)),
            "tras": float(readings.get("tras", 400)),
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

        return data["readings"]

    async def execute_lbml(self, lbml: str) -> dict:
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

        return {
            "accepted": data["accepted"],
            "command": data.get("command", lbml),
            "status": "executado",
            "target_client_id": data.get("targetClientId"),
        }

    async def get_state(self) -> dict | None:
        try:
            response = await self.client.get(f"{self.base_url}/api/state")
            response.raise_for_status()
            data = response.json()
        except httpx.HTTPError:
            return None

        return data.get("state")

    async def health_check(self) -> bool:
        try:
            response = await self.client.get(f"{self.base_url}/api/health")
            return response.status_code == 200
        except httpx.HTTPError:
            return False
