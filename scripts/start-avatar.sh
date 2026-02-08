#!/usr/bin/env bash
# Start AIAvatarKit server
# Web UI:  http://localhost:8100/static/index.html
# Admin:   http://localhost:8100/admin

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
AVATAR_DIR="$SCRIPT_DIR/../configs/aiavatarkit"

cd "$AVATAR_DIR"
source .venv/bin/activate
exec python -m uvicorn server:app --host 0.0.0.0 --port 8100
