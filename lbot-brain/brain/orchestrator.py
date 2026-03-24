from __future__ import annotations

import difflib
import json
import time
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

DEFAULT_PLANNER_SYSTEM_PROMPT = "Retorne apenas um array JSON de comandos do LBOT."


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
        planner_system_prompt: str = DEFAULT_PLANNER_SYSTEM_PROMPT,
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

        self._last_spoken_text = ""
        self._last_spoken_at = 0.0
        self._last_user_text = ""
        self._last_user_at = 0.0

        self._echo_cooldown_seconds = 1.3
        self._echo_similarity_threshold = 0.72
        self._dedupe_window_seconds = 4.0
        self._dedupe_similarity_threshold = 0.9

    def start(self) -> None:
        self.microphone.set_on_result(self._on_transcript)
        print("[ORCHESTRATOR] Running. Listening for voice input...")
        self.microphone.listen()

    def _on_transcript(self, text: str) -> None:
        user_text = text.strip()
        if not user_text:
            return

        print(f"[ORCHESTRATOR][STT_USER] {user_text}")

        if self._should_ignore_transcript(user_text):
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
            self._last_user_text = user_text
            self._last_user_at = time.monotonic()
        except Exception as exc:
            print(f"[ORCHESTRATOR][ERROR] {exc}")
        finally:
            self.microphone.resume()

    def _should_ignore_transcript(self, user_text: str) -> bool:
        now = time.monotonic()

        if self._last_spoken_at > 0 and now - self._last_spoken_at < self._echo_cooldown_seconds:
            print("[ORCHESTRATOR] Ignored transcript (speak cooldown).")
            return True

        if self._last_spoken_text:
            echo_similarity = self._similarity(user_text, self._last_spoken_text)
            if echo_similarity >= self._echo_similarity_threshold:
                print(
                    "[ORCHESTRATOR] Ignored transcript "
                    f"(echo similarity={echo_similarity:.2f})."
                )
                return True

        if self._last_user_text and now - self._last_user_at < self._dedupe_window_seconds:
            user_similarity = self._similarity(user_text, self._last_user_text)
            if user_similarity >= self._dedupe_similarity_threshold:
                print(
                    "[ORCHESTRATOR] Ignored transcript "
                    f"(duplicate similarity={user_similarity:.2f})."
                )
                return True

        return False

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def _plan_commands(self, payload: dict[str, Any]) -> list[dict[str, str]]:
        message = str(payload.get("message", "")).strip()
        if self._is_history_query(message):
            return [{"command": "SPEAK", "input": self._build_history_reply()}]

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

            if command == "VIEW":
                speak_output = self._speak_text(str(output))
                speak_item = {
                    "command": "SPEAK",
                    "input": str(output),
                    "output": speak_output,
                }
                executed.append(speak_item)
                print(f"[ORCHESTRATOR] {speak_item}")

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
        speak.output = self._speak_text(speak.input)
        return str(speak.output)

    def _speak_text(self, text: str) -> str:
        if not text.strip():
            return "EMPTY"
        if self.speaker is None:
            return "NO_SPEAKER"
        self.speaker.speak(text)
        self._last_spoken_text = text
        self._last_spoken_at = time.monotonic()
        return "SENT"

    def _is_history_query(self, message: str) -> bool:
        msg = message.lower()
        triggers = (
            "quais comandos",
            "comandos executados",
            "o que voce executou",
            "o que você executou",
            "o que ja executou",
            "o que já executou",
            "o que voce fez",
            "o que você fez",
        )
        return any(trigger in msg for trigger in triggers)

    def _build_history_reply(self) -> str:
        if not self._past_commands:
            return "Ainda nao executei comandos nesta sessao."

        recent = self._past_commands[-8:]
        parts: list[str] = []
        for item in recent:
            command = str(item.get("command", ""))
            command_input = str(item.get("input", "")).strip()
            if command_input:
                parts.append(f"{command}: {command_input}")
            else:
                parts.append(command)

        return "Comandos recentes executados: " + " | ".join(parts)

    def _trim_history(self, max_messages: int = 40, max_commands: int = 100) -> None:
        if len(self._past_messages) > max_messages:
            self._past_messages = self._past_messages[-max_messages:]
        if len(self._past_commands) > max_commands:
            self._past_commands = self._past_commands[-max_commands:]
