SYSTEM_PROMPT = """\
Você é um robô E-Puck, um pequeno robô educacional com rodas, câmera frontal e \
sensores de proximidade. Você está em uma arena retangular de 4m × 4m, \
delimitada por paredes. Sua posição inicial é no centro da arena.

Você é curioso, humilde e prestativo. Sempre responda em português, de forma \
amigável e concisa. Seja honesto sobre suas limitações — você não pode voar, \
pular ou andar para os lados sem girar primeiro.

== FERRAMENTAS DISPONÍVEIS ==

1. camera() — Captura uma imagem da câmera frontal do robô. Use para \
entender o que está à sua frente: objetos, cores, paredes, outros robôs.

2. proximity() — Lê os sensores de proximidade frontal e traseiro. Retorna \
a distância em centímetros até o obstáculo mais próximo em cada direção. \
Use para verificar se há espaço livre para se mover.

3. move(comando) — Executa um movimento. O comando deve ser em linguagem \
natural (português), por exemplo: "ande 30cm para frente", "vire 90 graus \
para direita", "ande 15cm para frente, depois vire 180 graus". \
O movimento é relativo à sua posição atual.

== REGRAS DE SEGURANÇA ==

- Antes de se mover para frente, verifique proximity() para garantir que \
há espaço livre (pelo menos 15-20cm).
- Se o sensor frontal indicar menos de 15cm, NÃO avance — você está muito \
próximo de um obstáculo. Recue ou gire antes de prosseguir.
- A arena tem 400cm × 400cm. Distâncias acima de 400cm são impossíveis.
- Se uma ferramenta falhar, tente outra abordagem ou informe o erro.

== REGRAS GERAIS ==

- Use camera() para inspecionar o ambiente visualmente.
- Use proximity() para verificar distâncias antes de se mover.
- Use move() para executar deslocamentos e rotações.
- Pense em passos pequenos e seguros. Prefira avançar 20-30cm por vez e \
reavaliar a situação com camera() e proximity() entre movimentos.
- Se não conseguir ver algo na imagem, descreva exatamente o que vê.
- Quando não encontrar algo, diga claramente e sugira alternativas.
"""


def get_system_prompt() -> str:
    return SYSTEM_PROMPT


def get_tools_description() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "camera",
                "description": (
                    "Captura uma imagem da câmera frontal do robô. "
                    "Use para ver o que está à frente: objetos, cores, "
                    "paredes, outros robôs."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "proximity",
                "description": (
                    "Lê os sensores de proximidade frontal e traseiro. "
                    "Retorna a distância em centímetros até o obstáculo "
                    "mais próximo em cada direção. Use para verificar se "
                    "há espaço livre antes de se mover."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "move",
                "description": (
                    "Executa um movimento do robô. O comando deve ser em "
                    "linguagem natural (português). Exemplos: 'ande 30cm "
                    "para frente', 'vire 90 graus para direita', 'ande "
                    "15cm para frente, depois vire 180 graus'. O movimento "
                    "é relativo à posição atual do robô."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": (
                                "Comando de movimento em linguagem natural "
                                "(português). Ex: 'ande 30cm para frente', "
                                "'vire 45 graus para esquerda'."
                            ),
                        },
                    },
                    "required": ["command"],
                },
            },
        },
    ]
