import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from harness.agent import ReActAgent, _summarize_messages


@pytest.fixture
def mock_mcp_client():
    client = MagicMock()
    client.call_tool = AsyncMock(return_value="ok")
    return client


class TestSummarizeMessages:
    def test_truncates_long_text(self):
        msgs = [{"role": "user", "content": "x" * 300}]
        result = _summarize_messages(msgs)
        assert result[0]["content"].endswith("...")
        assert len(result[0]["content"]) == 203

    def test_replaces_image_url_with_placeholder(self):
        msgs = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "olhe"},
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc123"}},
                ],
            }
        ]
        result = _summarize_messages(msgs)
        assert "[imagem]" in result[0]["content"]
        assert "olhe" in result[0]["content"]

    def test_handles_system_and_tool_messages(self):
        msgs = [
            {"role": "system", "content": "sys prompt"},
            {"role": "assistant", "content": "hi"},
            {"role": "tool", "content": "result"},
        ]
        result = _summarize_messages(msgs)
        assert len(result) == 3
        assert result[0]["role"] == "system"


class TestReActAgentEvents:
    @pytest.mark.asyncio
    async def test_emits_goal_and_final_answer(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            mock_message = MagicMock()
            mock_message.content = "Resposta final"
            mock_message.tool_calls = None
            mock_choice = MagicMock()
            mock_choice.message = mock_message
            mock_choice.finish_reason = "stop"
            mock_llm.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            result = await agent.run("ola")

        assert result == "Resposta final"
        event_names = [e[0] for e in events]
        assert "goal" in event_names
        assert "llm_request" in event_names
        assert "llm_response" in event_names
        assert "final_answer" in event_names

        goal_event = next(e for e in events if e[0] == "goal")
        assert goal_event[1]["goal"] == "ola"

        final_event = next(e for e in events if e[0] == "final_answer")
        assert final_event[1]["content"] == "Resposta final"

    @pytest.mark.asyncio
    async def test_emits_tool_call_and_tool_result(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            # First response: tool call
            msg1 = MagicMock()
            msg1.content = "Vou medir a distância."
            tc = MagicMock()
            tc.id = "tc-1"
            tc.function.name = "proximity"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            # Second response: final answer
            msg2 = MagicMock()
            msg2.content = "Está livre."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            result = await agent.run("qual a distancia")

        assert result == "Está livre."
        event_names = [e[0] for e in events]
        assert event_names.count("llm_request") == 2
        assert event_names.count("llm_response") == 2
        assert "tool_call" in event_names
        assert "tool_result" in event_names
        assert "final_answer" in event_names

        tool_call_event = next(e for e in events if e[0] == "tool_call")
        assert tool_call_event[1]["tool"] == "proximity"

        tool_result_event = next(e for e in events if e[0] == "tool_result")
        assert tool_result_event[1]["result"] == "ok"

    @pytest.mark.asyncio
    async def test_emits_error_on_llm_failure(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            mock_llm.chat.completions.create.side_effect = RuntimeError("API down")
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            result = await agent.run("teste")

        assert "API down" in result
        error_event = next(e for e in events if e[0] == "error")
        assert "API down" in error_event[1]["error"]

    @pytest.mark.asyncio
    async def test_emits_retry_when_image_not_supported(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            # First call fails with image error
            error = RuntimeError("Model does not support image input")
            # Second call succeeds
            msg = MagicMock()
            msg.content = "Resposta"
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                error,
                MagicMock(choices=[choice]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            result = await agent.run("teste")

        assert result == "Resposta"
        event_names = [e[0] for e in events]
        assert "llm_request_retry" in event_names

        retry_event = next(e for e in events if e[0] == "llm_request_retry")
        assert "imagem" in retry_event[1]["reason"].lower()

    @pytest.mark.asyncio
    async def test_no_events_when_callback_is_none(self, mock_mcp_client):
        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            msg = MagicMock()
            msg.content = "ok"
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = "stop"
            mock_llm.chat.completions.create.return_value = MagicMock(choices=[choice])
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=None)
            result = await agent.run("teste")

        assert result == "ok"
        # If no callback is registered, no exception should be raised

    @pytest.mark.asyncio
    async def test_truncates_tool_result_in_event(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        long_result = "x" * 500
        mock_mcp_client.call_tool = AsyncMock(return_value=long_result)

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = None
            tc = MagicMock()
            tc.id = "tc-1"
            tc.function.name = "camera"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "feito"
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            await agent.run("foto")

        tool_result_event = next(e for e in events if e[0] == "tool_result")
        displayed = tool_result_event[1]["result"]
        assert displayed.endswith("...")
        assert len(displayed) == 203


class TestReActAgentCameraTool:
    @pytest.mark.asyncio
    async def test_camera_success_with_base64(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        camera_payload = json.dumps({
            "image": "iVBORw0KGgo=" + "A" * 200,  # valid PNG prefix-ish + padding
            "render_method": "2d",
            "robot_position": {"x": 1.0, "z": 2.0, "rotation": 90.0},
        })
        mock_mcp_client.call_tool = AsyncMock(return_value=camera_payload)

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "Tirando foto..."
            tc = MagicMock()
            tc.id = "tc-1"
            tc.function.name = "camera"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Foto tirada."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client, on_event=on_event)
            result = await agent.run("tire uma foto")

        assert result == "Foto tirada."
        assert "tool_call" in [e[0] for e in events]
        assert "tool_result" in [e[0] for e in events]
