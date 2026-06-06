import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from harness.agent import (
    ReActAgent,
    _extract_proximity_from_messages,
    _is_forward_command,
    _is_rotation_command,
    _parse_lbml_command,
    _parsed_to_lbml,
    _reduce_step,
    _summarize_messages,
)


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


class TestReActAgentObserveTool:
    @pytest.fixture
    def mock_mcp_client_observe(self):
        client = MagicMock()
        return client

    @pytest.fixture
    def observe_success_payload(self):
        return json.dumps({
            "image": "iVBORw0KGgo=" + "A" * 200,
            "render_method": "2d",
            "robot_position": {"x": 1.0, "z": 2.0, "rotation": 90.0},
            "proximity": {"frente": 50.0, "tras": 200.0},
        })

    @pytest.fixture
    def observe_camera_error_payload(self):
        return json.dumps({
            "camera_error": "camera indisponivel",
            "proximity": {"frente": 50.0, "tras": 200.0},
        })

    @pytest.fixture
    def observe_proximity_error_payload(self):
        return json.dumps({
            "image": "iVBORw0KGgo=" + "A" * 200,
            "render_method": "2d",
            "robot_position": {"x": 1.0, "z": 2.0, "rotation": 90.0},
            "proximity_error": "sensor indisponivel",
        })

    @pytest.fixture
    def observe_both_error_payload(self):
        return json.dumps({
            "camera_error": "camera fail",
            "proximity_error": "prox fail",
        })

    @pytest.mark.asyncio
    async def test_observe_success_injects_image_and_proximity(self, mock_mcp_client_observe, observe_success_payload):
        mock_mcp_client_observe.call_tool = AsyncMock(return_value=observe_success_payload)
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "Observando..."
            tc = MagicMock()
            tc.id = "tc-obs-1"
            tc.function.name = "observe"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Vejo um objeto a 50cm."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client_observe, on_event=on_event)
            result = await agent.run("observe a sala")

        assert result == "Vejo um objeto a 50cm."

        user_messages_with_image = [
            m for m in agent._messages
            if m.get("role") == "user" and isinstance(m.get("content"), list)
        ]
        assert len(user_messages_with_image) == 1
        content = user_messages_with_image[0]["content"]
        has_image = any(
            isinstance(part, dict) and part.get("type") == "image_url"
            for part in content
        )
        assert has_image

        has_prox_text = any(
            isinstance(part, dict)
            and part.get("type") == "text"
            and "50" in part.get("text", "")
            for part in content
        )
        assert has_prox_text

    @pytest.mark.asyncio
    async def test_observe_camera_error_only_proximity(self, mock_mcp_client_observe, observe_camera_error_payload):
        mock_mcp_client_observe.call_tool = AsyncMock(return_value=observe_camera_error_payload)

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "Observando..."
            tc = MagicMock()
            tc.id = "tc-obs-2"
            tc.function.name = "observe"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Câmera falhou mas proximidade ok."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client_observe)
            result = await agent.run("observe")

        assert result == "Câmera falhou mas proximidade ok."

        user_messages_with_image = [
            m for m in agent._messages
            if m.get("role") == "user" and isinstance(m.get("content"), list)
        ]
        assert len(user_messages_with_image) == 0

    @pytest.mark.asyncio
    async def test_observe_proximity_error_only_camera(self, mock_mcp_client_observe, observe_proximity_error_payload):
        mock_mcp_client_observe.call_tool = AsyncMock(return_value=observe_proximity_error_payload)

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "Observando..."
            tc = MagicMock()
            tc.id = "tc-obs-3"
            tc.function.name = "observe"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Imagem ok, proximidade falhou."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client_observe)
            result = await agent.run("observe")

        assert result == "Imagem ok, proximidade falhou."

        user_messages_with_image = [
            m for m in agent._messages
            if m.get("role") == "user" and isinstance(m.get("content"), list)
        ]
        assert len(user_messages_with_image) == 1

        content = user_messages_with_image[0]["content"]
        has_prox_error_text = any(
            isinstance(part, dict)
            and part.get("type") == "text"
            and "sensor indisponivel" in part.get("text", "")
            for part in content
        )
        assert has_prox_error_text

    @pytest.mark.asyncio
    async def test_observe_both_error(self, mock_mcp_client_observe, observe_both_error_payload):
        mock_mcp_client_observe.call_tool = AsyncMock(return_value=observe_both_error_payload)

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "Observando..."
            tc = MagicMock()
            tc.id = "tc-obs-4"
            tc.function.name = "observe"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Ambos falharam."
            msg2.tool_calls = None
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client_observe)
            result = await agent.run("observe")

        assert result == "Ambos falharam."

    @pytest.mark.asyncio
    async def test_observe_increments_steps_correctly(self, mock_mcp_client_observe, observe_success_payload):
        mock_mcp_client_observe.call_tool = AsyncMock(return_value=observe_success_payload)
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = None
            tc1 = MagicMock()
            tc1.id = "tc-1"
            tc1.function.name = "observe"
            tc1.function.arguments = "{}"
            msg1.tool_calls = [tc1]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = None
            tc2 = MagicMock()
            tc2.id = "tc-2"
            tc2.function.name = "observe"
            tc2.function.arguments = "{}"
            msg2.tool_calls = [tc2]
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "tool_calls"

            msg3 = MagicMock()
            msg3.content = "Feito."
            msg3.tool_calls = None
            choice3 = MagicMock()
            choice3.message = msg3
            choice3.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
                MagicMock(choices=[choice3]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client_observe, on_event=on_event)
            result = await agent.run("observe twice")

        assert result == "Feito."
        llm_request_events = [e for e in events if e[0] == "llm_request"]
        assert len(llm_request_events) == 3


class TestReActAgentMaxSteps:
    def test_max_steps_default_is_50(self):
        mock_client = MagicMock()
        agent = ReActAgent(mock_client)
        assert agent._max_steps == 50

    def test_max_steps_override(self):
        mock_client = MagicMock()
        agent = ReActAgent(mock_client, max_steps=100)
        assert agent._max_steps == 100


# ---------------------------------------------------------------------------
# Fase 02: LBML helpers and command validation
# ---------------------------------------------------------------------------

class TestLBMLHelpers:
    def test_parse_single_forward(self):
        result = _parse_lbml_command("D30F;")
        assert result == [{"type": "D", "value": 30, "direction": "F"}]

    def test_parse_single_rotation(self):
        result = _parse_lbml_command("R90L;")
        assert result == [{"type": "R", "value": 90, "direction": "L"}]

    def test_parse_sequence(self):
        result = _parse_lbml_command("D50F;R90L;D30B;")
        assert len(result) == 3
        assert result[0] == {"type": "D", "value": 50, "direction": "F"}
        assert result[1] == {"type": "R", "value": 90, "direction": "L"}
        assert result[2] == {"type": "D", "value": 30, "direction": "B"}

    def test_parse_empty(self):
        result = _parse_lbml_command("")
        assert result == []

    def test_parse_non_lbml(self):
        result = _parse_lbml_command("ande 30cm para frente")
        assert result == []

    def test_is_forward_true(self):
        parsed = [{"type": "D", "value": 50, "direction": "F"}]
        assert _is_forward_command(parsed)

    def test_is_forward_false_backward(self):
        parsed = [{"type": "D", "value": 50, "direction": "B"}]
        assert not _is_forward_command(parsed)

    def test_is_forward_mixed(self):
        parsed = [
            {"type": "R", "value": 90, "direction": "L"},
            {"type": "D", "value": 30, "direction": "F"},
        ]
        assert _is_forward_command(parsed)

    def test_is_rotation_true(self):
        parsed = [{"type": "R", "value": 90, "direction": "L"}]
        assert _is_rotation_command(parsed)

    def test_is_rotation_false_mixed(self):
        parsed = [
            {"type": "R", "value": 90, "direction": "L"},
            {"type": "D", "value": 30, "direction": "F"},
        ]
        assert not _is_rotation_command(parsed)

    def test_is_rotation_empty(self):
        assert not _is_rotation_command([])

    def test_reduce_step_single(self):
        parsed = [{"type": "D", "value": 20, "direction": "F"}]
        result = _reduce_step(parsed, 10)
        assert result[0]["value"] == 10

    def test_reduce_step_sequence(self):
        parsed = [
            {"type": "D", "value": 20, "direction": "F"},
            {"type": "R", "value": 90, "direction": "L"},
            {"type": "D", "value": 15, "direction": "F"},
            {"type": "D", "value": 10, "direction": "B"},
        ]
        result = _reduce_step(parsed, 10)
        assert result[0]["value"] == 10
        assert result[1]["value"] == 90
        assert result[2]["value"] == 10
        assert result[3]["value"] == 10

    def test_reduce_step_below_max(self):
        parsed = [{"type": "D", "value": 5, "direction": "F"}]
        result = _reduce_step(parsed, 10)
        assert result[0]["value"] == 5

    def test_parsed_to_lbml(self):
        parsed = [
            {"type": "D", "value": 30, "direction": "F"},
            {"type": "R", "value": 90, "direction": "L"},
        ]
        result = _parsed_to_lbml(parsed)
        assert result == "D30F;R90L;"

    def test_parsed_to_lbml_empty(self):
        assert _parsed_to_lbml([]) == ""


class TestProximityExtraction:
    def test_extract_from_proximity_text(self):
        messages = [
            {"role": "tool", "content": "Frente: 50 cm | Trás: 200 cm"},
        ]
        result = _extract_proximity_from_messages(messages)
        assert result == {"frente": 50.0, "tras": 200.0}

    def test_extract_from_observe_text(self):
        messages = [
            {
                "role": "tool",
                "content": "Imagem capturada com sucesso. Proximidade — Frente: 50.0 cm | Trás: 200.0 cm.",
            },
        ]
        result = _extract_proximity_from_messages(messages)
        assert result == {"frente": 50.0, "tras": 200.0}

    def test_extract_from_user_message_with_proximity(self):
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Aqui está a imagem da câmera frontal do robô: Proximidade — Frente: 35 cm | Trás: 200 cm.",
                    },
                    {"type": "image_url", "image_url": {"url": "data:image/png;base64,abc"}},
                ],
            },
        ]
        result = _extract_proximity_from_messages(messages)
        assert result == {"frente": 35.0, "tras": 200.0}

    def test_no_proximity_found(self):
        messages = [
            {"role": "tool", "content": "Comando executado: D30F; (LBML direto)"},
        ]
        result = _extract_proximity_from_messages(messages)
        assert result is None

    def test_empty_messages(self):
        result = _extract_proximity_from_messages([])
        assert result is None

    def test_extract_latest_proximity(self):
        messages = [
            {"role": "tool", "content": "Frente: 100 cm | Trás: 200 cm"},
            {"role": "tool", "content": "Comando executado: D30F;"},
            {"role": "tool", "content": "Frente: 50 cm | Trás: 200 cm"},
        ]
        result = _extract_proximity_from_messages(messages)
        assert result == {"frente": 50.0, "tras": 200.0}


class TestCommandModification:
    def test_blocks_forward_when_front_lte_20(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 20 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("D30F;")
        assert command is None
        assert "Bloqueado" in msg
        assert "20cm" in msg.lower()

    def test_reduces_to_10_when_front_between_20_40(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 35 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("D20F;")
        assert command == "D10F;"
        assert "reduzido" in msg.lower()

    def test_reduces_to_15_when_front_between_40_80(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 60 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("D20F;")
        assert command == "D15F;"

    def test_no_modification_when_front_gt_80(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 100 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("D20F;")
        assert command == "D20F;"
        assert msg is None

    def test_backward_not_blocked(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("D20B;")
        assert command == "D20B;"
        assert msg is None

    def test_rotation_not_blocked(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("R90L;")
        assert command == "R90L;"
        assert msg is None

    def test_fallback_when_no_proximity_reading(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        command, msg = agent._validate_and_adjust_move("D20F;")
        assert command == "D20F;"
        assert msg is None

    def test_non_lbml_passes_through(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        command, msg = agent._validate_and_adjust_move("ande 30cm para frente")
        assert command == "ande 30cm para frente"
        assert msg is None


# ---------------------------------------------------------------------------
# Fase 03: Proximity goal, loop detection, max steps
# ---------------------------------------------------------------------------

_OBJECT_CENTERED_KEYWORDS = [
    "centralizado", "centralizei", "no centro",
    "esta centralizado", "objeto esta no centro",
]


class TestProximityGoal:
    def test_goal_when_front_in_range_15_25(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 20 cm | Trás: 200 cm"}
        )
        agent._object_was_centered = True
        msg = agent._check_proximity_goal()
        assert msg is not None
        assert "CONTROLE AUTOMATICO" in msg
        assert "15-25cm" in msg
        assert agent._goal_achieved is True
        assert agent._last_front_proximity == 20.0

    def test_no_goal_when_front_above_25(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 30 cm | Trás: 200 cm"}
        )
        msg = agent._check_proximity_goal()
        assert msg is None
        assert agent._goal_achieved is False

    def test_alert_when_front_below_15_not_centered(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._object_was_centered = False
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        msg = agent._check_proximity_goal()
        assert msg is not None
        assert "muito perto" in msg.lower()
        assert agent._goal_achieved is False

    def test_alert_when_front_below_15_was_centered(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._object_was_centered = True
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        msg = agent._check_proximity_goal()
        assert msg is not None
        assert "ALERTA" in msg
        assert "passou do alvo" in msg.lower()
        assert agent._object_was_centered is False
        assert agent._goal_achieved is False

    def test_no_proximity_returns_none(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._check_proximity_goal()
        assert msg is None

    def test_updates_proximity_state(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._messages.append(
            {"role": "tool", "content": "Frente: 25 cm | Trás: 200 cm"}
        )
        agent._check_proximity_goal()
        assert agent._last_front_proximity == 25.0
        assert agent._last_back_proximity == 200.0


class TestLoopDetection:
    def test_resets_on_displacement_command(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 5
        parsed = _parse_lbml_command("D30F;")
        msg = agent._check_rotation_loop("D30F;", parsed)
        assert msg is None
        assert agent._consecutive_rotations == 0

    def test_resets_on_mixed_command(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 5
        parsed = _parse_lbml_command("D30F;R90L;")
        msg = agent._check_rotation_loop("D30F;R90L;", parsed)
        assert msg is None
        assert agent._consecutive_rotations == 0

    def test_increments_on_rotation(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        parsed = _parse_lbml_command("R5L;")
        agent._check_rotation_loop("R5L;", parsed)
        assert agent._consecutive_rotations == 1
        agent._check_rotation_loop("R5R;", parsed)
        assert agent._consecutive_rotations == 2

    def test_alerts_after_10_consecutive_rotations(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 9
        parsed = _parse_lbml_command("R5L;")
        msg = agent._check_rotation_loop("R5L;", parsed)
        assert msg is not None
        assert "CONTROLE AUTOMATICO" in msg
        assert "10 rotacoes consecutivas" in msg.lower()
        assert agent._consecutive_rotations == 0

    def test_no_alert_before_10(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 8
        parsed = _parse_lbml_command("R5L;")
        msg = agent._check_rotation_loop("R5L;", parsed)
        assert msg is None
        assert agent._consecutive_rotations == 9

    def test_empty_parsed_returns_none(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._check_rotation_loop("ande 30cm", [])
        assert msg is None

    def test_backward_command_resets(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 7
        parsed = _parse_lbml_command("D20B;")
        msg = agent._check_rotation_loop("D20B;", parsed)
        assert msg is None
        assert agent._consecutive_rotations == 0


class TestStateReset:
    def test_reset_clears_state_trackers(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._last_front_proximity = 50.0
        agent._last_back_proximity = 200.0
        agent._last_position = {"x": 1.0, "z": 2.0, "rotation": 90.0}
        agent._consecutive_rotations = 5
        agent._object_was_centered = True
        agent._goal_achieved = True

        agent.reset()

        assert agent._last_front_proximity is None
        assert agent._last_back_proximity is None
        assert agent._last_position is None
        assert agent._consecutive_rotations == 0
        assert agent._object_was_centered is False
        assert agent._goal_achieved is False


class TestObjectCenteredDetection:
    @pytest.mark.asyncio
    async def test_detects_centered_from_llm_text(self, mock_mcp_client):
        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            msg = MagicMock()
            msg.content = "o objeto esta centralizado na camera, vou me aproximar"
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = "stop"
            mock_llm.chat.completions.create.return_value = MagicMock(choices=[choice])
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client)
            await agent.run("aproxime do cubo")
            assert agent._object_was_centered is True

    @pytest.mark.asyncio
    async def test_detects_centered_variant_centralizei(self, mock_mcp_client):
        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            msg = MagicMock()
            msg.content = "centralizei o objeto no centro da tela"
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = "stop"
            mock_llm.chat.completions.create.return_value = MagicMock(choices=[choice])
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client)
            await agent.run("centralize o cubo")
            assert agent._object_was_centered is True

    @pytest.mark.asyncio
    async def test_no_centered_detection_without_keyword(self, mock_mcp_client):
        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()
            msg = MagicMock()
            msg.content = "vejo um cubo vermelho"
            msg.tool_calls = None
            choice = MagicMock()
            choice.message = msg
            choice.finish_reason = "stop"
            mock_llm.chat.completions.create.return_value = MagicMock(choices=[choice])
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client)
            await agent.run("observe a sala")
            assert agent._object_was_centered is False

    @pytest.mark.asyncio
    async def test_detects_centered_with_tool_calls(self, mock_mcp_client):
        events: list[tuple[str, dict]] = []

        def on_event(event: str, data: dict):
            events.append((event, data))

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            msg1 = MagicMock()
            msg1.content = "objeto esta centralizado, vou medir distancia"
            tc = MagicMock()
            tc.id = "tc-1"
            tc.function.name = "proximity"
            tc.function.arguments = "{}"
            msg1.tool_calls = [tc]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            msg2 = MagicMock()
            msg2.content = "Distancia medida, continuando."
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
            await agent.run("aproxime do cubo")
            assert agent._object_was_centered is True


# ---------------------------------------------------------------------------
# Fase 04: Object loss detection and recovery
# ---------------------------------------------------------------------------


class TestObjectLossDetection:
    def test_no_loss_on_first_reading(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._detect_object_loss(50.0, None)
        assert msg is None

    def test_no_loss_when_distance_normal(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._detect_object_loss(22.0, 20.0)
        assert msg is None

    def test_detects_loss_when_front_jumps_from_under_25_to_over_30(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._object_was_centered = True
        agent._consecutive_rotations = 5
        msg = agent._detect_object_loss(45.0, 20.0)
        assert msg is not None
        assert "CONTROLE AUTOMATICO" in msg
        assert "ALERTA DE PERDA DE OBJETO" in msg
        assert "saltou de 20cm para 45cm" in msg.lower()
        assert "Recue 20cm" in msg
        assert agent._object_was_centered is False
        assert agent._consecutive_rotations == 0

    def test_detects_loss_when_front_jumps_from_under_25_to_over_30_boundary(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._detect_object_loss(31.0, 25.0)
        assert msg is not None
        assert "ALERTA DE PERDA DE OBJETO" in msg

    def test_no_loss_when_already_distant(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        msg = agent._detect_object_loss(45.0, 40.0)
        assert msg is None

    def test_resets_object_centered_on_loss(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._object_was_centered = True
        agent._detect_object_loss(50.0, 20.0)
        assert agent._object_was_centered is False

    def test_resets_rotation_counter_on_loss(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._consecutive_rotations = 8
        agent._detect_object_loss(50.0, 20.0)
        assert agent._consecutive_rotations == 0

    def test_overshooting_in_proximity_goal_uses_recovery_message(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._object_was_centered = True
        agent._consecutive_rotations = 3
        agent._messages.append(
            {"role": "tool", "content": "Frente: 10 cm | Trás: 200 cm"}
        )
        msg = agent._check_proximity_goal()
        assert msg is not None
        assert "ALERTA DE PERDA DE OBJETO" in msg
        assert "overshooting" in msg.lower()
        assert "Recue 20cm" in msg
        assert agent._object_was_centered is False
        assert agent._consecutive_rotations == 0

    def test_loss_check_runs_before_state_update_in_proximity_goal(self, mock_mcp_client):
        agent = ReActAgent(mock_mcp_client)
        agent._last_front_proximity = 20.0
        agent._messages.append(
            {"role": "tool", "content": "Frente: 50 cm | Trás: 200 cm"}
        )
        msg = agent._check_proximity_goal()
        assert msg is not None
        assert "ALERTA DE PERDA DE OBJETO" in msg
        assert agent._last_front_proximity == 50.0


class TestRecoveryIntegration:
    @pytest.mark.asyncio
    async def test_loss_message_injected_into_context(self, mock_mcp_client):
        observe_near = json.dumps({
            "proximity": {"frente": 20.0, "tras": 200.0},
        })
        observe_far = json.dumps({
            "proximity": {"frente": 50.0, "tras": 200.0},
        })
        mock_mcp_client.call_tool = AsyncMock()
        mock_mcp_client.call_tool.side_effect = [observe_near, observe_far]

        with patch("harness.agent.OpenAI") as MockOpenAI:
            mock_llm = MagicMock()

            # Round 1: LLM calls observe → proximity 20 (sets _last_front_proximity=20)
            msg1 = MagicMock()
            msg1.content = "objeto esta centralizado, vou observar"
            tc1 = MagicMock()
            tc1.id = "tc-loss-1"
            tc1.function.name = "observe"
            tc1.function.arguments = "{}"
            msg1.tool_calls = [tc1]
            choice1 = MagicMock()
            choice1.message = msg1
            choice1.finish_reason = "tool_calls"

            # Round 2: LLM calls observe again → proximity 50 (detecta perda)
            msg2 = MagicMock()
            msg2.content = None
            tc2 = MagicMock()
            tc2.id = "tc-loss-2"
            tc2.function.name = "observe"
            tc2.function.arguments = "{}"
            msg2.tool_calls = [tc2]
            choice2 = MagicMock()
            choice2.message = msg2
            choice2.finish_reason = "tool_calls"

            # Round 3: LLM finishes
            msg3 = MagicMock()
            msg3.content = "Perdi o objeto, vou recuar."
            msg3.tool_calls = None
            choice3 = MagicMock()
            choice3.message = msg3
            choice3.finish_reason = "stop"

            mock_llm.chat.completions.create.side_effect = [
                MagicMock(choices=[choice1]),
                MagicMock(choices=[choice2]),
                MagicMock(choices=[choice3]),
            ]
            MockOpenAI.return_value = mock_llm

            agent = ReActAgent(mock_mcp_client)
            await agent.run("aproxime do cubo")

            loss_messages = [
                m for m in agent._messages
                if m.get("role") == "user"
                and isinstance(m.get("content"), str)
                and "ALERTA DE PERDA DE OBJETO" in m.get("content", "")
            ]
            assert len(loss_messages) >= 1
            assert "Recue 20cm" in loss_messages[0]["content"]
