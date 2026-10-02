from unittest.mock import AsyncMock

import pytest

from mcp_server.services.search_orchestrator import SearchOrchestrator

from .fake_backend import FakeBackend


@pytest.mark.asyncio
async def test_search_locates_without_approaching():
    b = FakeBackend()
    p = AsyncMock(
        return_value={
            "status": "detected",
            "bbox": [300, 200, 40, 40],
            "sensor_association": True,
        }
    )
    r = await SearchOrchestrator(b, perception=p).run("cubo vermelho")
    assert r["detected"] and not r["approached"]
    assert b.commands == []


@pytest.mark.asyncio
async def test_absent_target_has_bounded_search_and_no_world_absence_claim():
    b = FakeBackend()
    p = AsyncMock(
        return_value={
            "status": "not_detected",
            "bbox": None,
            "sensor_association": False,
        }
    )
    r = await SearchOrchestrator(b, perception=p).run("cubo vermelho")
    assert not r["detected"]
    assert r["reason"] == "not_located_within_search"
    assert p.call_count == 40
    assert all(int(c[1:-2]) <= 20 for c in b.commands if c.startswith("D"))


@pytest.mark.asyncio
async def test_invalid_sensor_never_assumes_free_space():
    b = FakeBackend(valid=False)
    p = AsyncMock(
        return_value={
            "status": "not_detected",
            "bbox": None,
            "sensor_association": False,
        }
    )
    with pytest.raises(RuntimeError, match="sensor_unavailable"):
        await SearchOrchestrator(b, perception=p).run("cubo vermelho")
    assert not any(c.startswith("D") for c in b.commands)


@pytest.mark.asyncio
async def test_object_approach_verifies_range_and_detection_without_absolute_pose():
    b = FakeBackend()
    p = AsyncMock(
        return_value={
            "status": "detected",
            "bbox": [300, 200, 40, 40],
            "sensor_association": True,
        }
    )
    r = await SearchOrchestrator(b, perception=p).approach(
        "object", "cubo vermelho", 50
    )
    assert r["approached"] and r["detected"]
    assert 45 <= r["target_distance_cm"] <= 55


@pytest.mark.asyncio
async def test_unassociated_obstacle_does_not_count_as_target_arrival():
    b = FakeBackend()
    p = AsyncMock(
        return_value={
            "status": "detected",
            "bbox": [300, 200, 40, 40],
            "sensor_association": False,
        }
    )
    r = await SearchOrchestrator(b, perception=p).approach("object", "cubo vermelho")
    assert r["status"] == "blocked"
    assert not r["approached"]
    assert b.commands == []


@pytest.mark.asyncio
async def test_inference_error_is_not_object_absence():
    b = FakeBackend()
    p = AsyncMock(side_effect=RuntimeError("inference_unavailable"))
    with pytest.raises(RuntimeError, match="inference_unavailable"):
        await SearchOrchestrator(b, perception=p).run("cubo vermelho")


@pytest.mark.asyncio
async def test_search_budget_reports_partial_coverage_without_world_absence(
    monkeypatch,
):
    monkeypatch.setenv("LBOT_SEARCH_BUDGET", "11")
    clock = [0]

    async def perception(*args):
        clock[0] += 2
        return {"status": "not_detected", "bbox": None, "sensor_association": False}

    backend = FakeBackend()
    result = await SearchOrchestrator(
        backend, perception=perception, clock=lambda: clock[0]
    ).run("cubo azul")
    assert result["status"] == "completed" and not result["detected"]
    assert result["coverage"] == {
        "observations": 1,
        "search_complete": False,
        "limit_reason": "time_budget",
    }
    assert result["reason"] == "not_located_within_search"
    assert not any(command.startswith("D") for command in backend.commands)


@pytest.mark.asyncio
async def test_calibrated_beam_uses_visible_target_region_not_llm_distance():
    b = FakeBackend()
    original = b.get_camera

    async def calibrated():
        data = await original()
        data["range_projection"] = {"origin_cm": [0, 0, 0], "direction": [0, 0, 1]}
        return data

    b.get_camera = calibrated
    # The semantic model can be conservative about association; calibration and image validate it.
    p = AsyncMock(
        return_value={
            "status": "detected",
            "bbox": [300, 200, 40, 40],
            "sensor_association": False,
        }
    )
    result = await SearchOrchestrator(b, perception=p).approach(
        "object", "cubo vermelho"
    )
    assert result["approached"] and 45 <= result["target_distance_cm"] <= 55


@pytest.mark.asyncio
async def test_calibrated_range_does_not_attribute_foreground_to_background_target():
    import base64

    import cv2
    import numpy as np

    b = FakeBackend()
    frame = np.zeros((480, 640, 3), np.uint8)
    cv2.rectangle(frame, (300, 200), (340, 240), (255, 0, 0), -1)
    _, png = cv2.imencode(".png", frame)
    b.image = base64.b64encode(png).decode()
    original = b.get_camera

    async def calibrated():
        data = await original()
        data["range_projection"] = {"origin_cm": [0, 0, 0], "direction": [0, 0, 1]}
        return data

    b.get_camera = calibrated
    p = AsyncMock(
        return_value={
            "status": "detected",
            "bbox": [300, 200, 40, 40],
            "sensor_association": True,
        }
    )
    result = await SearchOrchestrator(b, perception=p).approach(
        "object", "cubo vermelho"
    )
    assert result["status"] == "blocked" and not result["approached"]
    assert not any(c.startswith("D") for c in b.commands)


@pytest.mark.asyncio
async def test_approach_does_not_explore_around_a_nearby_blocker():
    backend = FakeBackend()
    backend.distance = 5
    perception = AsyncMock()
    result = await SearchOrchestrator(backend, perception=perception).approach(
        "object", "cubo vermelho"
    )
    assert result["status"] == "blocked" and not result["approached"]
    assert result["reason"] == "obstacle_too_close"
    assert backend.commands == []
    perception.assert_not_awaited()


@pytest.mark.asyncio
async def test_reset_after_frame_prevents_rotation_in_new_session():
    backend = FakeBackend()

    async def perception(*args):
        backend.session = "new"
        return {"status": "not_detected", "bbox": None, "sensor_association": False}

    with pytest.raises(RuntimeError, match="stale_session"):
        await SearchOrchestrator(backend, perception=perception).run("cubo vermelho")
    assert backend.commands == []


@pytest.mark.asyncio
async def test_partial_scan_restores_heading_before_verified_return(monkeypatch):
    from .fake_backend import OdometryFakeBackend

    monkeypatch.setenv("LBOT_SEARCH_BUDGET", "30")
    backend = OdometryFakeBackend(delay=0.001)
    clock = [0]

    async def perception(*args):
        clock[0] += 2
        return {"status": "not_detected", "bbox": None, "sensor_association": False}

    result = await SearchOrchestrator(
        backend, perception=perception, clock=lambda: clock[0]
    ).run("cubo azul")
    assert not result["coverage"]["search_complete"]
    assert abs(backend.x) < 0.001 and abs(backend.z) < 0.001
    assert await backend.get_state() is None
    assert backend.commands[-4:] == ["R90R;", "D20B;", "D20B;", "D10B;"]
