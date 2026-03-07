# L-Bot Orchestrator

Voice orchestrator for the L-Bot robot. Captures audio from a microphone and transcribes speech in real time using [Vosk](https://alphacephei.com/vosk/) — fully offline, no internet required.

Designed to run on a **Raspberry Pi** with a USB microphone.

## Architecture

```
  ┌────────────┐      ┌──────────────────┐      ┌──────────────────┐
  │ Microphone │─────▶│  VoiceListener   │─────▶│  Terminal output  │
  │ (USB/built │      │  (Vosk STT)      │      │  (transcription)  │
  │  -in)      │      │  16 kHz / mono   │      │                   │
  └────────────┘      └──────────────────┘      └──────────────────┘
```

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

# 2. Download the Vosk model for Portuguese (~39 MB)
bash setup_model.sh

# 3. Run the voice listener
python main.py
```

Speak in Portuguese — you'll see partial transcriptions (grey) and final results (bold) printed to the terminal.

Press **Ctrl-C** to stop.

## CLI Options

```
python main.py --help

  --list-devices       List available audio input devices and exit
  --device N           Use audio input device N (see --list-devices)
  --model-path PATH    Path to Vosk model directory
  --sample-rate HZ     Audio sample rate (default: 16000)
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
- **Low accuracy:** The small model (`vosk-model-small-pt-0.3`, 39 MB) trades accuracy for speed. For better results, download the large model (~1.8 GB):
  ```bash
  # Edit setup_model.sh or download manually:
  wget https://alphacephei.com/vosk/models/vosk-model-pt-fb-v0.1.1-20220516_2113.zip
  unzip vosk-model-pt-fb-v0.1.1-20220516_2113.zip -d models/
  python main.py --model-path models/vosk-model-pt-fb-v0.1.1-20220516_2113
  ```
- **High latency:** Reduce `blocksize` in `voice_listener.py` (default 4000 ≈ 250 ms).

## Project Structure

```
lbot-orchestrator/
├── main.py              # CLI entry-point
├── voice_listener.py    # VoiceListener class (mic capture + Vosk STT)
├── setup_model.sh       # Downloads the Vosk Portuguese model
├── requirements.txt     # Python dependencies
├── README.md            # This file
└── models/              # Vosk model(s) — created by setup_model.sh
    └── vosk-model-small-pt-0.3/
```
