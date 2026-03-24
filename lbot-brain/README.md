# lbot-brain

`lbot-brain` is the OOP replacement for `lbot-orchestrator`.

It is structured around three encapsulated classes:

- `Speaker` for speech synthesis output.
- `Microphone` for microphone capture and transcription.
- `LLM` for local model chat requests.

There is also a `Camera` module (mock for now) that always returns `image.jpg`.

There is an `ESP32` module placeholder (no-op for now).

`WELL_DEFINED_MOVEMENT` is implemented in-process via `lbot-v7`:

- input text -> `lbot-natural-language-controller/lbot-v7/lbot_v7.py`
- output LBML -> `ESP32.send(output)`

`SPEAK` is implemented by calling the `Speaker` module directly.

`VIEW` is implemented by:

- reading image from `Camera.capture()`
- sending image + `VIEW.input` prompt to LLM multimodal endpoint
- storing response text in `VIEW.output`

## Orchestrator

The orchestrator runs the full loop:

1. Listen on `Microphone` until speech ends.
2. Send `{ past_commands, past_messages, message }` to LLM planner using the LBOT system prompt.
3. Receive JSON array of commands.
4. Execute each command in order.
5. Store command outputs in session history.
6. Resume listening.

Current execution behavior:

- `WELL_DEFINED_MOVEMENT`: translates with `lbot-v7` and sends to `ESP32`.
- `BAD_DEFINED_MOVEMENT`: no-op (`output="NOOP"`).
- `LOCATION_MOVEMENT`: no-op (`output="NOOP"`).
- `VIEW`: captures image and asks multimodal LLM.
- `VIEW`: captures image, asks multimodal LLM, and always speaks the result.
- `SPEAK`: calls `Speaker`.

`main.py` only wires these classes and runs the loop.

All runtime classes are inside `brain/modules/`.

Command models are inside `brain/commands/`:

- `WELL_DEFINED_MOVEMENT`
- `BAD_DEFINED_MOVEMENT`
- `LOCATION_MOVEMENT`
- `VIEW`
- `SPEAK`

Each command model has `input` and `output` properties.

This project uses namespace package style for `brain/` and avoids extra
`__init__.py` files in subfolders.

Bytecode cache is centralized at `lbot-brain/.pycache/`.

## Setup

```bash
cd lbot-brain
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run

```bash
python3 main.py
```

Useful flags:

- `--list-devices`
- `--device N`
- `--no-llm`
- `--no-tts`
- `--llm-api-base http://localhost:1234/v1`
- `--llm-model qwen3.5-2b` (default)
- `--tts-model ../lbot-orchestrator/models/pt_BR-faber-medium.onnx`
- `--planner-system-prompt-file ./system-prompt.txt`
- `--v7-model ../lbot-natural-language-controller/lbot-v7/lbot_translator_v7.pt`

## Reused resources

This project reuses the same core runtime strategy and dependencies from
`lbot-orchestrator`:

- `faster-whisper` for STT
- `openai` client with OpenAI-compatible local server for LLM
- `piper-tts` for TTS
