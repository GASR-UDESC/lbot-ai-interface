#!/usr/bin/env python3

import argparse
import contextlib
import importlib.util
import json
import sys


def load_translator(script_path: str, model_path: str):
    spec = importlib.util.spec_from_file_location("lbot_v7_module", script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load translator script: {script_path}")

    module = importlib.util.module_from_spec(spec)
    main_module = sys.modules["__main__"]

    with contextlib.redirect_stdout(sys.stderr):
        spec.loader.exec_module(module)

        for symbol_name in [
            "Seq2SeqConfig",
            "Vocabulary",
            "Encoder",
            "BahdanauAttention",
            "Decoder",
            "Seq2Seq",
            "LBotTranslatorV7",
        ]:
            if hasattr(module, symbol_name):
                setattr(main_module, symbol_name, getattr(module, symbol_name))

        translator = module.LBotTranslatorV7(model_path)

    return translator


def emit(payload):
    sys.stdout.write(json.dumps(payload, ensure_ascii=True) + "\n")
    sys.stdout.flush()


def main() -> int:
    parser = argparse.ArgumentParser(description="Persistent stdin/stdout bridge for LBot V7")
    parser.add_argument("--translator-script", required=True)
    parser.add_argument("--model", required=True)
    args = parser.parse_args()

    translator = load_translator(args.translator_script, args.model)

    for raw_line in sys.stdin:
        line = raw_line.strip()
        if not line:
            continue

        request_id = None

        try:
            payload = json.loads(line)
            request_id = payload.get("id")
            command = payload.get("command")

            if not isinstance(command, str) or not command.strip():
                raise ValueError("Command must be a non-empty string.")

            lbml = translator.translate(command)
            if lbml == "ERRO":
                raise RuntimeError("Translator returned ERRO.")

            emit({
                "id": request_id,
                "ok": True,
                "lbml": lbml,
            })
        except Exception as error:
            emit({
                "id": request_id,
                "ok": False,
                "error": str(error),
            })

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
