import base64
from unittest.mock import AsyncMock

import cv2
import numpy as np
import pytest

FRAME_WIDTH = 640
FRAME_HEIGHT = 480


def _encode_frame(frame: np.ndarray) -> str:
    _, buffer = cv2.imencode(".png", frame)
    return base64.b64encode(buffer).decode("utf-8")


def _make_solid_frame(color_bgr: tuple[int, int, int]) -> np.ndarray:
    return np.full((FRAME_HEIGHT, FRAME_WIDTH, 3), color_bgr, dtype=np.uint8)


def _make_frame_with_rect(
    color_bgr: tuple[int, int, int], x: int = 270, y: int = 190, w: int = 100, h: int = 100
) -> np.ndarray:
    frame = _make_solid_frame((128, 128, 128))
    cv2.rectangle(frame, (x, y), (x + w, y + h), color_bgr, -1)
    return frame


def _make_frame_with_circle(
    color_bgr: tuple[int, int, int], cx: int = 320, cy: int = 240, r: int = 50
) -> np.ndarray:
    frame = _make_solid_frame((128, 128, 128))
    cv2.circle(frame, (cx, cy), r, color_bgr, -1)
    return frame


def _make_frame_with_triangle(color_bgr: tuple[int, int, int]) -> np.ndarray:
    frame = _make_solid_frame((128, 128, 128))
    pts = np.array([[270, 290], [370, 290], [320, 190]], dtype=np.int32)
    cv2.fillPoly(frame, [pts], color_bgr)
    return frame


RED_BGR = (0, 0, 255)
ORANGE_BGR = (0, 165, 255)
GREEN_BGR = (0, 255, 0)


@pytest.fixture
def sample_frame_base64() -> str:
    frame = _make_frame_with_rect(RED_BGR)
    return _encode_frame(frame)


@pytest.fixture
def empty_frame_base64() -> str:
    frame = _make_solid_frame((128, 128, 128))
    return _encode_frame(frame)


@pytest.fixture
def sphere_frame_base64() -> str:
    frame = _make_frame_with_circle(RED_BGR)
    return _encode_frame(frame)


@pytest.fixture
def cone_frame_base64() -> str:
    frame = _make_frame_with_triangle(ORANGE_BGR)
    return _encode_frame(frame)


@pytest.fixture
def sample_frame() -> np.ndarray:
    return _make_frame_with_rect(RED_BGR)


@pytest.fixture
def sphere_frame() -> np.ndarray:
    return _make_frame_with_circle(RED_BGR)


@pytest.fixture
def cone_frame() -> np.ndarray:
    return _make_frame_with_triangle(ORANGE_BGR)


@pytest.fixture
def empty_frame() -> np.ndarray:
    return _make_solid_frame((128, 128, 128))


@pytest.fixture
def two_cubes_frame() -> np.ndarray:
    frame = _make_solid_frame((128, 128, 128))
    cv2.rectangle(frame, (100, 100), (200, 200), RED_BGR, -1)
    cv2.rectangle(frame, (350, 200), (500, 400), RED_BGR, -1)
    return frame


@pytest.fixture
def sample_camera_response(sample_frame_base64: str) -> dict:
    return {
        "image": sample_frame_base64,
        "render_method": "webgl",
        "robot_position": {"x": 0, "z": 0, "angle": 0},
    }


@pytest.fixture
def empty_camera_response(empty_frame_base64: str) -> dict:
    return {
        "image": empty_frame_base64,
        "render_method": "webgl",
        "robot_position": {"x": 0, "z": 0, "angle": 0},
    }


@pytest.fixture
def mock_backend() -> AsyncMock:
    backend = AsyncMock()
    backend.get_camera = AsyncMock()
    backend.get_proximity_sensor = AsyncMock()
    backend.execute_lbml = AsyncMock()
    backend.get_proximity = AsyncMock()
    return backend


def _make_llm_response(text: str) -> AsyncMock:
    choice = AsyncMock()
    choice.message = AsyncMock()
    choice.message.content = text
    response = AsyncMock()
    response.choices = [choice]
    return response


@pytest.fixture
def mock_llm_client() -> AsyncMock:
    llm = AsyncMock()
    llm.chat = AsyncMock()
    llm.chat.completions = AsyncMock()
    llm.chat.completions.create = AsyncMock()
    return llm


@pytest.fixture
def mock_llm_yes(mock_llm_client: AsyncMock) -> AsyncMock:
    mock_llm_client.chat.completions.create.return_value = _make_llm_response("SIM")
    return mock_llm_client


@pytest.fixture
def mock_llm_no(mock_llm_client: AsyncMock) -> AsyncMock:
    mock_llm_client.chat.completions.create.return_value = _make_llm_response("NAO")
    return mock_llm_client


@pytest.fixture
def orchestrator_fixture(mock_backend: AsyncMock, mock_llm_client: AsyncMock):
    return _make_orchestrator(mock_backend, mock_llm_client)


def _make_orchestrator(backend: AsyncMock, llm_client: AsyncMock):
    from mcp_server.services.search_orchestrator import SearchOrchestrator
    return SearchOrchestrator(backend, llm_client=llm_client, llm_model="test-model")
