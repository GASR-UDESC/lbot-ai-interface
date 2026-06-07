import asyncio
import time

import cv2
import numpy as np

from .detector import (
    decode_frame,
    detect_object,
    parse_description,
    FRAME_WIDTH,
    FRAME_HEIGHT,
)
from .vision import ask_llm_if_object_visible

MOVE_DELAY_SECONDS = 2
FOV_HORIZONTAL = 100
CENTER_THRESHOLD_PX = 64
MAX_CENTER_ATTEMPTS = 5
MAX_APPROACH_STEPS = 10
MAX_RESCANS = 2
MIN_SAFE_DISTANCE_CM = 20
TARGET_DISTANCE_CM = 50
CAMERA_TIMEOUT = 5.0
EXPLORE_OFFSET_CM = 50
MAX_EXPLORE_DIRECTIONS = 4
OPENCV_RETRY_FORWARD_1 = 50
OPENCV_RETRY_FORWARD_2 = 30


class SearchOrchestrator:

    def __init__(self, backend, *, llm_client, llm_model: str = "auto"):
        self._backend = backend
        self._llm_client = llm_client
        self._llm_model = llm_model
        self._steps_taken: list[str] = []
        self._last_bbox: tuple | None = None
        self._rescan_count = 0
        self._original_description: str = ""
        self._object_type: str = "cubo"
        self._object_color: str | None = None
        self._llm_spotted: bool = False

    async def run(self, description: str) -> dict:
        t0 = time.monotonic()

        self._original_description = description
        self._object_type, self._object_color = parse_description(description)

        scan_result = await self._scan(self._object_type, self._object_color)

        if scan_result is None and not self._llm_spotted:
            scan_result = await self._explore_offsets(
                self._object_type, self._object_color
            )

        if scan_result is None and self._llm_spotted:
            scan_result = await self._opencv_retry_with_advance(
                self._object_type, self._object_color
            )

        if scan_result is None:
            return {
                "status": "not_found",
                "object_type": self._object_type,
                "object_color": self._object_color,
                "bounding_box": None,
                "final_distance_cm": None,
                "steps_taken": self._steps_taken,
            }

        obj = scan_result["object"]
        self._last_bbox = obj["bbox"]

        centered = await self._center(obj["center"])
        if not centered:
            return {
                "status": "not_found",
                "reason": "could not center",
                "object_type": self._object_type,
                "object_color": self._object_color,
                "bounding_box": self._last_bbox,
                "final_distance_cm": None,
                "steps_taken": self._steps_taken,
            }

        approach_result = await self._approach(self._object_type, self._object_color)

        elapsed = round(time.monotonic() - t0, 2)
        return {
            "status": approach_result.get("status", "not_found"),
            "reason": approach_result.get("reason"),
            "object_type": self._object_type,
            "object_color": self._object_color,
            "bounding_box": self._last_bbox,
            "final_distance_cm": approach_result.get("final_distance_cm"),
            "steps_taken": self._steps_taken,
            "elapsed_seconds": elapsed,
        }

    async def _scan(
        self, object_type: str, object_color: str | None
    ) -> dict | None:
        for i in range(4):
            self._steps_taken.append(f"scan_frame_{i}")

            try:
                camera_data = await asyncio.wait_for(
                    self._backend.get_camera(), timeout=CAMERA_TIMEOUT
                )
            except asyncio.TimeoutError:
                self._steps_taken.append("camera_timeout")
                continue
            except Exception:
                self._steps_taken.append("camera_error")
                continue

            image_base64 = camera_data["image"]
            frame = decode_frame(image_base64)

            if frame is None or frame.shape[0] == 0:
                continue

            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"llm_not_found_at_{i * 90}deg")
                if i < 3:
                    await self._rotate(-90)
                continue

            self._steps_taken.append(f"llm_detected_at_{i * 90}deg")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                angle = i * 90
                self._steps_taken.append(f"cv_confirmed_at_{angle}deg")
                return {"object": result, "angle": angle}

            self._steps_taken.append(f"cv_not_confirmed_at_{i * 90}deg")
            self._llm_spotted = True
            if i < 3:
                await self._rotate(-90)

        return None

    async def _capture_frame(self) -> np.ndarray | None:
        try:
            camera_data = await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
            return decode_frame(camera_data["image"])
        except asyncio.TimeoutError:
            self._steps_taken.append("camera_timeout")
            return None
        except Exception:
            self._steps_taken.append("camera_error")
            return None

    async def _rotate(self, degrees: float) -> None:
        direction = "R" if degrees > 0 else "L"
        cmd = f"R{int(abs(degrees))}{direction};"
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"rotate_{cmd.strip(';')}")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _move_forward(self, cm: int) -> None:
        cmd = f"D{cm}F;"
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"forward_{cm}cm")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _move_backward(self, cm: int) -> None:
        cmd = f"D{cm}B;"
        await self._backend.execute_lbml(cmd)
        self._steps_taken.append(f"backward_{cm}cm")
        await asyncio.sleep(MOVE_DELAY_SECONDS)

    async def _explore_offsets(
        self, object_type: str, object_color: str | None
    ) -> dict | None:
        for direction in range(MAX_EXPLORE_DIRECTIONS):
            self._steps_taken.append(f"explore_direction_{direction}")
            await self._rotate(90)

            await self._move_forward(EXPLORE_OFFSET_CM)

            frame = await self._capture_frame()
            if frame is None:
                await self._move_backward(EXPLORE_OFFSET_CM)
                continue

            try:
                camera_data = await asyncio.wait_for(
                    self._backend.get_camera(), timeout=CAMERA_TIMEOUT
                )
            except (asyncio.TimeoutError, Exception):
                await self._move_backward(EXPLORE_OFFSET_CM)
                continue

            image_base64 = camera_data["image"]
            llm_description = self._original_description
            if not llm_description:
                llm_description = f"{object_color} {object_type}" if object_color else object_type

            llm_sees = await ask_llm_if_object_visible(
                self._llm_client, self._llm_model,
                image_base64, llm_description,
            )

            if not llm_sees:
                self._steps_taken.append(f"explore_dir_{direction}_llm_not_found")
                await self._move_backward(EXPLORE_OFFSET_CM)
                continue

            self._steps_taken.append(f"explore_dir_{direction}_llm_detected")
            result = detect_object(frame, object_type, object_color)

            if result is not None:
                self._steps_taken.append(f"explore_cv_confirmed_dir_{direction}")
                return {"object": result, "angle": direction * 90}

            self._steps_taken.append(f"explore_cv_not_confirmed_dir_{direction}")
            self._llm_spotted = True
            await self._move_backward(EXPLORE_OFFSET_CM)

        return None

    async def _opencv_retry_with_advance(
        self, object_type: str, object_color: str | None
    ) -> dict | None:
        self._steps_taken.append("opencv_retry_start")
        self._llm_spotted = False

        frame = await self._capture_frame()
        if frame is not None:
            result = detect_object(frame, object_type, object_color)
            if result is not None:
                self._steps_taken.append("opencv_retry_found_initial")
                return {"object": result, "angle": 0}

        self._steps_taken.append("opencv_retry_forward_50cm")
        await self._move_forward(OPENCV_RETRY_FORWARD_1)
        frame = await self._capture_frame()
        if frame is not None:
            result = detect_object(frame, object_type, object_color)
            if result is not None:
                self._steps_taken.append("opencv_retry_found_after_50cm")
                return {"object": result, "angle": 0}

        self._steps_taken.append("opencv_retry_forward_30cm")
        await self._move_forward(OPENCV_RETRY_FORWARD_2)
        frame = await self._capture_frame()
        if frame is not None:
            result = detect_object(frame, object_type, object_color)
            if result is not None:
                self._steps_taken.append("opencv_retry_found_after_30cm")
                return {"object": result, "angle": 0}

        self._steps_taken.append("opencv_retry_not_found")
        return None

    async def _center(self, object_center: tuple[int, int]) -> bool:
        cx, cy = object_center

        for attempt in range(MAX_CENTER_ATTEMPTS):
            erro_x = cx - FRAME_WIDTH / 2

            if abs(erro_x) < CENTER_THRESHOLD_PX:
                self._steps_taken.append(f"centered_attempt_{attempt + 1}")
                return True

            graus = (erro_x / FRAME_WIDTH) * FOV_HORIZONTAL

            if abs(graus) < 1:
                self._steps_taken.append(f"centered_attempt_{attempt + 1}")
                return True

            self._steps_taken.append(f"center_attempt_{attempt + 1}_error_{erro_x:.0f}px")
            await self._rotate(graus)

            frame = await self._capture_frame()
            if frame is None:
                continue

            result = detect_object(frame, self._object_type, self._object_color)
            if result is None:
                return False

            cx, cy = result["center"]
            self._last_bbox = result["bbox"]

        return False

    async def _approach(self, object_type: str, object_color: str | None) -> dict:
        step_count = 0
        rescan_count = 0

        while step_count < MAX_APPROACH_STEPS:
            sensor = await self._backend.get_proximity_sensor()
            distance = sensor["frente"]

            self._steps_taken.append(f"approach_step_{step_count + 1}_sensor_{distance:.0f}cm")

            if distance < MIN_SAFE_DISTANCE_CM:
                return {"status": "not_found", "reason": "obstacle too close"}

            if distance <= TARGET_DISTANCE_CM:
                self._steps_taken.append("approach_target_reached_confirming")
                confirmed = await self._confirm_via_camera()
                if confirmed:
                    self._steps_taken.append("camera_confirmed_object")
                    return {"status": "found", "final_distance_cm": distance}
                self._steps_taken.append("camera_did_not_confirm")
                return {"status": "not_found", "reason": "camera did not confirm object"}

            step = max(5, int(distance / 3))
            self._steps_taken.append(f"approach_step_{step}cm")
            await self._move_forward(step)
            step_count += 1

            frame = await self._capture_frame()
            if frame is None:
                continue

            result = detect_object(frame, object_type, object_color)

            if result is None:
                self._steps_taken.append("tracking_lost_rescan")
                if rescan_count >= MAX_RESCANS:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                rescan_count += 1
                scan_result = await self._scan(object_type, object_color)
                if scan_result is None:
                    if rescan_count >= MAX_RESCANS:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    if not self._llm_spotted:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    continue
                obj = scan_result["object"]
                cx, cy = obj["center"]
                self._last_bbox = obj["bbox"]
            else:
                cx, cy = result["center"]
                self._last_bbox = result["bbox"]

            centered = await self._center((cx, cy))
            if not centered:
                self._steps_taken.append("recenter_failed")
                if rescan_count >= MAX_RESCANS:
                    return {"status": "not_found", "reason": "lost tracking after rescan"}
                rescan_count += 1
                scan_result = await self._scan(object_type, object_color)
                if scan_result is None:
                    if rescan_count >= MAX_RESCANS:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    if not self._llm_spotted:
                        return {"status": "not_found", "reason": "lost tracking after rescan"}
                    continue
                obj = scan_result["object"]
                self._last_bbox = obj["bbox"]

        return {"status": "not_found", "reason": "max approach steps exceeded"}

    async def _confirm_via_camera(self) -> bool:
        self._steps_taken.append("camera_confirmation_check")
        try:
            camera_data = await asyncio.wait_for(
                self._backend.get_camera(), timeout=CAMERA_TIMEOUT
            )
            image_base64 = camera_data["image"]
        except (asyncio.TimeoutError, Exception):
            self._steps_taken.append("camera_confirmation_error")
            return False

        llm_description = self._original_description
        if not llm_description:
            llm_description = (
                f"{self._object_color} {self._object_type}"
                if self._object_color else self._object_type
            )

        return await ask_llm_if_object_visible(
            self._llm_client, self._llm_model,
            image_base64, llm_description,
        )
