import httpx
import pytest

from mcp_server.backends.simulator import SimulatorBackend


@pytest.mark.asyncio
async def test_adapter_waits_for_terminal_record_instead_of_acceptance():
    calls = []

    def handler(req):
        calls.append(req.method + " " + req.url.path)
        if req.url.path == "/api/state":
            return httpx.Response(200, json={"state": {"session_id": "one"}})
        if req.method == "POST":
            return httpx.Response(
                200,
                json={
                    "status": "accepted",
                    "command_id": "cmd",
                    "session_id": "one",
                    "revision": 2,
                },
            )
        return httpx.Response(
            200,
            json={
                "status": "completed",
                "command_id": "cmd",
                "session_id": "one",
                "revision": 3,
            },
        )

    b = SimulatorBackend()
    b._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    r = await b.execute_lbml("D20F;", wait=True)
    assert r["status"] == "completed"
    assert any(c.startswith("GET /api/commands/") for c in calls)
    await b.close()


@pytest.mark.asyncio
async def test_camera_failure_has_no_fallback_image():
    b = SimulatorBackend()
    b._client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda req: httpx.Response(503, json={"error": "camera_unavailable"})
        )
    )
    with pytest.raises(RuntimeError, match="camera_unavailable"):
        await b.get_camera()
    await b.close()


@pytest.mark.asyncio
async def test_deadline_stops_without_replaying_movement():
    calls = []

    def handler(req):
        calls.append(req.url.path)
        if req.url.path == "/api/state":
            return httpx.Response(200, json={"state": {"session_id": "one"}})
        return httpx.Response(200, json={"status": "accepted", "command_id": "cmd"})

    b = SimulatorBackend(command_timeout=0)
    b._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    assert (await b.execute_lbml("D20F;", wait=True))["status"] == "timed_out"
    assert calls.count("/api/commands") == 1
    assert calls[-1] == "/api/stop"
    await b.close()


@pytest.mark.asyncio
async def test_unknown_acceptance_never_replays():
    posts = []

    def handler(req):
        if req.url.path == "/api/state":
            return httpx.Response(200, json={"state": {"session_id": "one"}})
        posts.append(req.url.path)
        raise httpx.ReadTimeout("lost", request=req)

    b = SimulatorBackend()
    b._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    r = await b.execute_lbml("D20F;", wait=True)
    assert r["reason"] == "execution_unknown"
    assert posts.count("/api/commands") == 1
    assert posts[-1] == "/api/stop"
    await b.close()


@pytest.mark.asyncio
async def test_stale_frame_and_privileged_pose_are_not_accepted():
    frame = {
        "image": "base64",
        "renderMethod": "webgl",
        "frame_id": "frame",
        "session_id": "one",
        "revision": 2,
        "captured_at": "now",
        "intrinsics": {},
        "robot_position": {"x": 1},
    }
    b = SimulatorBackend()
    b._client = httpx.AsyncClient(
        transport=httpx.MockTransport(
            lambda req: httpx.Response(
                200,
                json={"state": {"session_id": "one"}}
                if req.url.path == "/api/state"
                else frame,
            )
        )
    )
    assert "robot_position" not in await b.get_camera()
    b._last_revision = 3
    b._last_session = "one"
    with pytest.raises(RuntimeError, match="stale_observation"):
        await b.get_camera()
    await b.close()


@pytest.mark.asyncio
async def test_reset_between_observation_and_command_never_actuates_new_session():
    calls = []

    def handler(req):
        calls.append(req.method)
        return httpx.Response(200, json={"state": {"session_id": "new"}})

    backend = SimulatorBackend()
    backend._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    with pytest.raises(RuntimeError, match="stale_session"):
        await backend.execute_lbml("R45L;", wait=True, session_id="old")
    assert calls == ["GET"]
    await backend.close()
