import asyncio
import base64

import cv2
import numpy as np

from mcp_server.backends.base import LBotBackend


class FakeBackend(LBotBackend):
    """A robot with no absolute pose, delayed actuators and real observation envelopes."""

    def __init__(self, delay=0, valid=True):
        self.delay = delay
        self.valid = valid
        self.distance = 100.0
        self.revision = 0
        self.session = "fake"
        self.commands = []
        self.stopped = False
        image = np.zeros((480, 640, 3), np.uint8)
        cv2.rectangle(image, (300, 200), (340, 240), (0, 0, 255), -1)
        _, png = cv2.imencode(".png", image)
        self.image = base64.b64encode(png).decode()

    async def get_camera(self):
        return {
            "image": self.image,
            "frame_id": str(self.revision),
            "session_id": self.session,
            "revision": self.revision,
            "captured_at": "now",
            "intrinsics": {
                "width": 640,
                "height": 480,
                "fx": 342,
                "fy": 342,
                "cx": 320,
                "cy": 240,
            },
        }

    async def get_proximity(self):
        return {
            "readings": {"frente": self.distance, "tras": 200},
            "validity": {
                "frente": "valid" if self.valid else "unavailable",
                "tras": "valid",
            },
            "session_id": self.session,
            "revision": self.revision,
            "captured_at": "now",
        }

    async def execute_lbml(self, lbml, *, wait=False, session_id=None):
        await asyncio.sleep(self.delay)
        if session_id is not None and session_id != self.session:
            raise RuntimeError("stale_session")
        self.commands.append(lbml)
        self.revision += 1
        amount = int(lbml[1:-2])
        distance = 0
        if lbml.startswith("D"):
            distance = amount
            self.distance += amount if lbml[-2] == "B" else -amount
        return {
            "status": "completed",
            "command_id": str(self.revision),
            "session_id": self.session,
            "revision": self.revision,
            "distance_cm": distance,
            "rotation_degrees": (amount if lbml[-2] == "L" else -amount)
            if lbml.startswith("R")
            else 0,
        }

    async def stop(self):
        self.stopped = True
        return {"status": "completed"}


class OdometryFakeBackend(FakeBackend):
    """Second adapter with measured relative motion, no public absolute pose."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.x = self.z = self.heading = 0.0

    async def execute_lbml(self, lbml, *, wait=False, session_id=None):
        import math

        result = await super().execute_lbml(lbml, wait=wait, session_id=session_id)
        self.heading += result["rotation_degrees"]
        if lbml.startswith("D"):
            amount = result["distance_cm"] * (-1 if lbml[-2] == "B" else 1)
            self.x += math.sin(math.radians(self.heading)) * amount
            self.z += math.cos(math.radians(self.heading)) * amount
        return result
