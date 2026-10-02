"""Versioned development/held-out tasks; labels are never passed to the harness."""

import json
from pathlib import Path

cases = []


def cube(color, x=0, z=120, id="target"):
    return {
        "id": id,
        "type": "cube",
        "x": x,
        "z": z,
        "color": color,
        "size": {"width": 20, "height": 20, "depth": 20},
    }


def add(category, prompt, expected_tools, objects=None, **expected):
    index = sum(c["category"] == category for c in cases)
    spawn = (
        [(0, 0), (20, -20), (-20, 10)][index % 3] if category != "movement" else (0, 0)
    )
    objects = [
        {**o, "x": o["x"] + spawn[0], "z": o["z"] + spawn[1]} for o in (objects or [])
    ]
    if category == "sensors":
        expected["readings"] = {"frente": 74.9 + index * 5, "tras": 184.9 + spawn[1]}
    cases.append(
        {
            "id": f"{category}-{index + 1:02d}",
            "split": "development" if index < 5 else "acceptance",
            "category": category,
            "prompt": prompt,
            "expected_tools": expected_tools,
            "scenario": {
                "objects": objects or [],
                "pose": {"x": spawn[0], "z": spawn[1], "rotation": 0},
            },
            "expected": expected,
        }
    )


for p in [
    "Olá!",
    "Oi, tudo bem?",
    "Qual é seu nome?",
    "Quem é você?",
    "O que você é?",
    "Bom dia!",
    "Boa tarde!",
    "Você consegue voar?",
    "Você é um robô?",
    "Você tem rodas?",
]:
    add("conversation", p, [])
for i, p in enumerate(
    [
        "O que você vê à frente?",
        "Descreva a imagem da câmera.",
        "Qual objeto está na sua frente?",
        "Observe o ambiente à frente.",
        "Que cor tem o objeto visível?",
        "Mostre o que está vendo agora.",
        "Olhe pela câmera e descreva a cena.",
        "Existe um objeto visível à frente?",
        "Descreva o objeto que aparece na imagem.",
        "Veja qual é a cor do cubo na frente.",
    ]
):
    color, word = [("#ff0000", "vermelh"), ("#ffff00", "amarel")][i % 2]
    add("observation", p, ["camera"], [cube(color)], text_contains=word)
for i, p in enumerate(
    [
        "Meça a distância à frente.",
        "Qual a distância do obstáculo frontal?",
        "Leia os sensores de proximidade.",
        "Quanto espaço tenho à frente?",
        "Existe um obstáculo próximo pelo sensor?",
        "Meça a proximidade frontal.",
        "Qual é a distância do que está atrás?",
        "Verifique o sensor traseiro.",
        "Informe a distância do obstáculo à frente em centímetros.",
        "Leia a distância frontal e traseira.",
    ]
):
    add("sensors", p, ["proximity"], [cube("#ff0000", z=100 + i * 5)])
for i, p in enumerate(
    [
        "Ande 20 cm para frente.",
        "Avance 30 centímetros.",
        "Recue 10 cm.",
        "Vire 90 graus para a esquerda.",
        "Gire 180 graus para a direita.",
        "Ande 25 cm para frente e vire 90 graus para esquerda.",
        "Avance 15 cm e depois vire 90 graus para direita.",
        "Vire 90 graus para esquerda e ande 20 cm para frente.",
        "Faça um giro de 360 graus para a esquerda.",
        "Ande 20 cm para frente e depois 10 cm para trás.",
    ]
):
    poses = [
        (0, 20, 0),
        (0, 30, 0),
        (0, -10, 0),
        (0, 0, 90),
        (0, 0, -180),
        (0, 25, 90),
        (0, 15, -90),
        (20, 0, 90),
        (0, 0, 360),
        (0, 10, 0),
    ]
    add("movement", p, ["move"], pose=poses[i])
for i, p in enumerate(
    [
        "Procure o cubo vermelho.",
        "Encontre o cubo amarelo.",
        "Busque um cubo vermelho na arena.",
        "Localize o cubo amarelo.",
        "Procure um cubo vermelho ao redor.",
        "Veja se encontra um cubo amarelo na arena.",
        "Procure o cubo vermelho e diga se localizou.",
        "Encontre um cubo amarelo sem chegar perto dele.",
        "Procure o cubo azul.",
        "Busque uma esfera roxa na arena.",
    ]
):
    absent = i >= 8
    color = "#ff0000" if i % 2 == 0 else "#ffff00"
    add(
        "search",
        p,
        ["search_object"],
        [] if absent else [cube(color, x=60 if i % 3 else -60, z=110)],
        detected=not absent,
        approached=False,
    )
for i, p in enumerate(
    [
        "Chegue perto do cubo vermelho.",
        "Aproxime do cubo amarelo e pare a 50 cm.",
        "Vá até o cubo vermelho mantendo 50 cm.",
        "Aproxime do obstáculo à frente e pare a 50 cm.",
        "Chegue a 50 cm do obstáculo frontal.",
        "Aproxime do cubo amarelo a 50 cm.",
        "Chegue a 40 cm do cubo vermelho.",
        "Aproxime do obstáculo à frente a 60 cm.",
        "Aproxime do cubo vermelho, mas pare se houver bloqueio.",
        "Chegue perto do cubo amarelo, sem contornar obstáculos.",
    ]
):
    front = i in (3, 4, 7)
    blocked = i >= 8
    color = "#ffff00" if i in (1, 5, 9) else "#ff0000"
    objects = [cube(color, z=120)]
    if blocked:
        objects.append(cube("#0000ff", z=30, id="blocker"))
    add(
        "approach",
        p,
        ["approach"],
        objects,
        approached=not blocked,
        stop_distance_cm=40 if i == 6 else 60 if i == 7 else 50,
    )
Path(__file__).with_name("cases.json").write_text(
    json.dumps(cases, ensure_ascii=False, indent=2) + "\n"
)
