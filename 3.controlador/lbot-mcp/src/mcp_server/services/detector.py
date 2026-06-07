import base64
import re

import cv2
import numpy as np

FRAME_WIDTH = 640
FRAME_HEIGHT = 480

COLOR_RANGES: dict[str, tuple[np.ndarray, np.ndarray]] = {
    "vermelho": (
        np.array([0, 100, 100], dtype=np.uint8),
        np.array([10, 255, 255], dtype=np.uint8),
    ),
    "vermelho2": (
        np.array([160, 100, 100], dtype=np.uint8),
        np.array([180, 255, 255], dtype=np.uint8),
    ),
    "azul": (
        np.array([100, 100, 100], dtype=np.uint8),
        np.array([130, 255, 255], dtype=np.uint8),
    ),
    "verde": (
        np.array([40, 100, 100], dtype=np.uint8),
        np.array([80, 255, 255], dtype=np.uint8),
    ),
    "amarelo": (
        np.array([20, 100, 100], dtype=np.uint8),
        np.array([35, 255, 255], dtype=np.uint8),
    ),
    "laranja": (
        np.array([10, 100, 100], dtype=np.uint8),
        np.array([25, 255, 255], dtype=np.uint8),
    ),
    "roxo": (
        np.array([130, 100, 100], dtype=np.uint8),
        np.array([160, 255, 255], dtype=np.uint8),
    ),
}


def decode_frame(image_base64: str) -> np.ndarray:
    raw = base64.b64decode(image_base64)
    arr = np.frombuffer(raw, dtype=np.uint8)
    frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if frame is None or frame.shape[:2] != (FRAME_HEIGHT, FRAME_WIDTH):
        frame = np.zeros((FRAME_HEIGHT, FRAME_WIDTH, 3), dtype=np.uint8)
    return frame


def apply_color_mask(frame: np.ndarray, color: str) -> np.ndarray:
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    if color == "vermelho":
        lower1, upper1 = COLOR_RANGES["vermelho"]
        lower2, upper2 = COLOR_RANGES["vermelho2"]
        mask1 = cv2.inRange(hsv, lower1, upper1)
        mask2 = cv2.inRange(hsv, lower2, upper2)
        mask = cv2.bitwise_or(mask1, mask2)
    else:
        lower, upper = COLOR_RANGES.get(color, (np.array([0, 0, 0]), np.array([180, 255, 255])))
        mask = cv2.inRange(hsv, lower, upper)

    return cv2.bitwise_and(frame, frame, mask=mask)


def detect_spheres(frame: np.ndarray, color: str | None = None) -> list[dict]:
    working = frame.copy()

    if color is not None:
        working = apply_color_mask(working, color)

    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)

    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=30,
        param1=50,
        param2=30,
        minRadius=10,
        maxRadius=150,
    )

    if circles is None:
        return []

    results: list[dict] = []
    for circle in circles[0]:
        cx, cy, r = circle
        x = int(cx - r)
        y = int(cy - r)
        w = int(2 * r)
        h = int(2 * r)
        results.append(
            {
                "type": "esfera",
                "color": color,
                "bbox": (x, y, w, h),
                "center": (int(cx), int(cy)),
                "area": w * h,
            }
        )

    return results


def _detect_poly_objects(
    frame: np.ndarray, target_vertices: int, object_type: str, color: str | None = None
) -> list[dict]:
    working = frame.copy()

    if color is not None:
        working = apply_color_mask(working, color)

    gray = cv2.cvtColor(working, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    results: list[dict] = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 200:
            continue

        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.04 * peri, True)

        if len(approx) == target_vertices:
            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            results.append(
                {
                    "type": object_type,
                    "color": color,
                    "bbox": (x, y, w, h),
                    "center": (cx, cy),
                    "area": w * h,
                }
            )

    return results


def detect_cubes(frame: np.ndarray, color: str | None = None) -> list[dict]:
    return _detect_poly_objects(frame, 4, "cubo", color)


def detect_cones(frame: np.ndarray, color: str | None = None) -> list[dict]:
    return _detect_poly_objects(frame, 3, "cone", color)


def _try_detect_decorated(
    frame: np.ndarray, object_type: str, object_color: str | None
) -> list[dict]:
    if object_type == "esfera":
        return detect_spheres(frame, object_color)
    elif object_type == "cubo":
        return detect_cubes(frame, object_color)
    elif object_type == "cone":
        return detect_cones(frame, object_color)
    return []


def detect_object(
    frame: np.ndarray, object_type: str, object_color: str | None = None
) -> dict | None:
    matches = _try_detect_decorated(frame, object_type, object_color)

    if not matches:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        equalized = cv2.equalizeHist(gray)
        eq_frame = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
        matches = _try_detect_decorated(eq_frame, object_type, object_color)

    if not matches:
        return None

    return select_best_match(matches)


def select_best_match(matches: list[dict]) -> dict:
    return max(matches, key=lambda m: m["area"])


def parse_description(description: str) -> tuple[str, str | None]:
    text = description.lower().strip()

    type_map = {
        "cubo": "cubo",
        "cubos": "cubo",
        "esfera": "esfera",
        "esferas": "esfera",
        "bola": "esfera",
        "bolas": "esfera",
        "cone": "cone",
        "cones": "cone",
    }

    for key, obj_type in type_map.items():
        if key in text:
            for color in COLOR_RANGES:
                if color in text:
                    return (obj_type, color)
            return (obj_type, None)

    for color in COLOR_RANGES:
        if color in text:
            return ("cubo", color)

    return ("cubo", None)
