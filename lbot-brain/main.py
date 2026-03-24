#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import sounddevice as sd

sys.pycache_prefix = str(Path.home() / ".cache" / "lbot-brain" / "pycache")

from brain.modules.camera import Camera
from brain.modules.esp32 import ESP32
from brain.modules.llm import LLM
from brain.modules.microphone import Microphone
from brain.modules.movement_translator import MovementTranslatorV7
from brain.modules.speaker import Speaker
from brain.orchestrator import Orchestrator


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_SIZE = "small"
DEFAULT_SAMPLE_RATE = 16_000
DEFAULT_LLM_MODEL = "qwen3.5-2b"
DEFAULT_TTS_MODEL = SCRIPT_DIR.parent / "lbot-orchestrator" / "models" / "pt_BR-faber-medium.onnx"
DEFAULT_SYSTEM_PROMPT_FILE = SCRIPT_DIR / "system-prompt.txt"
DEFAULT_V7_MODEL = (
    SCRIPT_DIR.parent
    / "lbot-natural-language-controller"
    / "lbot-v7"
    / "lbot_translator_v7.pt"
)


def list_devices() -> None:
    print("\nAvailable audio input devices:\n")
    for index, device in enumerate(sd.query_devices()):
        if device["max_input_channels"] > 0:
            marker = " (default)" if index == sd.default.device[0] else ""
            print(
                f"  [{index}] {device['name']} "
                f"({device['max_input_channels']}ch, {int(device['default_samplerate'])} Hz){marker}"
            )
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="L-Bot Brain - OOP voice runtime (STT + LLM + TTS)."
    )
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--device", type=int, default=None)
    parser.add_argument(
        "--model-size",
        choices=["tiny", "base", "small"],
        default=DEFAULT_MODEL_SIZE,
    )
    parser.add_argument("--sample-rate", type=int, default=DEFAULT_SAMPLE_RATE)
    parser.add_argument("--language", default="pt")
    parser.add_argument("--silence-threshold", type=float, default=None)
    parser.add_argument("--silence-duration", type=float, default=1.0)

    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--llm-api-base", default="http://localhost:1234/v1")
    parser.add_argument("--llm-model", default=DEFAULT_LLM_MODEL)
    parser.add_argument("--system-prompt", default=None)

    parser.add_argument("--no-tts", action="store_true")
    parser.add_argument("--tts-model", default=str(DEFAULT_TTS_MODEL))
    parser.add_argument("--tts-speaker", type=int, default=None)
    parser.add_argument("--planner-system-prompt-file", default=str(DEFAULT_SYSTEM_PROMPT_FILE))
    parser.add_argument("--v7-model", default=str(DEFAULT_V7_MODEL))
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_devices:
        list_devices()
        return

    llm_enabled = not args.no_llm
    tts_enabled = llm_enabled and not args.no_tts

    llm = None
    if llm_enabled:
        llm_kwargs = {
            "api_base": args.llm_api_base,
            "model": args.llm_model,
        }
        if args.system_prompt is not None:
            llm_kwargs["system_prompt"] = args.system_prompt
        try:
            llm = LLM(**llm_kwargs)
        except Exception as exc:
            sys.exit(f"[ERROR] Failed to initialize LLM: {exc}")

    speaker = None
    if tts_enabled:
        try:
            speaker = Speaker(model_path=args.tts_model, speaker_id=args.tts_speaker)
        except Exception as exc:
            sys.exit(f"[ERROR] Failed to initialize TTS: {exc}")

    microphone = Microphone(
        model_size=args.model_size,
        sample_rate=args.sample_rate,
        device=args.device,
        language=args.language,
        silence_threshold=args.silence_threshold,
        silence_duration=args.silence_duration,
    )
    camera = Camera()
    esp32 = ESP32()

    planner_prompt_file = Path(args.planner_system_prompt_file).expanduser().resolve()
    if not planner_prompt_file.exists():
        sys.exit(f"[ERROR] Planner system prompt file not found: {planner_prompt_file}")
    planner_system_prompt = planner_prompt_file.read_text(encoding="utf-8")

    try:
        movement_translator = MovementTranslatorV7(model_path=args.v7_model)
    except Exception as exc:
        sys.exit(f"[ERROR] Failed to initialize WELL_DEFINED_MOVEMENT translator: {exc}")

    if llm is None:
        sys.exit("[ERROR] Orchestrator requires LLM enabled. Remove --no-llm.")

    print(f"[CAMERA] Mock image: {camera.capture()}")
    print(f"[ESP32] Placeholder connected={esp32.connected}")
    print(f"[WELL_DEFINED_MOVEMENT] Translator ready: {args.v7_model}")
    print(f"[PLANNER] System prompt file: {planner_prompt_file}")

    orchestrator = Orchestrator(
        microphone=microphone,
        llm=llm,
        speaker=speaker,
        camera=camera,
        esp32=esp32,
        movement_translator=movement_translator,
        planner_system_prompt=planner_system_prompt,
    )

    print("L-Bot Brain running. Press Ctrl-C to stop.")
    try:
        orchestrator.start()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
