#!/usr/bin/env python3
"""
main.py — Entry-point for the L-Bot voice orchestrator.

Captures microphone audio and transcribes it in real time using faster-whisper.
Designed to run on a Raspberry Pi with a USB microphone.

Usage:
    python main.py                        # base model, default mic
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

DEFAULT_MODEL_SIZE = "base"
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list_devices:
        list_devices()
        sys.exit(0)

    print("╔══════════════════════════════════════════╗")
    print("║   L-Bot Voice Orchestrator  (v0.2)       ║")
    print("║   faster-whisper  •  Offline  •  int8    ║")
    print("╚══════════════════════════════════════════╝\n")

    listener = VoiceListener(
        model_size=args.model_size,
        sample_rate=args.sample_rate,
        device=args.device,
        language=args.language,
    )
    listener.listen()


if __name__ == "__main__":
    main()
