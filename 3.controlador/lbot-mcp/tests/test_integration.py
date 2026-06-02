import pytest
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.get_camera = AsyncMock(return_value="iVBORbase64test")
    backend.get_proximity = AsyncMock(return_value={"frente": 50.0, "tras": 200.0})
    backend.execute_lbml = AsyncMock(
        return_value={"accepted": True, "command": "D30F;", "status": "executado"}
    )
    backend.health_check = AsyncMock(return_value=True)
    return backend


@pytest.fixture
def setup_context(mock_backend):
    import mcp_server.context as ctx

    original = ctx.backend
    ctx.backend = mock_backend
    yield
    ctx.backend = original


class TestCameraTool:
    @pytest.mark.asyncio
    async def test_camera_returns_base64(self, setup_context, mock_backend):
        from mcp_server.tools.camera import camera

        result = await camera()
        assert "iVBOR" in result

    @pytest.mark.asyncio
    async def test_camera_backend_unavailable(self, mock_backend):
        import mcp_server.context as ctx

        mock_backend.get_camera = AsyncMock(side_effect=RuntimeError("camera indisponivel"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.camera import camera

            result = await camera()
            assert "Erro" in result
        finally:
            ctx.backend = original

    @pytest.mark.asyncio
    async def test_camera_timeout(self, mock_backend):
        import httpx
        import mcp_server.context as ctx

        mock_backend.get_camera = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.camera import camera

            result = await camera()
            assert "timeout" in result.lower()
        finally:
            ctx.backend = original


class TestProximityTool:
    @pytest.mark.asyncio
    async def test_proximity_returns_formatted_readings(self, setup_context, mock_backend):
        from mcp_server.tools.proximity import proximity

        result = await proximity()
        assert "Frente:" in result
        assert "Trás:" in result

    @pytest.mark.asyncio
    async def test_proximity_backend_unavailable(self, mock_backend):
        import mcp_server.context as ctx

        mock_backend.get_proximity = AsyncMock(side_effect=RuntimeError("sensor indisponivel"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.proximity import proximity

            result = await proximity()
            assert "Erro" in result
        finally:
            ctx.backend = original

    @pytest.mark.asyncio
    async def test_proximity_max_distance(self, setup_context, mock_backend):
        mock_backend.get_proximity = AsyncMock(return_value={"frente": 500, "tras": 500})

        from mcp_server.tools.proximity import proximity

        result = await proximity()
        assert "sem obstáculo" in result


class TestMoveTool:
    @pytest.mark.asyncio
    async def test_move_translates_and_executes(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "ande 30 centimetros para frente",
            "ande 30 cm frente",
            "D30F;",
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 30 centimetros para frente")
            assert "Comando executado" in result
            assert "D30F" in result

    @pytest.mark.asyncio
    async def test_move_invalid_input(self, setup_context, mock_backend):
        from mcp_server.translator import TranslationError
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.side_effect = TranslationError("nao entendi")

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("zzzzzz")
            assert "não entendi" in result

    @pytest.mark.asyncio
    async def test_move_execution_rejected(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "ande 40cm para frente",
            "ande 40 cm frente",
            "D40F;",
        )

        mock_backend.execute_lbml = AsyncMock(side_effect=RuntimeError("falha na execucao"))

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 40cm para frente")
            assert "Erro" in result

    @pytest.mark.asyncio
    async def test_move_invalid_lbml_from_translator(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "comando invalido",
            "comando invalido",
            "ERRO",
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("comando invalido")
            assert "não entendi" in result


class TestContextModule:
    def test_get_backend_raises_when_not_set(self):
        import mcp_server.context as ctx

        original = ctx.backend
        ctx.backend = None

        try:
            with pytest.raises(RuntimeError, match=r"Backend n.o configurado"):
                ctx.get_backend()
        finally:
            ctx.backend = original

    def test_get_backend_returns_backend(self, mock_backend):
        import mcp_server.context as ctx

        original = ctx.backend
        ctx.backend = mock_backend

        try:
            result = ctx.get_backend()
            assert result is mock_backend
        finally:
            ctx.backend = original
