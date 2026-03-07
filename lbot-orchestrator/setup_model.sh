#!/usr/bin/env bash
# Pre-downloads the faster-whisper model for offline use.
# Usage: bash setup_model.sh [tiny|base|small]
#
# Models (multilingual, great for Portuguese):
#   tiny  ~75  MB — fastest, good for RPi Zero 2W
#   base  ~145 MB — best balance for RPi 4/5  (default)
#   small ~244 MB — most accurate, needs RPi 4 with 4+ GB RAM

set -euo pipefail

MODEL_SIZE="${1:-base}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "⬇  Pre-downloading faster-whisper '${MODEL_SIZE}' model ..."
echo "   (saved to ~/.cache/huggingface  —  reused across runs)"

python3 - <<EOF
from faster_whisper import WhisperModel
print("Loading model '${MODEL_SIZE}' (this downloads it if missing)...")
m = WhisperModel("${MODEL_SIZE}", device="cpu", compute_type="int8")
print("✔ Model ready")
EOF
