import base64

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
    color_bgr: tuple[int, int, int],
    x: int = 270,
    y: int = 190,
    w: int = 100,
    h: int = 100,
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
