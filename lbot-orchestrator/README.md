# L-Bot Orchestrator

Voice orchestrator for the L-Bot robot. Implements a full conversational loop:

1. **STT** — Captures audio from a microphone and transcribes speech in real time using [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (CTranslate2 backend, offline).
2. **LLM** — Sends transcribed text to a local LLM (via LM Studio API) for conversational responses.
3. **TTS** — Speaks the LLM response aloud using [piper-tts](https://github.com/rhasspy/piper) (ONNX neural TTS, offline).

The microphone is automatically paused during TTS playback to prevent feedback loops.

Designed to run on a **Raspberry Pi** with a USB microphone.

## Architecture

```
  ┌────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ Microphone │─────▶│  VoiceListener   │──┬──▶│  Terminal output  │
  │ (USB/built │      │  (Whisper STT)   │  │   │  (transcription)  │
  │  -in)      │      │  16 kHz / mono   │  │   └──────────────────┘
  └────────────┘      └──────────────────┘  │
       ▲                                    │   text
       │ pause/resume                       ▼
       │                              ┌──────────────┐
  ┌────────────┐     streamed tokens  │   LLMClient  │
  │  Speaker   │◀─────────────────────│  (LM Studio) │
  │ (TTS out)  │      ┌──────────┐    └──────────────┘
  └────────────┘◀─────│ TTSSpeaker│           │
                      │  (piper) │◀───────────┘
                      └──────────┘   full response
```

### Key Features (v0.5)

- **Full conversational loop** — STT → LLM → TTS: speak to the robot, it understands and talks back.
- **Offline TTS** — piper-tts with pt-BR neural voice (ONNX, ~40 MB). No internet required.
- **Mic pause during TTS** — automatically pauses the microphone while the robot speaks to prevent feedback loops.
- **Adaptive noise calibration** — automatically measures ambient noise on startup and sets the silence threshold accordingly.
- **Pre-buffer ring** — keeps ~500 ms of audio before speech is detected so the first syllable is never clipped.
- **Audio peak-normalisation** — normalises volume to –1 dBFS before transcription for consistent results regardless of mic gain.
- **Domain-specific prompt** — primes Whisper with L-Bot robot vocabulary (directions, body parts, units) to reduce hallucinations.
- **Silero VAD + tuned params** — faster-whisper's built-in Silero VAD with optimised thresholds for Portuguese speech.
- **Noise burst filtering** — discards audio segments shorter than 0.4 s (clicks, pops, bumps).
- **int8 quantisation** — 4-6× speed-up on CPU with minimal accuracy loss.

> **Future:** the transcribed text will feed into `lbot-v7` (NLP seq2seq model) to translate Portuguese commands into LBML, which are then sent to the robot via `lbot-socket-control` (TCP:9999).

## Prerequisites

| Requirement | macOS | Raspberry Pi (Debian/Ubuntu) |
|---|---|---|
| Python | 3.9+ | 3.9+ |
| PortAudio | `brew install portaudio` | `sudo apt install libportaudio2 portaudio19-dev` |
| pip | bundled with Python | `sudo apt install python3-pip` |

## Quick Start

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Download STT + TTS models
bash setup_model.sh

# 3. Start the LLM server (LM Studio, ollama, etc.)
#    LM Studio: Developer → Start Server (port 1234)

# 4. Run the voice orchestrator
python main.py
```

Speak in Portuguese — you'll see transcriptions in the terminal and hear the AI response through your speakers.

Press **Ctrl-C** to stop.

## CLI Options

```
python main.py --help

  --list-devices          List available audio input devices and exit
  --device N              Use audio input device N (see --list-devices)
  --model-size SIZE       tiny (~75 MB), base (~145 MB), small (~244 MB, default)
  --sample-rate HZ        Audio sample rate (default: 16000)
  --language LANG         BCP-47 language code (default: pt)
  --silence-threshold F   RMS threshold for silence (0-1). Default: auto-calibrated
  --silence-duration F    Seconds of silence to end a segment (default: 1.0)

  LLM:
  --no-llm                Disable LLM (STT-only mode)
  --llm-api-base URL      LLM API URL (default: http://localhost:1234/v1)
  --system-prompt TEXT    Custom system prompt for the LLM

  TTS:
  --no-tts                Disable TTS (text-only LLM responses)
  --tts-model PATH        Path to piper .onnx model (default: models/pt_BR-faber-medium.onnx)
  --tts-speaker ID        Speaker ID for multi-speaker models
```

## Raspberry Pi Setup

1. **Connect a USB microphone** and verify it's detected:
   ```bash
   arecord -l
   ```

2. **Install system dependencies:**
   ```bash
   sudo apt update
   sudo apt install -y libportaudio2 portaudio19-dev python3-pip
   ```

3. **Install Python packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download the model:**
   ```bash
   bash setup_model.sh
   ```

5. **Find your microphone device index:**
   ```bash
   python main.py --list-devices
   ```

6. **Run with your mic:**
   ```bash
   python main.py --device <N>
   ```

### Troubleshooting (RPi)

- **"No default input device":** Make sure a USB mic is connected. Run `arecord -l` to check.
- **Low accuracy:** Try the `small` model (default) for best accuracy, or `tiny` for constrained devices. You can also set `--language pt` explicitly.
- **Clipping at the start of speech:** The pre-buffer should handle this automatically. If it persists, try lowering `--silence-threshold`.
- **Too many false triggers:** Increase `--silence-threshold` or ensure the ambient calibration runs in a quiet environment.
- **High latency:** Use `--model-size tiny` for fastest inference on RPi Zero 2W.

## Project Structure

```
lbot-orchestrator/
├── main.py              # CLI entry-point (STT + LLM + TTS loop)
├── voice_listener.py    # VoiceListener class (mic capture + faster-whisper STT)
├── llm_client.py        # LLMClient class (OpenAI-compatible API, streaming)
├── tts_speaker.py       # TTSSpeaker class (piper-tts, offline neural TTS)
├── requirements.txt     # Python dependencies
├── setup_model.sh       # Download STT + TTS models
├── README.md            # This file
└── models/
    ├── pt_BR-faber-medium.onnx       # piper TTS voice model (~40 MB)
    ├── pt_BR-faber-medium.onnx.json  # piper model config
    └── vosk-model-small-pt-0.3/      # (legacy — no longer used)
```
