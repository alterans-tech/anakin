#!/usr/bin/env bash
# Start Voice Auth service manually (for development/debugging)
# Production: use systemctl --user start voice-auth

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VOICE_AUTH_DIR="$SCRIPT_DIR/../configs/voice-auth"

cd "$VOICE_AUTH_DIR"
source .venv/bin/activate
exec python -m uvicorn speaker_service:app --host 127.0.0.1 --port 8200
