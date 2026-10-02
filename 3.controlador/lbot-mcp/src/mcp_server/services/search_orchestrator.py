import asyncio
import math
import os
import time

import cv2

from .detector import COLOR_RANGES, decode_frame, parse_description, propose_regions
from .vision import locate_object


class SearchBudgetExpired(Exception):
    """A deliberate search limit, separate from a failed perception request."""


class SearchOrchestrator:
    def __init__(self, backend, *, perception=locate_object, clock=time.monotonic):
        self.backend = backend
        self.perception = perception
        self.steps = []
        self.last = None
        self.camera = None
        self.description = ""
        self.session = None
        self.clock = clock
        self.deadline = None
        self.observations = 0
        self.heading = 0.0  # Relative odometry, never simulator absolute pose.

    async def _execute(self, command):
        result = await self.backend.execute_lbml(
            command, wait=True, session_id=self.session
        )
        self.steps.append({"command": command, **result})
        if result.get("status") != "completed":
            raise RuntimeError(
                result.get("reason") or result.get("status", "execution_unknown")
            )
        return result

    async def _rotate(self, degrees):
        if abs(degrees) < 1:
            return
        result = await self._execute(
            f"R{max(1, round(abs(degrees)))}{'L' if degrees > 0 else 'R'};"
        )
        self.heading += result["rotation_degrees"]

    async def _travel(self, cm, forward=True):
        remaining = max(0, round(cm))
        direction = "frente" if forward else "tras"
        while remaining:
            data = await self.backend.get_proximity()
            self._check_session(data)
            if data.get("validity", {}).get(direction) == "unavailable":
                raise RuntimeError("sensor_unavailable")
            distance = data.get("readings", {}).get(direction)
            if distance is None:
                raise RuntimeError("sensor_unavailable")
            step = min(20, remaining)
            if distance - step < 20:
                raise RuntimeError("obstacle_blocked")
            await self._execute(f"D{step}{'F' if forward else 'B'};")
            remaining -= step

    def _check_session(self, data):
        session = data.get("session_id")
        if session is None:
            raise RuntimeError("invalid_observation")
        if self.session is not None and session != self.session:
            raise RuntimeError("stale_session")
        self.session = session

    async def _observe(self, track=False):
        self.camera = await self.backend.get_camera()
        self._check_session(self.camera)
        frame = decode_frame(self.camera["image"])
        # OpenCV tracks a semantically selected target, without requiring rigid shape classification.
        if track and self.last and self.last.get("bbox"):
            _, color = parse_description(self.description)
            candidates = propose_regions(frame, color) if color else []
            old = self.last["bbox"]
            old_cx = old[0] + old[2] / 2
            old_cy = old[1] + old[3] / 2
            nearby = [
                c
                for c in candidates
                if abs(c[0] + c[2] / 2 - old_cx) < 100
                and abs(c[1] + c[3] / 2 - old_cy) < 100
                and 0.3 < (c[2] * c[3]) / (old[2] * old[3]) < 3
            ]
            if len(nearby) == 1:
                b = nearby[0]
                self.last = {
                    **self.last,
                    "bbox": b,
                    "frame_id": self.camera["frame_id"],
                    "revision": self.camera["revision"],
                    "sensor_association": False,
                }
                return self.last
        self.last = await self.perception(self.camera, self.description)
        return self.last

    async def _scan(self):
        inconclusive = False
        for _ in range(8):
            remaining = self.deadline - self.clock()
            # Reserve time to return safely from an exploration offset. The parent skill
            # still has its own hard timeout; inference failures are never object absence.
            if remaining <= 10:
                raise SearchBudgetExpired()
            budget = asyncio.timeout(remaining - 10)
            try:
                async with budget:
                    observation = await self._observe()
            except TimeoutError:
                if budget.expired():
                    raise SearchBudgetExpired() from None
                raise
            self.observations += 1
            if observation["status"] == "detected":
                return observation
            inconclusive |= observation["status"] == "inconclusive"
            await self._rotate(45)
        if inconclusive:
            raise RuntimeError("perception_inconclusive")
        return None

    async def _search(self):
        found = await self._scan()
        if not found:
            for _ in range(4):
                sensor = await self.backend.get_proximity()
                self._check_session(sensor)
                if sensor.get("validity", {}).get("frente") == "unavailable":
                    raise RuntimeError("sensor_unavailable")
                available = sensor.get("readings", {}).get("frente")
                if available is None:
                    raise RuntimeError("sensor_unavailable")
                advance = min(50, max(0, math.floor(available - 20)))
                if advance >= 5:
                    heading = self.heading
                    await self._travel(advance)
                    try:
                        found = await self._scan()
                    except SearchBudgetExpired:
                        await self._rotate((heading - self.heading + 180) % 360 - 180)
                        await self._travel(advance, False)
                        raise
                    if found:
                        break
                    await self._travel(advance, False)
                await self._rotate(90)
        return found

    async def run(self, description):
        self.description = description
        seconds = min(
            float(os.getenv("LBOT_SEARCH_BUDGET", "150")),
            float(os.getenv("LBOT_SKILL_TIMEOUT", "180")) - 15,
        )
        if seconds <= 10:
            raise ValueError("invalid_search_budget")
        self.deadline = self.clock() + seconds
        complete = True
        try:
            found = await self._search()
        except SearchBudgetExpired:
            await self._rotate((-self.heading + 180) % 360 - 180)
            found, complete = None, False
        return {
            "status": "completed",
            "detected": bool(found),
            "centered": False,
            "approached": False,
            "observation": found,
            "reason": None if found else "not_located_within_search",
            "coverage": {
                "observations": self.observations,
                "search_complete": complete,
                "limit_reason": None if complete else "time_budget",
            },
            "steps": self.steps,
        }

    async def _center(self):
        for _ in range(8):
            data = await self._observe(track=True)
            if data["status"] != "detected":
                # Recover by looking, never by advancing blind.
                recovered = False
                for delta in (-15, 30):
                    await self._rotate(delta)
                    data = await self._observe()
                    if data["status"] == "detected":
                        recovered = True
                        break
                if not recovered:
                    return False
            box = data["bbox"]
            intr = self.camera["intrinsics"]
            error = box[0] + box[2] / 2 - intr["cx"]
            if abs(error) <= min(16, max(4, box[2] / 4)):
                return True
            degrees = math.degrees(math.atan(error / intr["fx"]))
            await self._rotate(-max(-45, min(45, degrees)))
        return False

    def _associate_range(self, observation, distance):
        projection = self.camera.get("range_projection")
        if not projection:
            return bool(observation.get("sensor_association"))
        _, color = parse_description(self.description)
        if not color or color not in COLOR_RANGES:
            return bool(observation.get("sensor_association"))
        point = [
            o + d * distance
            for o, d in zip(projection["origin_cm"], projection["direction"])
        ]
        if point[2] <= 0:
            return False
        intr = self.camera["intrinsics"]
        px = round(intr["cx"] + intr["fx"] * point[0] / point[2])
        py = round(intr["cy"] + intr["fy"] * point[1] / point[2])
        x, y, w, h = observation["bbox"]
        if not (x <= px <= x + w and y <= py <= y + h):
            return False
        frame = decode_frame(self.camera["image"])
        if not (0 <= px < frame.shape[1] and 0 <= py < frame.shape[0]):
            return False
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pixel = hsv[py, px]
        ranges = [COLOR_RANGES[color]] + (
            [COLOR_RANGES["vermelho2"]] if color == "vermelho" else []
        )
        return any(
            bool(((pixel >= lower) & (pixel <= upper)).all()) for lower, upper in ranges
        )

    async def approach(self, target, description=None, stop_distance_cm=50):
        if not 20 <= stop_distance_cm <= 200:
            raise ValueError("stop_distance_cm must be between 20 and 200")
        initial_sensor = await self.backend.get_proximity()
        self._check_session(initial_sensor)
        initial_distance = initial_sensor.get("readings", {}).get("frente")
        if (
            initial_distance is None
            or initial_sensor.get("validity", {}).get("frente") == "unavailable"
        ):
            raise RuntimeError("sensor_unavailable")
        if initial_distance < 20:
            return {
                "status": "blocked",
                "reason": "obstacle_too_close",
                "detected": False,
                "approached": False,
                "evidence": {"sensor": initial_sensor},
            }
        detected = target == "object"
        if detected:
            result = await self.run(description)
            if not result["detected"]:
                return {
                    **result,
                    "status": "failed",
                    "reason": "target_not_located"
                    if result["coverage"]["search_complete"]
                    else "search_budget_exhausted",
                }
            if not await self._center():
                return {
                    "status": "failed",
                    "reason": "tracking_lost",
                    "detected": True,
                    "approached": False,
                }
        for _ in range(40):
            if detected:
                if not await self._center():
                    return {
                        "status": "failed",
                        "reason": "tracking_lost",
                        "detected": True,
                        "approached": False,
                    }
                # Semantic confirmation of the range beam association, not just a nearby colored patch.
                observation = await self._observe()
                if observation["status"] != "detected":
                    return {
                        "status": "blocked",
                        "reason": "target_range_unassociated",
                        "detected": True,
                        "approached": False,
                    }
            sensor = await self.backend.get_proximity()
            self._check_session(sensor)
            distance = sensor.get("readings", {}).get("frente")
            if (
                distance is None
                or sensor.get("validity", {}).get("frente") == "unavailable"
            ):
                raise RuntimeError("sensor_unavailable")
            if detected and not self._associate_range(observation, distance):
                return {
                    "status": "blocked",
                    "reason": "target_range_unassociated",
                    "detected": True,
                    "approached": False,
                }
            if distance < 20:
                return {
                    "status": "blocked",
                    "reason": "obstacle_too_close",
                    "detected": detected,
                    "approached": False,
                }
            if distance <= stop_distance_cm + 5:
                if distance < stop_distance_cm - 5:
                    await self._travel(
                        min(20, max(1, math.ceil(stop_distance_cm - distance))), False
                    )
                    continue
                return {
                    "status": "completed",
                    "detected": detected,
                    "centered": detected,
                    "approached": True,
                    "front_obstacle_distance_cm": distance,
                    "target_distance_cm": distance if detected else None,
                    "evidence": {
                        "sensor": {
                            k: sensor.get(k)
                            for k in ("session_id", "revision", "captured_at")
                        },
                        "observation": self.last if detected else None,
                    },
                    "steps": self.steps,
                }
            if sensor.get("validity", {}).get("frente") != "valid":
                return {
                    "status": "blocked",
                    "reason": "no_obstacle_in_range",
                    "approached": False,
                }
            await self._travel(
                min(20, max(1, round((distance - stop_distance_cm) / 2)))
            )
        return {
            "status": "failed",
            "reason": "approach_budget_exhausted",
            "detected": detected,
            "approached": False,
        }
