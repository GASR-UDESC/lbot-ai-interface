"""Run local model against a dedicated simulator (LBOT_ENABLE_EVAL=1).
Ground truth comes from diagnostic state, never from the model's final answer.
"""

import argparse
import asyncio
import json
import math
import os
import platform
import resource
import statistics
import sys
import time
from pathlib import Path

import httpx

from harness.agent import ReActAgent
from harness.mcp_client import MCPClient

ROOT = Path(__file__).parent


def score(case, trace, state, answer):
    calls = [e["tool"] for e in trace if e["event"] == "tool_call"]
    results = [e for e in trace if e["event"] == "tool_result"]
    expected = case["expected"]
    ok = (
        any(t in calls for t in case["expected_tools"])
        if case["expected_tools"]
        else not calls
    )
    selection = ok
    reason = []
    if not ok:
        reason.append("wrong_tool")
    if "pose" in expected:
        x, z, yaw = expected["pose"]
        delta = abs(state["rotation"] - yaw)
        if math.hypot(state["x"] - x, state["z"] - z) > 2 or delta > 2:
            ok = False
            reason.append("wrong_final_pose")
    if "text_contains" in expected and expected["text_contains"] not in answer.lower():
        ok = False
        reason.append("wrong_visual_description")
    if case["category"] == "search":
        r = next(
            (
                e["structured"]
                for e in reversed(results)
                if e["tool"] == "search_object"
            ),
            {},
        )
        if (
            r.get("detected") != expected["detected"]
            or r.get("approached") is not False
        ):
            ok = False
            reason.append("wrong_search_outcome")
        if expected["detected"] is False:
            origin = case["scenario"]["pose"]
            yaw_error = abs((state["rotation"] - origin["rotation"] + 180) % 360 - 180)
            if (
                math.hypot(state["x"] - origin["x"], state["z"] - origin["z"]) > 2
                or yaw_error > 2
            ):
                ok = False
                reason.append("search_return_unverified")
    if case["category"] == "sensors":
        reading = next(
            (
                e["structured"].get("readings", {})
                for e in reversed(results)
                if e["tool"] == "proximity"
            ),
            {},
        )
        if any(
            name not in reading or abs(reading[name] - value) > 1
            for name, value in expected["readings"].items()
        ):
            ok = False
            reason.append("wrong_sensor_readings")
    if case["category"] == "approach":
        r = next(
            (e["structured"] for e in reversed(results) if e["tool"] == "approach"), {}
        )
        # Range is checked with simulator geometry, not the tool's own claim.
        objects = case["scenario"]["objects"]
        target = next(o for o in objects if o["id"] == "target")
        actual = (
            math.hypot(state["x"] - target["x"], state["z"] - target["z"])
            - 15
            - target["size"]["depth"] / 2
        )
        if expected["approached"]:
            if (
                not r.get("approached")
                or abs(actual - expected["stop_distance_cm"]) > 5
            ):
                ok = False
                reason.append("arrival_unverified")
        elif r.get("approached") or r.get("status") not in ("blocked", "failed"):
            ok = False
            reason.append("block_not_reported")
    if state["isAnimating"]:
        ok = False
        reason.append("robot_still_running")
    return {"passed": ok, "tool_selection_correct": selection, "reasons": reason}


async def run(args):
    url = args.simulator.rstrip("/")
    os.environ["LBOT_SIMULATOR_URL"] = url
    cases = json.loads(args.cases.read_text())
    if args.split != "all":
        cases = [c for c in cases if c["split"] == args.split]
    if args.ids:
        cases = [c for c in cases if c["id"] in args.ids.split(",")]
    output = ROOT / args.output
    output.mkdir(parents=True, exist_ok=True)
    results = []
    trace_dir = Path(__file__).resolve().parent.parent / "runs" / "evals" / args.output
    os.environ["LBOT_TRACE_DIR"] = str(trace_dir)
    inference_log = trace_dir / "inference.jsonl"
    async with httpx.AsyncClient(timeout=30) as api, MCPClient() as mcp:
        agent = await ReActAgent.create(mcp)
        for case in cases:
            r = await api.post(url + "/api/scenario", json=case["scenario"])
            r.raise_for_status()
            log_offset = inference_log.stat().st_size if inference_log.exists() else 0
            start = time.monotonic()
            answer = await agent.run(case["prompt"])
            elapsed = time.monotonic() - start
            state = (await api.get(url + "/api/state")).json()["state"]
            infer = []
            if inference_log.exists():
                with inference_log.open() as stream:
                    stream.seek(log_offset)
                    infer = [json.loads(line) for line in stream if line.strip()]
            entry = {
                "id": case["id"],
                "split": case["split"],
                "category": case["category"],
                "prompt": case["prompt"],
                "answer": answer,
                "state": state,
                "metrics": {
                    **agent.metrics,
                    "total_inference_calls": len(infer),
                    "inference_seconds": sum(e["seconds"] for e in infer),
                },
                "inference": infer,
                "tool_results": [e for e in agent.trace if e["event"] == "tool_result"],
                "elapsed_seconds": elapsed,
                "process_max_rss": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                **score(case, agent.trace, state, answer),
            }
            results.append(entry)
            (output / "results.json").write_text(
                json.dumps(results, ensure_ascii=False, indent=2)
            )
            print(
                case["id"],
                entry["passed"],
                entry["reasons"],
                round(elapsed, 2),
                flush=True,
            )
        await mcp.call_tool("stop", {})
    categories = {}
    for category in sorted({r["category"] for r in results}):
        group = [r for r in results if r["category"] == category]
        categories[category] = {
            "count": len(group),
            "success_rate": sum(r["passed"] for r in group) / len(group),
        }
    times = sorted(r["elapsed_seconds"] for r in results)
    inference_times = sorted(e["seconds"] for r in results for e in r["inference"])

    def p95(values):
        return (
            values[min(len(values) - 1, math.ceil(len(values) * 0.95) - 1)]
            if values
            else None
        )

    summary = {
        "model": "qwen3.5-4b",
        "runtime": {
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "machine": platform.machine(),
            "context_tokens": 8192,
            "temperature": 0.2,
            "reasoning_effort": "none",
            "seed": 42,
        },
        "count": len(results),
        "success_rate": sum(r["passed"] for r in results) / len(results)
        if results
        else None,
        "tool_selection_rate": sum(r["tool_selection_correct"] for r in results)
        / len(results)
        if results
        else None,
        "categories": categories,
        "latency_p50_s": statistics.median(times) if times else None,
        "latency_p95_s": times[min(len(times) - 1, math.ceil(len(times) * 0.95) - 1)]
        if times
        else None,
        "total_inference_calls": len(inference_times),
        "inference_latency_p50_s": statistics.median(inference_times)
        if inference_times
        else None,
        "inference_latency_p95_s": p95(inference_times),
        "resource_note": "process_max_rss is the evaluator peak (bytes on macOS); model/server RAM, GPU utilization, energy and temperature are measured separately or unavailable.",
        "invalid_calls": sum(r["metrics"]["invalid_calls"] for r in results),
        "evaluation_note": "Success thresholds are goals, not automatically considered achieved.",
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2))
    (output / "REPORT.md").write_text(
        "# Avaliação local\n\nModelo: Qwen3.5 4B. Resultados verificados pelo estado diagnóstico, sem fornecer ground truth ao agente.\n\n```json\n"
        + json.dumps(summary, ensure_ascii=False, indent=2)
        + "\n```\n"
    )
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--simulator", default="http://127.0.0.1:3003")
    p.add_argument(
        "--split", choices=["all", "development", "acceptance"], default="all"
    )
    p.add_argument("--cases", type=Path, default=ROOT / "cases.json")
    p.add_argument("--ids")
    p.add_argument("--output", default="latest")
    asyncio.run(run(p.parse_args()))
