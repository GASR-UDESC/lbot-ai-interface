import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from mcp_server.backends.base import (
    LBotBackend,
    ERROR_CAMERA_UNAVAILABLE,
    ERROR_SENSOR_UNAVAILABLE,
    ERROR_COMMAND_FAILED,
)
from mcp_server.backends.simulator import SimulatorBackend


class TestLBotBackendAbstract:
    def test_cannot_instantiate_abstract(self):
        with pytest.raises(TypeError):
            LBotBackend()

    def test_concrete_subclass_requires_all_methods(self):
        class Incomplete(LBotBackend):
            pass

        with pytest.raises(TypeError):
            Incomplete()


def _mock_async_client(backend, get_return=None, post_return=None, get_side_effect=None, post_side_effect=None):
    mock_client = AsyncMock()
    if get_return is not None:
        mock_client.get.return_value = get_return
    if post_return is not None:
        mock_client.post.return_value = post_return
    if get_side_effect is not None:
        mock_client.get.side_effect = get_side_effect
    if post_side_effect is not None:
        mock_client.post.side_effect = post_side_effect
    mock_client.aclose = AsyncMock()
    object.__setattr__(backend, "_client", mock_client)
    return mock_client


def _make_response(status_code=200, json_data=None, raise_for_status=None):
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.raise_for_status = raise_for_status or MagicMock()
    return resp


class TestSimulatorBackend:
    BASE_URL = "http://localhost:3001"

    @pytest.fixture
    def backend(self):
        b = SimulatorBackend(base_url=self.BASE_URL)
        yield b
        object.__setattr__(b, "_client", None)

    @pytest.mark.asyncio
    async def test_health_check_online(self, backend):
        resp = _make_response(200)
        _mock_async_client(backend, get_return=resp)
        result = await backend.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_offline(self, backend):
        import httpx

        _mock_async_client(backend, get_side_effect=httpx.ConnectError("Connection refused"))
        result = await backend.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_get_camera_returns_base64(self, backend):
        resp = _make_response(json_data={"connected": True, "image": "iVBORbase64fake"})
        _mock_async_client(backend, get_return=resp)
        result = await backend.get_camera()
        assert result == {"image": "iVBORbase64fake", "render_method": "unknown", "robot_position": None}

    @pytest.mark.asyncio
    async def test_get_camera_unavailable(self, backend):
        resp = _make_response(json_data={"connected": False, "image": None, "error": "camera indisponivel"})
        _mock_async_client(backend, get_return=resp)
        with pytest.raises(RuntimeError, match="camera indisponivel"):
            await backend.get_camera()

    @pytest.mark.asyncio
    async def test_get_camera_connection_error(self, backend):
        import httpx

        _mock_async_client(backend, get_side_effect=httpx.ConnectError("refused"))
        with pytest.raises(RuntimeError):
            await backend.get_camera()

    @pytest.mark.asyncio
    async def test_get_proximity_returns_readings(self, backend):
        resp = _make_response(json_data={"connected": True, "readings": {"frente": 50.0, "tras": 200.0}})
        _mock_async_client(backend, get_return=resp)
        result = await backend.get_proximity()
        assert result == {"frente": 50.0, "tras": 200.0}

    @pytest.mark.asyncio
    async def test_get_proximity_unavailable(self, backend):
        resp = _make_response(json_data={"connected": False, "readings": None, "error": ERROR_SENSOR_UNAVAILABLE})
        _mock_async_client(backend, get_return=resp)
        with pytest.raises(RuntimeError, match=ERROR_SENSOR_UNAVAILABLE):
            await backend.get_proximity()

    @pytest.mark.asyncio
    async def test_execute_lbml_accepted(self, backend):
        resp = _make_response(json_data={
            "accepted": True, "command": "D40F;", "targetClientId": "sim-123",
        })
        _mock_async_client(backend, post_return=resp)
        result = await backend.execute_lbml("D40F;")
        assert result["accepted"] is True
        assert result["command"] == "D40F;"
        assert result["status"] == "executado"

    @pytest.mark.asyncio
    async def test_execute_lbml_rejected_409(self, backend):
        import httpx

        error_resp = MagicMock()
        error_resp.status_code = 409
        _mock_async_client(
            backend,
            post_side_effect=httpx.HTTPStatusError("409 Conflict", request=MagicMock(), response=error_resp),
        )
        with pytest.raises(RuntimeError, match=ERROR_COMMAND_FAILED):
            await backend.execute_lbml("D40F;")

    @pytest.mark.asyncio
    async def test_execute_lbml_not_accepted(self, backend):
        resp = _make_response(json_data={"accepted": False, "error": "Comando invalido"})
        _mock_async_client(backend, post_return=resp)
        with pytest.raises(RuntimeError, match="Comando invalido"):
            await backend.execute_lbml("INVALID")

    @pytest.mark.asyncio
    async def test_get_state_returns_dict(self, backend):
        resp = _make_response(json_data={
            "connected": True, "activeClientId": "sim-123",
            "state": {"x": 100, "z": 50, "rotation": 0},
        })
        _mock_async_client(backend, get_return=resp)
        result = await backend.get_state()
        assert result == {"x": 100, "z": 50, "rotation": 0}

    @pytest.mark.asyncio
    async def test_get_state_null(self, backend):
        resp = _make_response(json_data={"connected": False, "activeClientId": None, "state": None})
        _mock_async_client(backend, get_return=resp)
        result = await backend.get_state()
        assert result is None

    @pytest.mark.asyncio
    async def test_get_state_connection_error(self, backend):
        import httpx

        _mock_async_client(backend, get_side_effect=httpx.ConnectError("refused"))
        result = await backend.get_state()
        assert result is None

    @pytest.mark.asyncio
    async def test_close_client(self, backend):
        mock_client = _mock_async_client(backend)
        await backend.close()
        mock_client.aclose.assert_called_once()
