from abc import ABC, abstractmethod


class LBotBackend(ABC):
    """Robot boundary. Distances are cm, angles are degrees; absolute pose is optional."""

    @abstractmethod
    async def get_camera(self) -> dict: ...
    @abstractmethod
    async def get_proximity(self) -> dict: ...
    @abstractmethod
    async def execute_lbml(
        self, lbml: str, *, wait: bool = False, session_id: str | None = None
    ) -> dict: ...
    @abstractmethod
    async def stop(self) -> dict: ...
    async def get_proximity_sensor(self) -> dict:
        data = await self.get_proximity()
        if not data.get("readings") or any(
            v == "unavailable" for v in data.get("validity", {}).values()
        ):
            raise RuntimeError("sensor_unavailable")
        return data["readings"]

    async def capabilities(self) -> dict:
        return {
            "camera": True,
            "proximity": ["frente", "tras"],
            "stop": True,
            "absolute_pose": False,
            "distance_unit": "cm",
            "angle_unit": "degrees",
        }

    async def get_state(self) -> dict | None:
        return None

    async def health_check(self) -> bool:
        return True

    async def close(self) -> None:
        pass
