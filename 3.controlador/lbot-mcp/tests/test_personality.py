import pytest
from harness.personality import SYSTEM_PROMPT, get_system_prompt, get_tools_description


class TestSystemPrompt:
    def test_prompt_mentions_movimento_bem_definido(self):
        assert "MOVIMENTO BEM DEFINIDO" in SYSTEM_PROMPT
        assert "linguagem natural" in SYSTEM_PROMPT

    def test_prompt_mentions_movimento_ambiguo(self):
        assert "MOVIMENTO AMBÍGUO" in SYSTEM_PROMPT
        assert "LBML" in SYSTEM_PROMPT

    def test_prompt_mentions_tarefa(self):
        assert "TAREFA" in SYSTEM_PROMPT
        assert "raciocínio inteligente" in SYSTEM_PROMPT

    def test_prompt_mentions_observe(self):
        assert "observe()" in SYSTEM_PROMPT

    def test_prompt_mentions_distancia_seguranca(self):
        assert "DISTÂNCIA DE SEGURANÇA" in SYSTEM_PROMPT
        assert "20cm" in SYSTEM_PROMPT

    def test_prompt_mentions_centralizacao(self):
        assert "CENTRALIZAÇÃO" in SYSTEM_PROMPT
        assert "centralize" in SYSTEM_PROMPT

    def test_prompt_mentions_limite_arena(self):
        assert "400cm" in SYSTEM_PROMPT
        assert "arena" in SYSTEM_PROMPT

    def test_prompt_mentions_lbml_format(self):
        assert "FORMATO LBML" in SYSTEM_PROMPT
        assert "D<distância>" in SYSTEM_PROMPT

    def test_system_prompt_is_not_empty(self):
        assert len(SYSTEM_PROMPT) > 500

    def test_get_system_prompt_returns_prompt(self):
        assert get_system_prompt() is SYSTEM_PROMPT


class TestToolsDescription:
    def test_tools_include_observe(self):
        tools = get_tools_description()
        assert len(tools) == 4

        names = [t["function"]["name"] for t in tools]
        assert "observe" in names
        assert "camera" in names
        assert "proximity" in names
        assert "move" in names

    def test_observe_tool_has_no_parameters(self):
        tools = get_tools_description()
        observe_tool = next(t for t in tools if t["function"]["name"] == "observe")
        params = observe_tool["function"]["parameters"]
        assert params["type"] == "object"
        assert params["required"] == []

    def test_move_description_mentions_lbml(self):
        tools = get_tools_description()
        move_tool = next(t for t in tools if t["function"]["name"] == "move")
        desc = move_tool["function"]["description"]
        assert "LBML" in desc

    def test_move_description_mentions_both_formats(self):
        tools = get_tools_description()
        move_tool = next(t for t in tools if t["function"]["name"] == "move")
        desc = move_tool["function"]["description"]
        assert "Linguagem natural" in desc or "linguagem natural" in desc.lower()

    def test_tools_have_required_fields(self):
        tools = get_tools_description()
        for tool in tools:
            assert "type" in tool
            assert tool["type"] == "function"
            assert "function" in tool
            assert "name" in tool["function"]
            assert "description" in tool["function"]
            assert "parameters" in tool["function"]
