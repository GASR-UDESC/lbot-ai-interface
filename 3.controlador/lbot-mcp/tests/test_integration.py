import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.get_camera = AsyncMock(return_value={
        "image": "iVBORbase64test", "render_method": "2d",
        "robot_position": {"x": 0, "z": 0, "rotation": 0},
        "observation_mode": "topdown_simplified",
        "warning": "camera simplificada",
    })
    backend.get_proximity = AsyncMock(return_value={
        "front_cm": 50.0,
        "rear_cm": 200.0,
        "safe_to_move_forward": True,
        "safe_to_move_backward": True,
        "minimum_safe_distance_cm": 20,
        "robot_position": {"x": 0, "z": 0, "rotation": 0},
    })
    backend.execute_lbml = AsyncMock(
        return_value={
            "accepted": True,
            "command": "D30F;",
            "status": "completed",
            "completed": True,
            "final_state": {"x": 30, "z": 0, "rotation": 0},
            "message": "Sequencia executada com sucesso.",
        }
    )
    backend.get_state = AsyncMock(return_value={"x": 0, "z": 0, "rotation": 0})
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
        import json

        result = await camera()
        data = json.loads(result)
        assert "image" in data
        assert "iVBOR" in data["image"]

    @pytest.mark.asyncio
    async def test_camera_backend_unavailable(self, mock_backend):
        import json
        import mcp_server.context as ctx

        mock_backend.get_camera = AsyncMock(side_effect=RuntimeError("camera indisponivel"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.camera import camera

            result = await camera()
            data = json.loads(result)
            assert "error" in data
        finally:
            ctx.backend = original

    @pytest.mark.asyncio
    async def test_camera_timeout(self, mock_backend):
        import json
        import httpx
        import mcp_server.context as ctx

        mock_backend.get_camera = AsyncMock(side_effect=httpx.TimeoutException("timeout"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.camera import camera

            result = await camera()
            data = json.loads(result)
            assert "timeout" in data["error"].lower()
        finally:
            ctx.backend = original


class TestProximityTool:
    @pytest.mark.asyncio
    async def test_proximity_returns_formatted_readings(self, setup_context, mock_backend):
        from mcp_server.tools.proximity import proximity

        result = await proximity()
        data = json.loads(result)
        assert data["front_cm"] == 50.0
        assert data["rear_cm"] == 200.0
        assert data["safe_to_move_forward"] is True

    @pytest.mark.asyncio
    async def test_proximity_backend_unavailable(self, mock_backend):
        import mcp_server.context as ctx

        mock_backend.get_proximity = AsyncMock(side_effect=RuntimeError("sensor indisponivel"))
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.proximity import proximity

            result = await proximity()
            data = json.loads(result)
            assert "error" in data
        finally:
            ctx.backend = original

    @pytest.mark.asyncio
    async def test_proximity_max_distance(self, setup_context, mock_backend):
        mock_backend.get_proximity = AsyncMock(return_value={
            "front_cm": 500,
            "rear_cm": 500,
            "safe_to_move_forward": True,
            "safe_to_move_backward": True,
            "minimum_safe_distance_cm": 20,
            "robot_position": None,
        })

        from mcp_server.tools.proximity import proximity

        result = await proximity()
        data = json.loads(result)
        assert data["front_cm"] == 500
        assert data["rear_cm"] == 500


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
            data = json.loads(result)
            assert data["accepted"] is True
            assert data["translated_lbml"] == "D30F;"
            assert data["executed_lbml_steps"] == ["D30F;"]
            assert data["status"] == "completed"
            mock_backend.get_proximity.assert_awaited_once()
            mock_backend.execute_lbml.assert_awaited_once_with("D30F;")

    @pytest.mark.asyncio
    async def test_move_blocks_when_forward_step_is_not_safe(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "ande 40 centimetros para frente",
            "ande 40 cm frente",
            "D40F;",
        )

        mock_backend.get_proximity = AsyncMock(
            return_value={
                "front_cm": 45.0,
                "rear_cm": 200.0,
                "safe_to_move_forward": True,
                "safe_to_move_backward": True,
                "minimum_safe_distance_cm": 20,
                "robot_position": {"x": 0, "z": 0, "rotation": 0},
            }
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 40 centimetros para frente")
            data = json.loads(result)
            assert data["accepted"] is False
            assert data["completed"] is False
            assert data["status"] == "blocked_by_proximity"
            assert data["blocked_lbml_step"] == "D40F;"
            assert data["executed_lbml_steps"] == []
            assert data["proximity"]["max_safe_travel_cm"] == 25.0
            mock_backend.execute_lbml.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_move_rotates_then_blocks_implicit_right_step_when_sensor_is_not_safe(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "ande 30 centimetros para direita",
            "ande 30 cm direita",
            "D30R;",
        )

        mock_backend.get_proximity = AsyncMock(
            return_value={
                "front_cm": 35.0,
                "rear_cm": 200.0,
                "safe_to_move_forward": True,
                "safe_to_move_backward": True,
                "minimum_safe_distance_cm": 20,
                "robot_position": {"x": 0, "z": 0, "rotation": -90},
            }
        )
        mock_backend.execute_lbml = AsyncMock(
            side_effect=[
                {
                    "accepted": True,
                    "command": "R90R;",
                    "status": "completed",
                    "completed": True,
                    "request_id": "req-1",
                    "target_client_id": "sim-123",
                    "final_state": {"x": 0, "z": 0, "rotation": -90},
                    "message": "Rotacao executada com sucesso.",
                }
            ]
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 30 centimetros para direita")
            data = json.loads(result)
            assert data["accepted"] is True
            assert data["completed"] is False
            assert data["status"] == "blocked_by_proximity"
            assert data["blocked_lbml_step"] == "D30F;"
            assert data["executed_lbml_steps"] == ["R90R;"]
            assert data["final_state"] == {"x": 0, "z": 0, "rotation": -90}
            assert mock_backend.execute_lbml.await_args_list[0].args == ("R90R;",)

    @pytest.mark.asyncio
    async def test_move_executes_sequence_step_by_step_with_prechecks(self, setup_context, mock_backend):
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.return_value = (
            "ande 30 centimetros para frente e depois 20 para tras",
            "ande 30 cm frente e 20 cm tras",
            "D30F;D20B;",
        )

        mock_backend.get_proximity = AsyncMock(
            side_effect=[
                {
                    "front_cm": 60.0,
                    "rear_cm": 200.0,
                    "safe_to_move_forward": True,
                    "safe_to_move_backward": True,
                    "minimum_safe_distance_cm": 20,
                    "robot_position": {"x": 0, "z": 0, "rotation": 0},
                },
                {
                    "front_cm": 200.0,
                    "rear_cm": 60.0,
                    "safe_to_move_forward": True,
                    "safe_to_move_backward": True,
                    "minimum_safe_distance_cm": 20,
                    "robot_position": {"x": 0, "z": 30, "rotation": 0},
                },
            ]
        )
        mock_backend.execute_lbml = AsyncMock(
            side_effect=[
                {
                    "accepted": True,
                    "command": "D30F;",
                    "status": "completed",
                    "completed": True,
                    "request_id": "req-1",
                    "target_client_id": "sim-123",
                    "final_state": {"x": 0, "z": 30, "rotation": 0},
                    "message": "Primeiro movimento concluido.",
                },
                {
                    "accepted": True,
                    "command": "D20B;",
                    "status": "completed",
                    "completed": True,
                    "request_id": "req-2",
                    "target_client_id": "sim-123",
                    "final_state": {"x": 0, "z": 10, "rotation": 0},
                    "message": "Segundo movimento concluido.",
                },
            ]
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 30 centimetros para frente e depois 20 para tras")
            data = json.loads(result)
            assert data["accepted"] is True
            assert data["completed"] is True
            assert data["status"] == "completed"
            assert data["executed_lbml_steps"] == ["D30F;", "D20B;"]
            assert data["final_state"] == {"x": 0, "z": 10, "rotation": 0}
            assert mock_backend.get_proximity.await_count == 2
            assert [call.args[0] for call in mock_backend.execute_lbml.await_args_list] == ["D30F;", "D20B;"]

    @pytest.mark.asyncio
    async def test_move_invalid_input(self, setup_context, mock_backend):
        from mcp_server.translator import TranslationError
        from unittest.mock import MagicMock

        mock_translator = MagicMock()
        mock_translator.translate_verbose.side_effect = TranslationError("nao entendi")

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("zzzzzz")
            data = json.loads(result)
            assert "não entendi" in data["error"]

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
        mock_backend.get_proximity = AsyncMock(
            return_value={
                "front_cm": 80.0,
                "rear_cm": 200.0,
                "safe_to_move_forward": True,
                "safe_to_move_backward": True,
                "minimum_safe_distance_cm": 20,
                "robot_position": {"x": 0, "z": 0, "rotation": 0},
            }
        )

        with patch("mcp_server.tools.movement.get_translator", return_value=mock_translator):
            from mcp_server.tools.movement import move

            result = await move("ande 40cm para frente")
            data = json.loads(result)
            assert data["status"] == "execution_error"
            assert "falha na execução" in data["error"]

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
            data = json.loads(result)
            assert "não entendi" in data["error"]


class TestStateTool:
    @pytest.mark.asyncio
    async def test_state_returns_backend_state(self, setup_context, mock_backend):
        from mcp_server.tools.state import state

        result = await state()
        data = json.loads(result)
        assert data["x"] == 0
        assert data["z"] == 0

    @pytest.mark.asyncio
    async def test_state_handles_missing_state(self, mock_backend):
        import mcp_server.context as ctx

        mock_backend.get_state = AsyncMock(return_value=None)
        original = ctx.backend
        ctx.backend = mock_backend

        try:
            from mcp_server.tools.state import state

            result = await state()
            data = json.loads(result)
            assert data["error"] == "estado indisponivel"
        finally:
            ctx.backend = original


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
