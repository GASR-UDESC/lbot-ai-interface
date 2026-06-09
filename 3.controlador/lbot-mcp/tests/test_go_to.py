import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_server.tools.go_to import go_to


class TestGoToValidation:
    @pytest.mark.asyncio
    async def test_empty_target(self):
        result = await go_to("")
        data = json.loads(result)
        assert data["status"] == "error"
        assert "vazio" in data["error"]

    @pytest.mark.asyncio
    async def test_none_target(self):
        result = await go_to(None)
        data = json.loads(result)
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_invalid_direction(self):
        result = await go_to("parede", direction="cima")
        data = json.loads(result)
        assert data["status"] == "error"
        assert "direcao invalida" in data["error"]

    @pytest.mark.asyncio
    async def test_none_direction_defaults_to_frente(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "found",
            "target": "parede",
            "direction": "frente",
            "final_distance_cm": 20.0,
            "steps_taken": ["llm_confirmed", "approach_wall_start"],
        }

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await go_to("parede", direction=None)

        data = json.loads(result)
        assert data["status"] == "found"


class TestGoToErrors:
    @pytest.mark.asyncio
    async def test_backend_unavailable(self):
        with patch("mcp_server.tools.go_to.get_backend") as mock_get:
            mock_get.side_effect = RuntimeError("backend indisponivel")
            result = await go_to("parede")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "backend" in data["error"]

    @pytest.mark.asyncio
    async def test_timeout_exception(self):
        mock_backend = AsyncMock()

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.side_effect = httpx.TimeoutException("timeout")
                mock_orch_cls.return_value = mock_orch

                result = await go_to("parede")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "timeout" in data["error"]

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        mock_backend = AsyncMock()

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.side_effect = Exception("algo deu errado")
                mock_orch_cls.return_value = mock_orch

                result = await go_to("cubo vermelho")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "algo deu errado" in data["error"]


class TestGoToSuccess:
    @pytest.mark.asyncio
    async def test_wall_found(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "found",
            "target": "parede",
            "direction": "frente",
            "final_distance_cm": 20.0,
            "steps_taken": ["llm_confirmed", "approach_wall_start", "sensor_read_200cm"],
        }

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await go_to("parede")

        data = json.loads(result)
        assert data["status"] == "found"
        assert data["target"] == "parede"
        assert data["final_distance_cm"] == 20.0

    @pytest.mark.asyncio
    async def test_object_found(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "found",
            "target": "cubo vermelho",
            "direction": "direita",
            "object_type": "cubo",
            "object_color": "vermelho",
            "bounding_box": (270, 190, 100, 100),
            "final_distance_cm": 45.0,
            "steps_taken": ["rotate_R90R", "llm_confirmed", "opencv_detected"],
        }

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await go_to("cubo vermelho", direction="direita")

        data = json.loads(result)
        assert data["status"] == "found"
        assert data["object_type"] == "cubo"
        assert data["object_color"] == "vermelho"
        assert data["final_distance_cm"] == 45.0

    @pytest.mark.asyncio
    async def test_not_found(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "not_found",
            "reason": "target not visible in direction",
            "target": "esfera azul",
            "direction": "frente",
            "steps_taken": ["llm_did_not_confirm"],
        }

        with patch("mcp_server.tools.go_to.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.go_to.GoToOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await go_to("esfera azul")

        data = json.loads(result)
        assert data["status"] == "not_found"
        assert data["reason"] == "target not visible in direction"
