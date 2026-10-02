import asyncio
import json
from unittest.mock import AsyncMock

import pytest
from openai.types.chat import ChatCompletion

from harness.agent import ReActAgent
from harness.messages import compact_history


def response(content=None, calls=None):
    return ChatCompletion.model_validate(
        {
            "id": "test",
            "object": "chat.completion",
            "created": 0,
            "model": "fake",
            "choices": [
                {
                    "index": 0,
                    "finish_reason": "tool_calls" if calls else "stop",
                    "message": {
                        "role": "assistant",
                        "content": content,
                        "tool_calls": calls,
                    },
                }
            ],
        }
    )


def call(name, args, id="one"):
    return {
        "id": id,
        "type": "function",
        "function": {"name": name, "arguments": json.dumps(args)},
    }


def tools():
    return [
        {
            "type": "function",
            "function": {
                "name": name,
                "parameters": {
                    "type": "object",
                    "properties": {"command": {"type": "string"}}
                    if name == "move"
                    else {},
                    "required": ["command"] if name == "move" else [],
                    "additionalProperties": False,
                },
            },
        }
        for name in ("camera", "proximity", "move", "stop")
    ]


def agent(tmp_path, monkeypatch, responses, handler):
    monkeypatch.setenv("LBOT_TRACE_DIR", str(tmp_path))
    llm = AsyncMock()
    llm.complete.side_effect = responses
    mcp = AsyncMock()
    mcp.call_tool.side_effect = handler
    a = ReActAgent(mcp, tools(), inference=llm)
    a._compatible = True
    return a, llm, mcp


@pytest.mark.asyncio
async def test_multicall_results_precede_images(tmp_path, monkeypatch):
    async def handler(name, args):
        return (
            {"status": "completed", "image": "png", "frame_id": "f"}
            if name == "camera"
            else {"status": "completed", "readings": {"frente": 80}}
        )

    a, llm, _ = agent(
        tmp_path,
        monkeypatch,
        [
            response(calls=[call("camera", {}, "a"), call("proximity", {}, "b")]),
            response("Vejo o ambiente."),
        ],
        handler,
    )
    await a.run("observe e meça")
    roles = [m["role"] for m in a.history]
    assert roles == ["system", "user", "assistant", "tool", "tool", "user"]
    assert a.metrics["tool_calls"] == 2


@pytest.mark.asyncio
async def test_unknown_arguments_get_one_correction_without_actuation(
    tmp_path, monkeypatch
):
    async def handler(name, args):
        return {"status": "completed"}

    a, _, mcp = agent(
        tmp_path,
        monkeypatch,
        [
            response(calls=[call("move", {"command": 12})]),
            response(calls=[call("move", {"command": "ande 20 cm para frente"})]),
            response("Executado"),
        ],
        handler,
    )
    await a.run("ande")
    assert a.metrics["invalid_calls"] == 1
    assert mcp.call_tool.await_count == 1


@pytest.mark.asyncio
async def test_failure_stops_instead_of_announcing_success(tmp_path, monkeypatch):
    async def handler(name, args):
        return (
            {"status": "blocked", "reason": "obstacle_blocked"}
            if name == "move"
            else {"status": "completed"}
        )

    a, llm, mcp = agent(
        tmp_path,
        monkeypatch,
        [
            response(calls=[call("move", {"command": "ande 20 cm para frente"})]),
            response("Cheguei!"),
        ],
        handler,
    )
    text = await a.run("ande")
    assert "obstacle_blocked" in text
    assert llm.complete.await_count == 1
    assert mcp.call_tool.call_args.args[0] == "stop"


@pytest.mark.asyncio
async def test_cancellation_cancels_inference_and_stops(tmp_path, monkeypatch):
    started = asyncio.Event()

    async def complete(**kwargs):
        started.set()
        await asyncio.sleep(100)

    a, llm, mcp = agent(
        tmp_path, monkeypatch, [], lambda *args: {"status": "completed"}
    )
    llm.complete.side_effect = complete
    mcp.call_tool = AsyncMock(return_value={"status": "completed"})
    task = asyncio.create_task(a.run("ande"))
    await started.wait()
    a.cancel()
    assert "Parada confirmada" in await task
    mcp.call_tool.assert_awaited_once_with("stop", {})


def test_compaction_preserves_tool_result_pairs():
    messages = [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "goal"},
    ]
    for i in range(8):
        messages += [
            {
                "role": "assistant",
                "content": None,
                "tool_calls": [call("proximity", {}, str(i))],
            },
            {"role": "tool", "tool_call_id": str(i), "content": "x" * 1000},
        ]
    compact_history(messages, max_bytes=2000)
    ids = {c["id"] for m in messages for c in m.get("tool_calls", [])}
    assert all(m["tool_call_id"] in ids for m in messages if m["role"] == "tool")
    assert messages[1]["content"] == "goal"
    assert len(messages) < 18


def test_oversized_goal_fails_instead_of_silently_overfilling_context():
    with pytest.raises(RuntimeError, match="context_budget_exceeded"):
        compact_history(
            [
                {"role": "system", "content": "system"},
                {"role": "user", "content": "a" * 15000},
            ]
        )


@pytest.mark.asyncio
async def test_multicall_failure_skips_later_movement_but_returns_all_results(
    tmp_path, monkeypatch
):
    async def handler(name, args):
        return (
            {"status": "blocked", "reason": "collision"}
            if name == "move"
            else {"status": "completed"}
        )

    a, _, mcp = agent(
        tmp_path,
        monkeypatch,
        [
            response(
                calls=[
                    call("move", {"command": "avance 20 cm"}, "a"),
                    call("move", {"command": "recue 20 cm"}, "b"),
                ]
            )
        ],
        handler,
    )
    await a.run("avance e recue")
    assert [c.args[0] for c in mcp.call_tool.await_args_list] == ["move", "stop"]
    results = [m for m in a.history if m["role"] == "tool"]
    assert [r["tool_call_id"] for r in results] == ["a", "b"]
    assert json.loads(results[1]["content"])["reason"] == "previous_call_failed"


@pytest.mark.asyncio
async def test_busy_does_not_stop_another_operation(tmp_path, monkeypatch):
    a, _, mcp = agent(
        tmp_path,
        monkeypatch,
        [response(calls=[call("move", {"command": "avance 20 cm"})])],
        AsyncMock(return_value={"status": "failed", "reason": "busy"}),
    )
    assert "busy" in await a.run("avance")
    mcp.call_tool.assert_awaited_once_with("move", {"command": "avance 20 cm"})


def test_display_does_not_convert_approach_blockage_into_target_absence():
    from harness.tool_handler import result_for_display

    display = result_for_display(
        {
            "status": "blocked",
            "detected": False,
            "approached": False,
            "reason": "obstacle_too_close",
        }
    )
    assert "obstacle_too_close" in display
    assert "não localizado" not in display


@pytest.mark.asyncio
async def test_busy_in_later_call_does_not_stop_another_operation(
    tmp_path, monkeypatch
):
    handler = AsyncMock(
        side_effect=[{"status": "completed"}, {"status": "failed", "reason": "busy"}]
    )
    a, _, mcp = agent(
        tmp_path,
        monkeypatch,
        [
            response(
                calls=[
                    call("move", {"command": "avance 10 cm"}, "a"),
                    call("move", {"command": "recue 10 cm"}, "b"),
                ]
            )
        ],
        handler,
    )
    assert "busy" in await a.run("avance e recue")
    assert [c.args[0] for c in mcp.call_tool.await_args_list] == ["move", "move"]
