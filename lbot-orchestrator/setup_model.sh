#!/usr/bin/env bash
# Pre-downloads the faster-whisper model and piper TTS voice for offline use.
# Usage: bash setup_model.sh [tiny|base|small]
#
# STT Models (multilingual, great for Portuguese):
#   tiny  ~75  MB — fastest, good for RPi Zero 2W
#   base  ~145 MB — best balance for RPi 4/5  (default)
#   small ~244 MB — most accurate, needs RPi 4 with 4+ GB RAM
#
# TTS Voice:
#   pt_BR-faber-medium  ~40 MB — clear Portuguese voice, 22050 Hz

set -euo pipefail

MODEL_SIZE="${1:-base}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MODELS_DIR="${SCRIPT_DIR}/models"

# ── 1. STT: faster-whisper ─────────────────────────────────────────────────────

echo "⬇  Pre-downloading faster-whisper '${MODEL_SIZE}' model ..."
echo "   (saved to ~/.cache/huggingface  —  reused across runs)"

python3 - <<EOF
from faster_whisper import WhisperModel
print("Loading model '${MODEL_SIZE}' (this downloads it if missing)...")
m = WhisperModel("${MODEL_SIZE}", device="cpu", compute_type="int8")
print("✔ Model ready")
EOF

# ── 2. TTS: piper voice ───────────────────────────────────────────────────────

VOICE_NAME="pt_BR-faber-medium"
ONNX_FILE="${MODELS_DIR}/${VOICE_NAME}.onnx"
JSON_FILE="${MODELS_DIR}/${VOICE_NAME}.onnx.json"
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/pt/pt_BR/faber/medium"

mkdir -p "${MODELS_DIR}"

if [[ -f "${ONNX_FILE}" && -f "${JSON_FILE}" ]]; then
    echo ""
    echo "✔ TTS voice '${VOICE_NAME}' already downloaded."
else
    echo ""
    echo "⬇  Downloading piper TTS voice '${VOICE_NAME}' (~40 MB) ..."

    curl -L --progress-bar -o "${ONNX_FILE}" \
        "${BASE_URL}/${VOICE_NAME}.onnx"

    curl -L --progress-bar -o "${JSON_FILE}" \
        "${BASE_URL}/${VOICE_NAME}.onnx.json"

    echo "✔ TTS voice ready: ${ONNX_FILE}"
fi

echo ""
echo "✅ Setup completo!  Execute:  python main.py"
