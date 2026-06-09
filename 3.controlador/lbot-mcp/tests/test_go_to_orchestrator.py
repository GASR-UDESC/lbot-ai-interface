import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.services.go_to_orchestrator import (
    GoToOrchestrator,
    DIRECTION_ANGLES,
    FRAME_WIDTH,
    CAMERA_TIMEOUT,
    MOVE_DELAY_SECONDS,
)

from tests.conftest import (
    _encode_frame,
    _make_frame_with_rect,
    _make_frame_with_circle,
    _make_solid_frame,
    RED_BGR,
)


VISIBLE_PATCH = "mcp_server.services.go_to_orchestrator.ask_llm_if_object_visible"
DETECTOR_PATCH = "mcp_server.services.go_to_orchestrator.detect_object"
SLEEP_PATCH = "mcp_server.services.go_to_orchestrator.asyncio.sleep"


def _mock_camera_response(frame_base64: str) -> dict:
    return {
        "image": frame_base64,
        "render_method": "webgl",
        "robot_position": {"x": 0, "z": 0, "angle": 0},
    }


def _make_detection(cx=320, cy=240, bbox=(270, 190, 100, 100)):
    return {
        "type": "cubo",
        "color": "vermelho",
        "bbox": bbox,
        "center": (cx, cy),
        "area": bbox[2] * bbox[3],
    }


def _make_orchestrator(backend: AsyncMock, llm_client: AsyncMock):
    return GoToOrchestrator(backend, llm_client=llm_client, llm_model="test-model")


class TestDirectionParsing:
    def test_valid_directions(self):
        assert "frente" in DIRECTION_ANGLES
        assert "esquerda" in DIRECTION_ANGLES
        assert "direita" in DIRECTION_ANGLES
        assert "tras" in DIRECTION_ANGLES
        assert DIRECTION_ANGLES["frente"] == 0
        assert DIRECTION_ANGLES["esquerda"] == -90
        assert DIRECTION_ANGLES["direita"] == 90
        assert DIRECTION_ANGLES["tras"] == 180


class TestValidation:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch(SLEEP_PATCH):
            yield

    @pytest.mark.asyncio
    async def test_invalid_direction(self, mock_backend, mock_llm_client):
        orch = _make_orchestrator(mock_backend, mock_llm_client)
        result = await orch.run("parede", "cima")
        assert result["status"] == "error"
        assert "direcao invalida" in result["error"]

    @pytest.mark.asyncio
    async def test_empty_target(self, mock_backend, mock_llm_client):
        orch = _make_orchestrator(mock_backend, mock_llm_client)
        result = await orch.run("  ", "frente")
        assert result["status"] == "error"
        assert "vazio" in result["error"]

    @pytest.mark.asyncio
    async def test_unknown_target(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        result = await orch.run("abacaxi", "frente")
        assert result["status"] == "error"
        assert "nao reconhecido" in result["error"]


class TestWallGoTo:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch(SLEEP_PATCH):
            yield

    @pytest.mark.asyncio
    async def test_wall_in_front(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 200.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("parede", "frente")

        assert result["status"] == "found"
        assert result["target"] == "parede"

    @pytest.mark.asyncio
    async def test_wall_to_left(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 150.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("parede", "esquerda")

        assert result["status"] == "found"
        lbml_calls = [call[0][0] for call in mock_backend.execute_lbml.call_args_list]
        assert any("R90L" in c for c in lbml_calls)

    @pytest.mark.asyncio
    async def test_wall_to_right(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 100.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("muro", "direita")

        assert result["status"] == "found"
        lbml_calls = [call[0][0] for call in mock_backend.execute_lbml.call_args_list]
        assert any("R90R" in c for c in lbml_calls)

    @pytest.mark.asyncio
    async def test_wall_to_back(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 80.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("parede", "tras")

        assert result["status"] == "found"
        lbml_calls = [call[0][0] for call in mock_backend.execute_lbml.call_args_list]
        assert any("R180R" in c for c in lbml_calls)

    @pytest.mark.asyncio
    async def test_wall_already_close(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 15.0, "tras": 400.0}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("parede", "frente")

        assert result["status"] == "found"
        assert result["final_distance_cm"] == 15.0

    @pytest.mark.asyncio
    async def test_wall_sensor_no_obstacle(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 400.0, "tras": 400.0}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True):
            result = await orch.run("parede", "frente")

        assert result["status"] == "not_found"
        assert result["reason"] == "no obstacle detected"

    @pytest.mark.asyncio
    async def test_wall_llm_says_no(self, mock_backend, mock_llm_client):
        frame = _make_solid_frame(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=False):
            result = await orch.run("parede", "frente")

        assert result["status"] == "not_found"
        assert result["reason"] == "target not visible in direction"


class TestObjectGoTo:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch(SLEEP_PATCH):
            yield

    @pytest.mark.asyncio
    async def test_sphere_to_front(self, mock_backend, mock_llm_client):
        frame = _make_frame_with_circle(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 45.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, return_value=_make_detection()
        ):
            result = await orch.run("esfera azul", "frente")

        assert result["status"] == "found"
        assert result["object_type"] == "esfera"
        assert result["object_color"] == "azul"

    @pytest.mark.asyncio
    async def test_cube_to_right(self, mock_backend, mock_llm_client):
        frame = _make_frame_with_rect(RED_BGR, x=270, y=190, w=100, h=100)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 48.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, return_value=_make_detection()
        ):
            result = await orch.run("cubo vermelho", "direita")

        assert result["status"] == "found"
        lbml_calls = [call[0][0] for call in mock_backend.execute_lbml.call_args_list]
        assert any("R90R" in c for c in lbml_calls)

    @pytest.mark.asyncio
    async def test_object_llm_says_no(self, mock_backend, mock_llm_client):
        frame = _make_frame_with_circle(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=False):
            result = await orch.run("esfera", "frente")

        assert result["status"] == "not_found"
        assert result["reason"] == "target not visible in direction"

    @pytest.mark.asyncio
    async def test_object_llm_yes_opencv_no_match(self, mock_backend, mock_llm_client):
        empty_frame = _make_solid_frame((128, 128, 128))
        frame_b64 = _encode_frame(empty_frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, return_value=None
        ):
            result = await orch.run("cubo vermelho", "frente")

        assert result["status"] == "not_found"
        assert "LLM confirmed but OpenCV could not detect" in result.get("reason", "")

    @pytest.mark.asyncio
    async def test_object_center_needs_multiple_attempts(self, mock_backend, mock_llm_client):
        off_center_frame = _make_frame_with_rect(RED_BGR, x=100, y=190, w=100, h=100)

        mock_backend.get_camera.return_value = _mock_camera_response(
            _encode_frame(off_center_frame)
        )
        mock_backend.get_proximity_sensor.return_value = {"frente": 45.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        off_center = _make_detection(cx=150, cy=240)
        centered = _make_detection(cx=320, cy=240)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, side_effect=[off_center, centered, centered]
        ):
            result = await orch.run("cubo vermelho", "frente")

        assert result["status"] == "found"

    @pytest.mark.asyncio
    async def test_object_approach_with_steps(self, mock_backend, mock_llm_client):
        frame = _make_frame_with_circle(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.execute_lbml.return_value = {"accepted": True}

        sensor_values = [120.0, 80.0, 45.0]
        call_count = [0]

        async def sensor_side_effect():
            idx = min(call_count[0], len(sensor_values) - 1)
            call_count[0] += 1
            return {"frente": sensor_values[idx], "tras": 400.0}

        mock_backend.get_proximity_sensor = AsyncMock(side_effect=sensor_side_effect)

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, return_value=_make_detection()
        ):
            result = await orch.run("esfera vermelha", "frente")

        assert result["status"] == "found"

    @pytest.mark.asyncio
    async def test_object_approach_obstacle_too_close(self, mock_backend, mock_llm_client):
        frame = _make_frame_with_rect(RED_BGR)
        frame_b64 = _encode_frame(frame)
        mock_backend.get_camera.return_value = _mock_camera_response(frame_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 15.0, "tras": 400.0}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, return_value=_make_detection()
        ):
            result = await orch.run("cubo vermelho", "frente")

        assert result["status"] == "not_found"
        assert result["reason"] == "obstacle too close"

    @pytest.mark.asyncio
    async def test_object_lost_tracking_during_approach(self, mock_backend, mock_llm_client):
        frame_with_circle = _make_frame_with_circle(RED_BGR)
        circle_b64 = _encode_frame(frame_with_circle)
        empty_frame = _make_solid_frame((128, 128, 128))

        mock_backend.get_camera.return_value = _mock_camera_response(circle_b64)
        mock_backend.get_proximity_sensor.return_value = {"frente": 80.0, "tras": 400.0}
        mock_backend.execute_lbml.return_value = {"accepted": True}

        orch = _make_orchestrator(mock_backend, mock_llm_client)
        detection = _make_detection()

        def detector_side_effect(*args, **kwargs):
            return detection

        def detector_lost_side_effect(*args, **kwargs):
            return None

        with patch(VISIBLE_PATCH, return_value=True), patch(
            DETECTOR_PATCH, side_effect=[detection, detection, None]
        ):
            result = await orch.run("esfera vermelha", "frente")

        assert result["status"] == "not_found"
        assert "lost tracking" in result.get("reason", "")
