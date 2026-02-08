#!/usr/bin/env bash
# Setup Voice Authentication Service
# Creates venv, installs deps, downloads model, sets up systemd service.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VOICE_AUTH_DIR="$PROJECT_DIR/configs/voice-auth"
VENV_DIR="$VOICE_AUTH_DIR/.venv"
OPENCLAW_DIR="$HOME/.openclaw"
VOICEPRINT_DIR="$OPENCLAW_DIR/voice-auth/voiceprints"
SAMPLES_DIR="$OPENCLAW_DIR/voice-auth/samples"
SKILL_SRC="$VOICE_AUTH_DIR/SKILL.md"
SKILL_DST="$OPENCLAW_DIR/workspace/skills/voice-auth/SKILL.md"
SERVICE_SRC="$VOICE_AUTH_DIR/voice-auth.service"
SERVICE_DST="$HOME/.config/systemd/user/voice-auth.service"

echo "=== Voice Auth Setup ==="
echo ""

# 1. Check prerequisites
echo "[1/7] Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
command -v ffmpeg >/dev/null 2>&1 || { echo "ERROR: ffmpeg not found. Install: sudo apt install ffmpeg"; exit 1; }

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "  Python: $PYTHON_VERSION"
echo "  ffmpeg: $(ffmpeg -version 2>&1 | head -1)"

# 2. Create virtual environment
echo ""
echo "[2/7] Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "  Venv already exists at $VENV_DIR, reusing."
else
    python3 -m venv "$VENV_DIR"
    echo "  Created $VENV_DIR"
fi

# 3. Install Python dependencies
echo ""
echo "[3/7] Installing Python dependencies (this may take a few minutes)..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$VOICE_AUTH_DIR/requirements.txt" -q
echo "  Dependencies installed."

# 4. Pre-download SpeechBrain model
echo ""
echo "[4/7] Pre-downloading SpeechBrain ECAPA-TDNN model..."
"$VENV_DIR/bin/python" -c "
from speechbrain.inference.speaker import SpeakerRecognition
print('  Downloading model (first run only)...')
verifier = SpeakerRecognition.from_hparams(
    source='speechbrain/spkrec-ecapa-voxceleb',
    savedir='$VOICE_AUTH_DIR/pretrained_models/spkrec-ecapa-voxceleb',
)
print('  Model downloaded and verified.')
"

# 5. Create data directories
echo ""
echo "[5/7] Creating data directories..."
mkdir -p "$VOICEPRINT_DIR" "$SAMPLES_DIR"
echo "  $VOICEPRINT_DIR"
echo "  $SAMPLES_DIR"

# 6. Install OpenClaw skill
echo ""
echo "[6/7] Installing OpenClaw skill..."
mkdir -p "$(dirname "$SKILL_DST")"
cp "$SKILL_SRC" "$SKILL_DST"
echo "  Copied SKILL.md to $SKILL_DST"

# 7. Install and enable systemd service
echo ""
echo "[7/7] Installing systemd service..."
mkdir -p "$(dirname "$SERVICE_DST")"
cp "$SERVICE_SRC" "$SERVICE_DST"
systemctl --user daemon-reload
systemctl --user enable voice-auth.service
systemctl --user start voice-auth.service
echo "  Service installed, enabled, and started."

# Health check
echo ""
echo "=== Health Check ==="
sleep 3
if curl -sf http://127.0.0.1:8200/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://127.0.0.1:8200/health)
    echo "  Service is UP: $HEALTH"
else
    echo "  WARNING: Service not responding yet. Check logs:"
    echo "    journalctl --user -u voice-auth -n 20"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Next steps:"
echo "  1. Enroll your voice: send 5-10 voice notes to Moltbot on Telegram"
echo "  2. Or enroll manually:"
echo "     curl -F 'file=@voice_sample.ogg' -F 'name=arnaldo' http://localhost:8200/enroll"
echo "  3. Test verification:"
echo "     curl -F 'file=@test_voice.ogg' http://localhost:8200/verify"
echo "  4. Check status: systemctl --user status voice-auth"
