from abc import ABC, abstractmethod
from typing import Any


class LBotBackend(ABC):

    @abstractmethod
    async def get_camera(self) -> dict:
        ...

    @abstractmethod
    async def get_proximity(self) -> dict:
        ...

    @abstractmethod
    async def execute_lbml(self, lbml: str) -> dict:
        ...

    @abstractmethod
    async def get_proximity_sensor(self) -> dict:
        """Retorna leituras numericas brutas dos sensores.

        Returns:
            dict com chaves 'frente' e 'tras' (float). MAX_DISTANCE = 400.
        """
        ...

    @abstractmethod
    async def get_state(self) -> dict | None:
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        ...


ERROR_CAMERA_UNAVAILABLE = "câmera indisponível"
ERROR_SENSOR_UNAVAILABLE = "sensor indisponível"
ERROR_COMMAND_FAILED = "falha ao executar comando"
ERROR_BACKEND_UNREACHABLE = "backend indisponível"
ERROR_INVALID_RESPONSE = "resposta inválida do backend"
