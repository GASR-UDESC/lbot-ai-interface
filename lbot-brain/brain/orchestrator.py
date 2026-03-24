from __future__ import annotations

import json
from typing import Any

from brain.commands.models import BAD_DEFINED_MOVEMENT, LOCATION_MOVEMENT, SPEAK, VIEW, WELL_DEFINED_MOVEMENT
from brain.modules.camera import Camera
from brain.modules.esp32 import ESP32
from brain.modules.llm import LLM
from brain.modules.microphone import Microphone
from brain.modules.movement_translator import MovementTranslatorV7
from brain.modules.speaker import Speaker

ALLOWED_COMMANDS = {
    "WELL_DEFINED_MOVEMENT",
    "BAD_DEFINED_MOVEMENT",
    "LOCATION_MOVEMENT",
    "VIEW",
    "SPEAK",
}

PLANNER_SYSTEM_PROMPT = """Voce e o cerebro do robo LBOT.

Seu trabalho e converter a entrada do usuario em uma lista JSON de comandos para execucao sequencial.

## Entrada recebida (apos este system prompt)
Voce recebera um JSON neste formato:

{
  "past_commands": [],
  "past_messages": [],
  "message": ""
}

### Significado dos campos
- past_commands: historico de comandos ja gerados/executados na sessao. Alguns itens podem conter output.
- past_messages: historico de mensagens trocadas na sessao (usuario e assistente/sistema de aplicacao, quando disponivel).
- message: mensagem atual do usuario (a principal para decidir a proxima acao).

Observacao: se a aplicacao enviar past_commads em vez de past_commands, trate como equivalente.

## Objetivo
Dado o JSON de entrada, retornar somente um array JSON com comandos do LBOT, em ordem de execucao.

## Comandos permitidos
Voce so pode usar:

- WELL_DEFINED_MOVEMENT -> movimento claramente especificado e executavel.
- BAD_DEFINED_MOVEMENT -> movimento ambiguo/incompleto.
- LOCATION_MOVEMENT -> deslocamento para destino/local.
- VIEW -> percepcao visual do ambiente.
- SPEAK -> conversa, confirmacao, explicacao, limitacoes, pedido de esclarecimento.

## Formato de saida (obrigatorio)
Retorne apenas:

[
  {
    "command": "SPEAK",
    "input": "..."
  }
]

### Regras de saida
- A resposta deve ser somente JSON valido (sem markdown, sem explicacoes externas).
- Retorne um array de 1..N comandos.
- Cada item deve conter apenas:
  - command (string, um dos 5 comandos permitidos)
  - input (string)
- Nao invente campos adicionais.

## Regras de decisao
1. Pedido composto => multiplos comandos
2. Movimento claro => WELL_DEFINED_MOVEMENT
3. Movimento ambiguo => BAD_DEFINED_MOVEMENT (normalmente com SPEAK)
4. Ir para local => LOCATION_MOVEMENT
5. Visao => VIEW
6. Conversa geral => SPEAK
7. Uso de memoria da sessao com past_commands/past_messages
8. Nao alucinar
9. Respeitar limitacoes do robo
10. Em conflito/ambiguidade, pedir clarificacao com SPEAK

## Heuristica rapida
- ande/gire/mova X cm... => WELL_DEFINED_MOVEMENT
- vai ali / se move um pouco => BAD_DEFINED_MOVEMENT (+ SPEAK)
- va para a cozinha => LOCATION_MOVEMENT
- o que voce esta vendo? => VIEW
- pergunta/conversa/limite => SPEAK

## Regra final obrigatoria
Responda com apenas o JSON (array de comandos), sem qualquer texto adicional.
"""


class Orchestrator:
    """Coordinates STT -> command planning -> command execution loop."""

    def __init__(
        self,
        microphone: Microphone,
        llm: LLM,
        speaker: Speaker | None,
        camera: Camera,
        esp32: ESP32,
        movement_translator: MovementTranslatorV7,
        planner_system_prompt: str = PLANNER_SYSTEM_PROMPT,
    ) -> None:
        self.microphone = microphone
        self.llm = llm
        self.speaker = speaker
        self.camera = camera
        self.esp32 = esp32
        self.movement_translator = movement_translator
        self.planner_system_prompt = planner_system_prompt

        self._past_commands: list[dict[str, Any]] = []
        self._past_messages: list[dict[str, Any]] = []

    def start(self) -> None:
        self.microphone.set_on_result(self._on_transcript)
        print("[ORCHESTRATOR] Running. Listening for voice input...")
        self.microphone.listen()

    def _on_transcript(self, text: str) -> None:
        user_text = text.strip()
        if not user_text:
            return

        self.microphone.pause()
        try:
            payload = {
                "past_commands": self._past_commands,
                "past_messages": self._past_messages,
                "message": user_text,
            }
            planned_commands = self._plan_commands(payload)
            executed = self._execute_commands(planned_commands)

            self._past_messages.append({"role": "user", "content": user_text})
            self._past_messages.append({"role": "assistant", "content": json.dumps(executed, ensure_ascii=False)})
            self._past_commands.extend(executed)

            self._trim_history()
        except Exception as exc:
            print(f"[ORCHESTRATOR][ERROR] {exc}")
        finally:
            self.microphone.resume()

    def _plan_commands(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        raw_response = self.llm.complete(
            [
                {"role": "system", "content": self.planner_system_prompt},
                {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
            ],
            temperature=0.0,
            max_tokens=600,
        )
        return self._parse_planner_response(raw_response)

    def _parse_planner_response(self, raw_response: str) -> list[dict[str, str]]:
        parsed: Any
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError:
            start = raw_response.find("[")
            end = raw_response.rfind("]")
            if start == -1 or end == -1 or end <= start:
                return [
                    {
                        "command": "SPEAK",
                        "input": "Nao consegui interpretar o comando. Pode repetir de forma mais clara?",
                    }
                ]
            parsed = json.loads(raw_response[start : end + 1])

        if not isinstance(parsed, list) or not parsed:
            return [
                {
                    "command": "SPEAK",
                    "input": "Nao consegui interpretar o comando. Pode repetir de forma mais clara?",
                }
            ]

        normalized: list[dict[str, str]] = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            command = item.get("command")
            command_input = item.get("input")
            if command not in ALLOWED_COMMANDS:
                continue
            if not isinstance(command_input, str):
                continue
            normalized.append({"command": command, "input": command_input})

        if not normalized:
            return [
                {
                    "command": "SPEAK",
                    "input": "Nao consegui interpretar o comando. Pode repetir de forma mais clara?",
                }
            ]

        return normalized

    def _execute_commands(self, commands: list[dict[str, str]]) -> list[dict[str, Any]]:
        executed: list[dict[str, Any]] = []

        for item in commands:
            command = item["command"]
            command_input = item["input"]
            output = self._execute_single(command, command_input)
            executed_item = {
                "command": command,
                "input": command_input,
                "output": output,
            }
            executed.append(executed_item)
            print(f"[ORCHESTRATOR] {executed_item}")

        return executed

    def _execute_single(self, command: str, command_input: str) -> str:
        if command == "WELL_DEFINED_MOVEMENT":
            movement = WELL_DEFINED_MOVEMENT(input=command_input, output="")
            movement.output = self.movement_translator.translate(movement.input)
            if movement.output and movement.output != "ERRO":
                self.esp32.send(movement.output)
            return str(movement.output)

        if command == "BAD_DEFINED_MOVEMENT":
            bad = BAD_DEFINED_MOVEMENT(input=command_input, output="NOOP")
            return str(bad.output)

        if command == "LOCATION_MOVEMENT":
            location = LOCATION_MOVEMENT(input=command_input, output="NOOP")
            return str(location.output)

        if command == "VIEW":
            view = VIEW(input=command_input, output="")
            image_path = self.camera.capture()
            view.output = self.llm.complete_with_image(
                prompt=view.input,
                image_path=image_path,
                system_prompt="Descreva a imagem com foco no contexto do robo.",
                temperature=0.2,
                max_tokens=400,
            )
            return str(view.output)

        speak = SPEAK(input=command_input, output="SENT")
        if self.speaker is None:
            speak.output = "NO_SPEAKER"
            return str(speak.output)
        self.speaker.speak(speak.input)
        return str(speak.output)

    def _trim_history(self, max_messages: int = 40, max_commands: int = 100) -> None:
        if len(self._past_messages) > max_messages:
            self._past_messages = self._past_messages[-max_messages:]
        if len(self._past_commands) > max_commands:
            self._past_commands = self._past_commands[-max_commands:]
