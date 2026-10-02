"""Camera and stop benchmark; use a dedicated, idle simulator instance."""

import argparse
import asyncio
import json
import math
import statistics
import time
from pathlib import Path

import httpx


def summarize(values):
    ordered = sorted(values)
    return {
        "count": len(values),
        "p50_ms": statistics.median(values),
        "p95_ms": ordered[math.ceil(len(values) * 0.95) - 1],
        "max_ms": max(values),
    }


async def run(url, output):
    async with httpx.AsyncClient(base_url=url, timeout=30) as api:
        (await api.post("/api/reset")).raise_for_status()
        (await api.get("/api/camera")).raise_for_status()  # Warm Chromium.
        camera, stopping = [], []
        for _ in range(30):
            started = time.monotonic()
            response = await api.get("/api/camera")
            response.raise_for_status()
            assert response.json()["renderMethod"] == "webgl"
            camera.append((time.monotonic() - started) * 1000)
        for _ in range(20):
            (await api.post("/api/reset")).raise_for_status()
            command = await api.post("/api/commands", json={"command": "D100F;"})
            command.raise_for_status()
            # Observe running, rather than presuming execution after a delay.
            while True:
                record = (
                    await api.get("/api/commands/" + command.json()["command_id"])
                ).json()
                if record["status"] == "running":
                    break
                await asyncio.sleep(0.005)
            started = time.monotonic()
            response = await api.post("/api/stop")
            response.raise_for_status()
            stopping.append((time.monotonic() - started) * 1000)
            assert response.json()["state"]["isAnimating"] is False
        summary = {
            "camera": summarize(camera),
            "stop": summarize(stopping),
            "note": "Warm camera and HTTP request-to-confirmed-stop latency; includes loopback transport. Dedicated simulator instance; this benchmark does not invoke the model. Other local workloads are not controlled.",
        }
        Path(output).write_text(json.dumps(summary, indent=2) + "\n")
        print(json.dumps(summary))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulator", default="http://127.0.0.1:3002")
    parser.add_argument(
        "--output", default=str(Path(__file__).with_name("simulator-benchmark.json"))
    )
    args = parser.parse_args()
    asyncio.run(run(args.simulator, args.output))
