#!/usr/bin/env python3
"""
main.py — Entry-point for the L-Bot voice orchestrator.

Captures microphone audio and transcribes it in real time using faster-whisper.
By default, sends transcribed text to a local LLM (via LM Studio API) for
conversational responses.  Use --no-llm for STT-only mode.

Usage:
    python main.py                        # STT + LLM (default)
    python main.py --no-llm               # STT only
    python main.py --list-devices         # show available audio devices
    python main.py --device 2             # use a specific mic
    python main.py --model-size tiny      # fastest (RPi Zero 2W)
    python main.py --model-size small     # most accurate
"""

from __future__ import annotations

import argparse
import sys

import sounddevice as sd

from voice_listener import VoiceListener

DEFAULT_MODEL_SIZE = "small"
DEFAULT_SAMPLE_RATE = 16_000


def list_devices() -> None:
    """Print all audio input devices and exit."""
    print("\n📋 Dispositivos de áudio disponíveis:\n")
    devices = sd.query_devices()
    for idx, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            marker = " ◀ padrão" if idx == sd.default.device[0] else ""
            print(f"  [{idx}] {dev['name']}  ({dev['max_input_channels']}ch, "
                  f"{int(dev['default_samplerate'])} Hz){marker}")
    print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="L-Bot Voice Orchestrator — escuta o microfone e transcreve "
                    "a fala em tempo real (faster-whisper, offline).",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Lista dispositivos de áudio disponíveis e sai.",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Índice do dispositivo de entrada de áudio (ver --list-devices). "
             "Padrão: microfone padrão do sistema.",
    )
    parser.add_argument(
        "--model-size",
        choices=["tiny", "base", "small"],
        default=DEFAULT_MODEL_SIZE,
        help="Tamanho do modelo Whisper.  tiny (~75 MB, mais rápido), "
             "base (~145 MB, padrão), small (~244 MB, mais preciso).",
    )
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=DEFAULT_SAMPLE_RATE,
        help=f"Taxa de amostragem em Hz. Padrão: {DEFAULT_SAMPLE_RATE}",
    )
    parser.add_argument(
        "--language",
        default="pt",
        help="Código de idioma BCP-47 para o Whisper. Padrão: pt",
    )
    parser.add_argument(
        "--silence-threshold",
        type=float,
        default=None,
        help="Threshold RMS para silêncio (0-1). Padrão: auto-calibrado.",
    )
    parser.add_argument(
        "--silence-duration",
        type=float,
        default=1.0,
        help="Segundos de silêncio para encerrar um segmento de fala. Padrão: 1.0",
    )

    # ── LLM integration ───────────────────────────────────────────────────
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Desativa integração com LLM (somente transcrição STT).",
    )
    parser.add_argument(
        "--llm-api-base",
        type=str,
        default="http://localhost:1234/v1",
        help="URL base da API do LLM. Padrão: http://localhost:1234/v1 (LM Studio)",
    )
    parser.add_argument(
        "--system-prompt",
        type=str,
        default=None,
        help="Prompt de sistema para o LLM. Padrão: assistente genérico em português.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    # ── Banner ─────────────────────────────────────────────────────────────
    llm_mode = not args.no_llm
    if llm_mode:
        print("╔══════════════════════════════════════════╗")
        print("║   L-Bot Voice Orchestrator  (v0.4)       ║")
        print("║   faster-whisper + LLM  •  Streaming    ║")
        print("╚══════════════════════════════════════════╝\n")
    else:
        print("╔══════════════════════════════════════════╗")
        print("║   L-Bot Voice Orchestrator  (v0.4)       ║")
        print("║   faster-whisper  •  Offline  •  int8    ║")
        print("╚══════════════════════════════════════════╝\n")

    # ── LLM setup (optional) ───────────────────────────────────────────────
    llm_client = None
    if llm_mode:
        from llm_client import LLMClient

        llm_kwargs = {"api_base": args.llm_api_base}
        if args.system_prompt is not None:
            llm_kwargs["system_prompt"] = args.system_prompt

        llm_client = LLMClient(**llm_kwargs)

    # ── Callbacks ──────────────────────────────────────────────────────────
    on_result = None
    if llm_client is not None:
        def on_result(text: str) -> None:
            text = text.strip()
            if not text:
                return
            print(f"\r\033[K\033[1m  🗣 {text}\033[0m")
            print("\033[96m  🤖 \033[0m", end="", flush=True)
            try:
                for token in llm_client.chat_stream(text):
                    print(token, end="", flush=True)
            except Exception as exc:
                print(f"\n\033[91m  [ERRO LLM] {exc}\033[0m")
            print("\n")

    # ── Voice listener ─────────────────────────────────────────────────────
    listener = VoiceListener(
        model_size=args.model_size,
        sample_rate=args.sample_rate,
        device=args.device,
        language=args.language,
        silence_threshold=args.silence_threshold,
        silence_duration=args.silence_duration,
        on_result=on_result,
    )
    listener.listen()


if __name__ == "__main__":
    main()
