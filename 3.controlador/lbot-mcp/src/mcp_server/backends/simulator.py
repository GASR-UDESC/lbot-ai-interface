import asyncio
import time
import uuid

import httpx

from .base import LBotBackend

TERMINAL = {"completed", "blocked", "cancelled", "failed", "timed_out"}


class SimulatorBackend(LBotBackend):
    def __init__(
        self, base_url="http://localhost:3001", timeout=10.0, command_timeout=60.0
    ):
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._command_timeout = command_timeout
        self._client = None
        self._last_session = None
        self._last_revision = -1

    @property
    def client(self):
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self._timeout)
        return self._client

    async def _request(self, method, path, **kwargs):
        response = await self.client.request(method, self.base_url + path, **kwargs)
        if response.is_error:
            try:
                error = response.json().get("error", "backend_error")
            except ValueError:
                error = "backend_error"
            raise RuntimeError(error)
        return response.json()

    async def _validate_observation(self, data):
        state = await self.get_state()
        if data.get("session_id") != state["session_id"]:
            raise RuntimeError("stale_session")
        if self._last_session != data["session_id"]:
            self._last_session = data["session_id"]
            self._last_revision = -1
        if data.get("revision", -1) < self._last_revision:
            raise RuntimeError("stale_observation")

    async def get_camera(self):
        data = await self._request("GET", "/api/camera")
        if not data.get("image") or data.get("renderMethod") != "webgl":
            raise RuntimeError("camera_unavailable")
        await self._validate_observation(data)
        # Diagnostic pose is deliberately excluded from robot observations.
        return {
            k: data[k]
            for k in (
                "image",
                "frame_id",
                "session_id",
                "revision",
                "captured_at",
                "intrinsics",
                "range_projection",
            )
            if k in data
        }

    async def get_proximity(self):
        data = await self._request("GET", "/api/sensors")
        if data.get("readings") is None:
            raise RuntimeError("sensor_unavailable")
        await self._validate_observation(data)
        return data

    async def execute_lbml(self, lbml, *, wait=False, session_id=None):
        state = await self.get_state()
        if session_id is not None and state["session_id"] != session_id:
            raise RuntimeError("stale_session")
        command_id = str(uuid.uuid4())
        try:
            data = await self._request(
                "POST",
                "/api/commands",
                json={
                    "command": lbml,
                    "command_id": command_id,
                    "session_id": state["session_id"],
                    "source": "http",
                },
            )
        except httpx.HTTPError:
            await self.stop_best_effort()
            # The server may already have accepted it: never blindly replay an actuator request.
            return {
                "status": "failed",
                "reason": "execution_unknown",
                "command_id": command_id,
            }
        if not wait:
            return data
        deadline = time.monotonic() + self._command_timeout
        try:
            while data["status"] not in TERMINAL:
                if time.monotonic() >= deadline:
                    await self.stop()
                    return {
                        "status": "timed_out",
                        "reason": "command_timeout",
                        "command_id": command_id,
                    }
                await asyncio.sleep(
                    0.05
                )  # Poll interval, not an estimate of movement completion.
                data = await self._request("GET", "/api/commands/" + command_id)
        except httpx.HTTPError:
            await self.stop_best_effort()
            return {
                "status": "failed",
                "reason": "execution_unknown",
                "command_id": command_id,
            }
        if data.get("session_id") is not None and data.get("revision") is not None:
            self._last_session, self._last_revision = (
                data["session_id"],
                data["revision"],
            )
        return data

    async def stop(self):
        return await self._request("POST", "/api/stop")

    async def stop_best_effort(self):
        try:
            await self.stop()
        except Exception:
            pass

    async def get_state(self):
        return (await self._request("GET", "/api/state"))["state"]

    async def health_check(self):
        try:
            return (await self._request("GET", "/api/health"))["status"] == "online"
        except Exception:
            return False

    async def close(self):
        if self._client is not None:
            await self._client.aclose()
            self._client = None
