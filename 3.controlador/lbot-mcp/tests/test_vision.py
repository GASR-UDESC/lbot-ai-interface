import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mcp_server.services import vision

from .fake_backend import FakeBackend


@pytest.mark.asyncio
async def test_semantic_selection_accepts_region_without_shape_gate(monkeypatch):
    client = SimpleNamespace(
        complete=AsyncMock(
            return_value=SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(
                            content=json.dumps(
                                {
                                    "status": "detected",
                                    "candidate_id": 0,
                                    "bbox": None,
                                    "sensor_association": False,
                                }
                            )
                        )
                    )
                ]
            )
        )
    )
    monkeypatch.setattr(vision, "get_inference", lambda: client)
    observation = await vision.locate_object(
        await FakeBackend().get_camera(), "objeto vermelho"
    )
    assert observation["status"] == "detected"
    assert observation["bbox"][2] > 0
    assert observation["frame_id"] == "0"


@pytest.mark.asyncio
async def test_invalid_visual_response_remains_error(monkeypatch):
    client = SimpleNamespace(
        complete=AsyncMock(
            return_value=SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content='{"status":"not_detected"}')
                    )
                ]
            )
        )
    )
    monkeypatch.setattr(vision, "get_inference", lambda: client)
    with pytest.raises(RuntimeError, match="vision_invalid_response"):
        await vision.locate_object(await FakeBackend().get_camera(), "objeto vermelho")
