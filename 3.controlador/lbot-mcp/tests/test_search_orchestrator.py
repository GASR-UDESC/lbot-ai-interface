import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from mcp_server.services.search_orchestrator import (
    CAMERA_TIMEOUT,
    CENTER_THRESHOLD_PX,
    LLM_FORWARD_STEP_CM,
    MAX_LLM_FORWARD_RESCANS,
    MAX_APPROACH_STEPS,
    MAX_RESCANS,
    MIN_SAFE_DISTANCE_CM,
    SearchOrchestrator,
    TARGET_DISTANCE_CM,
)


def _make_llm_response(text: str) -> AsyncMock:
    choice = AsyncMock()
    choice.message = AsyncMock()
    choice.message.content = text
    response = AsyncMock()
    response.choices = [choice]
    return response


def _make_detection(cx=320, cy=240, bbox=(270, 190, 100, 100)):
    return {
        "type": "cubo",
        "color": "vermelho",
        "bbox": bbox,
        "center": (cx, cy),
        "area": bbox[2] * bbox[3],
    }


@pytest.fixture
def orchestrator(mock_backend, mock_llm_client):
    return SearchOrchestrator(
        mock_backend, llm_client=mock_llm_client, llm_model="test-model",
    )


class TestScan:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch("mcp_server.services.search_orchestrator.asyncio.sleep"):
            yield
    @pytest.mark.asyncio
    async def test_llm_detects_and_cv_confirms(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=True,
        ), patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._scan("cubo", "vermelho")

        assert result is not None
        assert result["angle"] == 0
        assert result["object"]["type"] == "cubo"
        mock_backend.execute_lbml.assert_not_called()

    @pytest.mark.asyncio
    async def test_detects_after_rotation(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [False, False, True]

            with patch(
                "mcp_server.services.search_orchestrator.detect_object",
                return_value=_make_detection(),
            ):
                result = await orchestrator._scan("cubo", "vermelho")

        assert result is not None
        assert result["angle"] == 180

    @pytest.mark.asyncio
    async def test_llm_never_sees_object(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=False,
        ):
            result = await orchestrator._scan("cubo", "vermelho")

        assert result is None
        assert mock_backend.execute_lbml.call_count == 3

    @pytest.mark.asyncio
    async def test_llm_yes_cv_no_continues(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [True, True, True, True]

            with patch(
                "mcp_server.services.search_orchestrator.detect_object",
                return_value=None,
            ):
                result = await orchestrator._scan("cubo", "vermelho")

        assert result is None
        assert mock_backend.execute_lbml.call_count == 3

    @pytest.mark.asyncio
    async def test_camera_timeout_does_not_abort(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.side_effect = [
            asyncio.TimeoutError(),
            sample_camera_response,
            sample_camera_response,
        ]

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [False, True]

            with patch(
                "mcp_server.services.search_orchestrator.detect_object",
                return_value=_make_detection(),
            ):
                result = await orchestrator._scan("cubo", "vermelho")

        assert result is not None


class TestCenter:
    @pytest.mark.asyncio
    async def test_already_centered(self, orchestrator):
        result = await orchestrator._center((320, 240))
        assert result is True

    @pytest.mark.asyncio
    async def test_within_threshold(self, orchestrator):
        result = await orchestrator._center((340, 240))
        assert result is True

    @pytest.mark.asyncio
    async def test_converges(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response

        center_values = [(400, 240), (350, 240), (320, 240)]

        with patch(
            "mcp_server.services.search_orchestrator.detect_object"
        ) as mock_detect:
            mock_detect.side_effect = [
                _make_detection(cx=v[0], cy=v[1]) for v in center_values
            ]
            result = await orchestrator._center((400, 240))

        assert result is True

    @pytest.mark.asyncio
    async def test_max_attempts_exceeded(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.detect_object"
        ) as mock_detect:
            far_detection = _make_detection(cx=500, cy=240)
            mock_detect.return_value = far_detection
            result = await orchestrator._center((500, 240))

        assert result is False

    @pytest.mark.asyncio
    async def test_loses_tracking(self, orchestrator, mock_backend):
        mock_backend.get_camera.return_value = {
            "image": "dummy",
            "render_method": "webgl",
            "robot_position": None,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object"
        ) as mock_detect:
            mock_detect.side_effect = [None]
            result = await orchestrator._center((400, 240))

        assert result is False


class TestApproach:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch("mcp_server.services.search_orchestrator.asyncio.sleep") as mock_sleep:
            self._mock_sleep = mock_sleep
            yield

    @pytest.mark.asyncio
    async def test_adaptive_step(self, orchestrator, mock_backend):
        mock_backend.get_proximity_sensor.return_value = {
            "frente": 80, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        cmd = mock_backend.execute_lbml.call_args[0][0]
        assert "D" in cmd
        assert "F;" in cmd
        step = int(cmd.replace("D", "").replace("F;", ""))
        assert step <= 50

    @pytest.mark.asyncio
    async def test_reaches_target(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": TARGET_DISTANCE_CM, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "found"

    @pytest.mark.asyncio
    async def test_obstacle_too_close(self, orchestrator, mock_backend):
        mock_backend.get_proximity_sensor.return_value = {
            "frente": MIN_SAFE_DISTANCE_CM - 5, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "not_found"
        assert "too close" in result["reason"]

    @pytest.mark.asyncio
    async def test_object_too_far(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": 401, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "not_found"
        assert "too far" in result["reason"]

    @pytest.mark.asyncio
    async def test_rescan_success(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.side_effect = [
            {"frente": 300, "tras": 400},
            {"frente": TARGET_DISTANCE_CM, "tras": 400},
        ]

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [False, False, True]
            with patch(
                "mcp_server.services.search_orchestrator.detect_object"
            ) as mock_detect:
                mock_detect.side_effect = [None, _make_detection()]
                result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "found"

    @pytest.mark.asyncio
    async def test_rescan_failure(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": 300, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=False,
        ), patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=None,
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "not_found"

    @pytest.mark.asyncio
    async def test_max_steps_exceeded(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": 300, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator._approach("cubo", "vermelho")

        assert result["status"] == "not_found"
        assert "max approach steps" in result["reason"]


class TestRunFullFlow:

    @pytest.fixture(autouse=True)
    def _patch_sleep(self):
        with patch("mcp_server.services.search_orchestrator.asyncio.sleep"):
            yield

    @pytest.mark.asyncio
    async def test_full_flow_found(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": TARGET_DISTANCE_CM, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=True,
        ), patch(
            "mcp_server.services.search_orchestrator.detect_object",
            return_value=_make_detection(),
        ):
            result = await orchestrator.run("cubo vermelho")

        assert result["status"] == "found"
        assert result["object_type"] == "cubo"
        assert result["object_color"] == "vermelho"
        assert result["bounding_box"] is not None
        assert "steps_taken" in result

    @pytest.mark.asyncio
    async def test_full_flow_not_found(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=False,
        ):
            result = await orchestrator.run("cubo vermelho")

        assert result["status"] == "not_found"
        assert result["bounding_box"] is None

    @pytest.mark.asyncio
    async def test_llm_spotted_forward_rescan_finds(
        self, orchestrator, mock_backend, sample_camera_response,
    ):
        mock_backend.get_camera.return_value = sample_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": TARGET_DISTANCE_CM, "tras": 400,
        }

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible",
            return_value=True,
        ):
            with patch(
                "mcp_server.services.search_orchestrator.detect_object"
            ) as mock_detect:
                mock_detect.side_effect = [
                    None, None, None, None,
                    _make_detection(),
                ]
                result = await orchestrator.run("cubo vermelho")

        assert result["status"] == "found"
        assert "llm_forward_rescan_1" in orchestrator._steps_taken
        mock_backend.execute_lbml.assert_any_call(f"D{LLM_FORWARD_STEP_CM}F;")

    @pytest.mark.asyncio
    async def test_llm_spotted_forward_rescan_exhausted(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response
        mock_backend.get_proximity_sensor.return_value = {
            "frente": 400, "tras": 400,
        }

        first_scan_calls = 4
        forwards = MAX_LLM_FORWARD_RESCANS
        total_calls = first_scan_calls * (1 + forwards)

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [True] * total_calls

            with patch(
                "mcp_server.services.search_orchestrator.detect_object",
                return_value=None,
            ):
                result = await orchestrator.run("cubo vermelho")

        assert result["status"] == "not_found"
        forward_calls = [
            call_args[0][0]
            for call_args in mock_backend.execute_lbml.call_args_list
            if str(call_args[0][0]).startswith("D")
        ]
        assert len(forward_calls) == MAX_LLM_FORWARD_RESCANS

    @pytest.mark.asyncio
    async def test_llm_spotted_once_then_disappears(
        self, orchestrator, mock_backend, empty_camera_response,
    ):
        mock_backend.get_camera.return_value = empty_camera_response

        with patch(
            "mcp_server.services.search_orchestrator.ask_llm_if_object_visible"
        ) as mock_llm:
            mock_llm.side_effect = [True] * 4 + [False] * 4

            with patch(
                "mcp_server.services.search_orchestrator.detect_object",
                return_value=None,
            ):
                result = await orchestrator.run("cubo vermelho")

        assert result["status"] == "not_found"
        forward_calls = [
            call_args[0][0]
            for call_args in mock_backend.execute_lbml.call_args_list
            if str(call_args[0][0]).startswith("D")
        ]
        assert len(forward_calls) == 1
