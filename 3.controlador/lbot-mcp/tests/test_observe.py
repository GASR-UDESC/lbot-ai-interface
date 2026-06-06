import json
import pytest
from unittest.mock import AsyncMock, MagicMock

import httpx


@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.get_camera = AsyncMock(return_value={
        "image": "iVBORw0KGgo=" + "A" * 200,
        "render_method": "2d",
        "robot_position": {"x": 1.0, "z": 2.0, "rotation": 90.0},
    })
    backend.get_proximity = AsyncMock(return_value={"frente": 50.0, "tras": 200.0})
    return backend


@pytest.fixture
def setup_context(mock_backend):
    import mcp_server.context as ctx

    original = ctx.backend
    ctx.backend = mock_backend
    yield
    ctx.backend = original


class TestObserveTool:
    @pytest.mark.asyncio
    async def test_observe_returns_camera_and_proximity(self, setup_context, mock_backend):
        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "image" in data
        assert "iVBOR" in data["image"]
        assert "proximity" in data
        assert data["proximity"]["frente"] == 50.0
        assert data["proximity"]["tras"] == 200.0
        assert data["render_method"] == "2d"
        assert data["robot_position"]["x"] == 1.0

    @pytest.mark.asyncio
    async def test_observe_camera_error_proximity_ok(self, setup_context, mock_backend):
        mock_backend.get_camera = AsyncMock(side_effect=RuntimeError("camera indisponivel"))

        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "camera_error" in data
        assert "camera indisponivel" in data["camera_error"]
        assert "proximity" in data
        assert data["proximity"]["frente"] == 50.0

    @pytest.mark.asyncio
    async def test_observe_proximity_error_camera_ok(self, setup_context, mock_backend):
        mock_backend.get_proximity = AsyncMock(side_effect=RuntimeError("sensor indisponivel"))

        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "image" in data
        assert "iVBOR" in data["image"]
        assert "proximity_error" in data
        assert "sensor indisponivel" in data["proximity_error"]

    @pytest.mark.asyncio
    async def test_observe_both_error(self, setup_context, mock_backend):
        mock_backend.get_camera = AsyncMock(side_effect=RuntimeError("camera fail"))
        mock_backend.get_proximity = AsyncMock(side_effect=RuntimeError("prox fail"))

        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "camera_error" in data
        assert "camera fail" in data["camera_error"]
        assert "proximity_error" in data
        assert "prox fail" in data["proximity_error"]

    @pytest.mark.asyncio
    async def test_observe_timeout_camera(self, setup_context, mock_backend):
        mock_backend.get_camera = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "camera_error" in data
        assert "proximity" in data
        assert data["proximity"]["frente"] == 50.0

    @pytest.mark.asyncio
    async def test_observe_timeout_proximity(self, setup_context, mock_backend):
        mock_backend.get_proximity = AsyncMock(side_effect=httpx.TimeoutException("timeout"))

        from mcp_server.tools.observe import observe

        result = await observe()
        data = json.loads(result)
        assert "image" in data
        assert "proximity_error" in data
