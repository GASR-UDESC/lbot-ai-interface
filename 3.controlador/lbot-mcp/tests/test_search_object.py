import asyncio

import pytest

from mcp_server.services.control import ControlService

from .fake_backend import FakeBackend


@pytest.mark.asyncio
async def test_stop_interrupts_long_operation():
    b = FakeBackend(delay=10)
    control = ControlService(b)
    task = asyncio.create_task(control.run(lambda: b.execute_lbml("D20F;", wait=True)))
    await asyncio.sleep(0.01)
    result = await control.stop()
    operation = await task
    assert result["status"] == "completed"
    assert operation["status"] == "cancelled"
    assert b.stopped
    assert not b.commands


@pytest.mark.asyncio
async def test_concurrent_operations_receive_busy():
    b = FakeBackend(delay=0.05)
    control = ControlService(b)
    task = asyncio.create_task(control.run(lambda: b.execute_lbml("D20F;", wait=True)))
    await asyncio.sleep(0.01)
    assert (await control.run(lambda: b.execute_lbml("D20F;", wait=True)))[
        "reason"
    ] == "busy"
    assert (await task)["status"] == "completed"


@pytest.mark.asyncio
async def test_deadline_stops_backend(monkeypatch):
    monkeypatch.setenv("LBOT_SKILL_TIMEOUT", ".01")
    b = FakeBackend(delay=10)
    result = await ControlService(b).run(lambda: b.execute_lbml("D20F;", wait=True))
    assert result["status"] == "timed_out" and b.stopped


@pytest.mark.asyncio
async def test_stop_interrupts_search_during_visual_inference():
    from mcp_server.services.search_orchestrator import SearchOrchestrator

    backend = FakeBackend()
    started = asyncio.Event()

    async def perception(*args):
        started.set()
        await asyncio.sleep(60)

    control = ControlService(backend)
    task = asyncio.create_task(
        control.run(
            lambda: SearchOrchestrator(backend, perception=perception).run("cubo azul")
        )
    )
    await started.wait()
    await control.stop()
    assert (await task)["status"] == "cancelled"
    assert backend.stopped and backend.commands == []
