SYSTEM_PROMPT = """\
Você é um robô lbot, um pequeno robô educacional com rodas, câmera frontal e \
sensores de proximidade, desenvolvido pela UDESC. Você está em uma arena retangular de 400cm × 400cm, \
delimitada por paredes. Sua posição inicial é no centro da arena.

Você é curioso, humilde e prestativo. Sempre responda em português, de forma \
amigável e concisa. Seja honesto sobre suas limitações — você não pode voar, \
pular ou andar para os lados sem girar primeiro.

Nunca resposa com emojis.
"""

LLM_DESCRIPTION_OVERRIDES = {
    "camera": (
        "Captura uma imagem da câmera frontal do robô. "
        "Use para ver o que está à frente: objetos, cores, "
        "paredes, outros robôs."
    ),
    "move": (
        "Executa um movimento do robô. O comando deve ser em "
        "linguagem natural (português). Exemplos: 'ande 30cm "
        "para frente', 'vire 90 graus para direita', 'ande "
        "15cm para frente, depois vire 180 graus'. O movimento "
        "é relativo à posição atual do robô."
    ),
}


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def build_tools_for_llm(raw_tools: list[dict]) -> list[dict]:
    result = []
    for tool in raw_tools:
        name = tool["name"]
        if name == "translate":
            continue
        result.append({
            "type": "function",
            "function": {
                "name": name,
                "description": LLM_DESCRIPTION_OVERRIDES.get(
                    name, tool.get("description", "")
                ),
                "parameters": tool["inputSchema"],
            },
        })
    return result
