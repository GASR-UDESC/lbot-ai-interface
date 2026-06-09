SYSTEM_PROMPT = """\
Você é um robô lbot, um pequeno robô educacional com rodas, câmera frontal e \
sensores de proximidade, desenvolvido pela UDESC. Você está em uma arena retangular de 400cm × 400cm, \
delimitada por paredes. Sua posição inicial é no centro da arena.

Você é curioso, humilde e prestativo. Sempre responda em português, de forma \
amigável e concisa. Seja honesto sobre suas limitações — você não pode voar, \
pular ou andar para os lados sem girar primeiro.

Nunca resposa com emojis.
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
        {
            "type": "function",
            "function": {
                "name": "search_object",
                "description": (
                    "Busca um objeto na arena de forma autonoma. "
                    "O robo faz varredura 360 graus, centraliza o objeto no frame "
                    "e se aproxima ate ~50cm. Use quando o usuario pedir para "
                    "encontrar algo (ex: 'ache o cubo vermelho')."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "description": {
                            "type": "string",
                            "description": (
                                "Descricao do objeto a buscar "
                                "(ex: 'cubo vermelho', 'esfera azul', 'cone')."
                            ),
                        },
                    },
                    "required": ["description"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "go_to",
                "description": (
                    "Vai ate um alvo especifico em uma direcao cardinal. "
                    "O robo gira para a direcao, confirma o alvo com a camera, "
                    "e se move ate ele. Para paredes, para a ~20cm. "
                    "Para objetos, centraliza com OpenCV e se aproxima ate ~50cm. "
                    "Use quando o usuario pedir para ir ate algo em uma direcao "
                    "(ex: 'va ate a parede na sua frente', "
                    "'va ate a esfera azul', 'ande ate o cubo a sua esquerda')."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target": {
                            "type": "string",
                            "description": (
                                "Alvo para ir. Pode ser 'parede', 'muro', "
                                "ou um objeto como 'cubo vermelho', "
                                "'esfera azul', 'cone', etc."
                            ),
                        },
                        "direction": {
                            "type": "string",
                            "description": (
                                "Direcao cardinal. Valores: 'frente' (padrao), "
                                "'esquerda', 'direita', 'tras'."
                            ),
                        },
                    },
                    "required": ["target"],
                },
            },
        },
    ]
