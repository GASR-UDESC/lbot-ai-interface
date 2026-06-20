"""
Parser LBML e calculador de duracao de comandos de movimento.

Constantes de velocidade mantidas em sincronia com o simulador:
  src/simulator/engine.ts -> ROBOT_SPEED, AVERAGE_MOVE_SPEED, ROTATION_SPEED
"""

import re
import math
from dataclasses import dataclass

# Constantes de velocidade (sincronizadas com simulator/engine.ts)
AVERAGE_MOVE_SPEED_CM_PER_S = 20     # engine.ts linha 8: ROBOT_SPEED * 2/3 = 30 * 2/3 = 20
ROTATION_SPEED_DEG_PER_S = 90        # engine.ts linha 9
INTER_COMMAND_DELAY_S = 0.3          # engine.ts linha 252: await sleep(300)

# Margem de seguranca (+10%) para absorver latencia de rede / startup
SAFETY_MARGIN = 1.10

COMMAND_REGEX = re.compile(r"^([DR])(\d+)([FBLR]);$")

@dataclass
class ParsedCommand:
    type: str       # 'D' (distancia) ou 'R' (rotacao)
    value: int      # centimetros ou graus
    direction: str  # F, B, L, R

def parse_lbml_sequence(input_str: str) -> list[ParsedCommand] | None:
    """
    Parse uma string LBML em lista de comandos.
    Ex: "D30F;R90L;" -> [ParsedCommand('D', 30, 'F'), ParsedCommand('R', 90, 'L')]
    Retorna None se invalido.
    """
    normalized = input_str.replace(" ", "").upper()
    if not normalized:
        return None

    commands: list[ParsedCommand] = []
    parts = [p for p in normalized.split(";") if p]
    for part in parts:
        cmd_str = part + ";"
        m = COMMAND_REGEX.match(cmd_str)
        if not m:
            return None
        commands.append(ParsedCommand(
            type=m.group(1),
            value=int(m.group(2)),
            direction=m.group(3),
        ))
    return commands if commands else None

def command_duration_s(cmd: ParsedCommand) -> float:
    """Duracao esperada de um unico comando em segundos."""
    if cmd.type == 'D':
        return cmd.value / AVERAGE_MOVE_SPEED_CM_PER_S
    else:  # 'R'
        return abs(cmd.value) / ROTATION_SPEED_DEG_PER_S

def calculate_duration_s(lbml: str) -> float | None:
    """
    Calcula a duracao total esperada de uma sequencia LBML em segundos.
    Inclui delay entre comandos e margem de seguranca.
    Retorna None se o LBML for invalido.
    """
    commands = parse_lbml_sequence(lbml)
    if commands is None:
        return None
    total = 0.0
    for cmd in commands:
        total += command_duration_s(cmd)
    # Delay entre comandos (N comandos -> N-1 delays)
    if len(commands) > 1:
        total += INTER_COMMAND_DELAY_S * (len(commands) - 1)
    return total * SAFETY_MARGIN

def move_duration_s(cm: int | float) -> float:
    """Duracao esperada de um movimento linear em segundos, com margem."""
    return (abs(cm) / AVERAGE_MOVE_SPEED_CM_PER_S) * SAFETY_MARGIN

def rotate_duration_s(degrees: int | float) -> float:
    """Duracao esperada de uma rotacao em segundos, com margem."""
    return (abs(degrees) / ROTATION_SPEED_DEG_PER_S) * SAFETY_MARGIN
