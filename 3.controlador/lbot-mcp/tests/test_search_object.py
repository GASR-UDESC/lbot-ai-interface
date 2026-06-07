import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from mcp_server.tools.search_object import search_object


class TestSearchObjectValidation:
    @pytest.mark.asyncio
    async def test_empty_description(self):
        result = await search_object("")
        data = json.loads(result)
        assert data["status"] == "error"
        assert "vazia" in data["error"]

    @pytest.mark.asyncio
    async def test_none_description(self):
        result = await search_object(None)
        data = json.loads(result)
        assert data["status"] == "error"

    @pytest.mark.asyncio
    async def test_whitespace_only_description(self):
        result = await search_object("   ")
        data = json.loads(result)
        assert data["status"] == "error"


class TestSearchObjectErrors:
    @pytest.mark.asyncio
    async def test_backend_unavailable(self):
        with patch("mcp_server.tools.search_object.get_backend") as mock_get:
            mock_get.side_effect = RuntimeError("backend indisponivel")
            result = await search_object("cubo vermelho")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "backend" in data["error"]

    @pytest.mark.asyncio
    async def test_timeout_exception(self):
        mock_backend = AsyncMock()
        mock_backend.get_camera = AsyncMock()

        with patch("mcp_server.tools.search_object.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.search_object.SearchOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.side_effect = httpx.TimeoutException("timeout")
                mock_orch_cls.return_value = mock_orch

                result = await search_object("cubo vermelho")

        data = json.loads(result)
        assert data["status"] == "error"
        assert "timeout" in data["error"]

    @pytest.mark.asyncio
    async def test_generic_exception(self):
        mock_backend = AsyncMock()

        with patch("mcp_server.tools.search_object.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.search_object.SearchOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.side_effect = Exception("algo deu errado")
                mock_orch_cls.return_value = mock_orch

                result = await search_object("cubo vermelho")

        data = json.loads(result)
        assert data["status"] == "error"


class TestSearchObjectSuccess:
    @pytest.mark.asyncio
    async def test_found_result(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "found",
            "object_type": "cubo",
            "object_color": "vermelho",
            "bounding_box": (270, 190, 100, 100),
            "final_distance_cm": 45.0,
            "steps_taken": ["scan_frame_0", "detected_at_0deg", "centered_attempt_1", "approach_target_reached"],
            "elapsed_seconds": 3.5,
        }

        with patch("mcp_server.tools.search_object.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.search_object.SearchOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await search_object("cubo vermelho")

        data = json.loads(result)
        assert data["status"] == "found"
        assert data["object_type"] == "cubo"
        assert data["object_color"] == "vermelho"
        assert data["final_distance_cm"] == 45.0

    @pytest.mark.asyncio
    async def test_not_found_result(self):
        mock_backend = AsyncMock()
        expected_result = {
            "status": "not_found",
            "object_type": "cone",
            "object_color": "laranja",
            "bounding_box": None,
            "final_distance_cm": None,
            "steps_taken": ["scan_frame_0", "scan_frame_1", "scan_frame_2", "scan_frame_3"],
            "elapsed_seconds": 10.0,
        }

        with patch("mcp_server.tools.search_object.get_backend", return_value=mock_backend):
            with patch("mcp_server.tools.search_object.SearchOrchestrator") as mock_orch_cls:
                mock_orch = AsyncMock()
                mock_orch.run.return_value = expected_result
                mock_orch_cls.return_value = mock_orch

                result = await search_object("cone laranja")

        data = json.loads(result)
        assert data["status"] == "not_found"
        assert data["object_type"] == "cone"
