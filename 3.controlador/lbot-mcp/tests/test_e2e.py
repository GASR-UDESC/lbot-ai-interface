import pytest
import os
import sys


E2E_SIMULATOR_URL = os.environ.get("LBOT_SIMULATOR_URL", "http://localhost:3001")

pytestmark = pytest.mark.e2e


async def _check_simulator_available() -> bool:
    import httpx

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(f"{E2E_SIMULATOR_URL}/api/health")
            return resp.status_code == 200
    except Exception:
        return False


@pytest.mark.asyncio
async def test_e2e_simulator_health():
    import httpx

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(f"{E2E_SIMULATOR_URL}/api/health")
            assert resp.status_code == 200
            data = resp.json()
            assert data["status"] == "online"
    except httpx.ConnectError:
        pytest.skip("Simulador nao disponivel")


@pytest.mark.asyncio
async def test_e2e_camera_via_backend():
    if not await _check_simulator_available():
        pytest.skip("Simulador nao disponivel")

    from mcp_server.backends.simulator import SimulatorBackend

    backend = SimulatorBackend(base_url=E2E_SIMULATOR_URL)
    try:
        result = await backend.get_camera()
        assert isinstance(result, dict)
        assert "image" in result
        assert isinstance(result["image"], str)
        assert len(result["image"]) > 0
        assert "render_method" in result
    finally:
        await backend.close()


@pytest.mark.asyncio
async def test_e2e_sensors_via_backend():
    if not await _check_simulator_available():
        pytest.skip("Simulador nao disponivel")

    from mcp_server.backends.simulator import SimulatorBackend

    backend = SimulatorBackend(base_url=E2E_SIMULATOR_URL)
    try:
        readings = await backend.get_proximity()
        assert "front_cm" in readings
        assert "rear_cm" in readings
        assert isinstance(readings["front_cm"], (int, float))
        assert isinstance(readings["rear_cm"], (int, float))
    finally:
        await backend.close()
