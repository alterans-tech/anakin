#!/usr/bin/env bash
# Setup Personal RAG Service
# Creates venv, installs deps, sets up systemd service, syncs initial data.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
RAG_DIR="$PROJECT_DIR/configs/personal-rag"
VENV_DIR="$RAG_DIR/.venv"
SKILL_SRC="$RAG_DIR/SKILL.md"
SKILL_DST="$HOME/.openclaw/workspace/skills/personal-knowledge/SKILL.md"
SERVICE_SRC="$RAG_DIR/personal-rag.service"
SERVICE_DST="$HOME/.config/systemd/user/personal-rag.service"

echo "=== Personal RAG Setup ==="
echo ""

# 1. Check prerequisites
echo "[1/6] Checking prerequisites..."
command -v python3 >/dev/null 2>&1 || { echo "ERROR: python3 not found"; exit 1; }
command -v ollama >/dev/null 2>&1 || { echo "ERROR: ollama not found"; exit 1; }

# Check Ollama models
if ! ollama list 2>/dev/null | grep -q "nomic-embed-text"; then
    echo "  Pulling nomic-embed-text..."
    ollama pull nomic-embed-text
fi
echo "  Ollama: OK"
echo "  Models: $(ollama list 2>/dev/null | grep -E 'qwen3|nomic' | awk '{print $1}' | tr '\n' ' ')"

# 2. Create virtual environment
echo ""
echo "[2/6] Creating virtual environment..."
if [ -d "$VENV_DIR" ]; then
    echo "  Venv already exists, reusing."
else
    python3 -m venv "$VENV_DIR"
    echo "  Created $VENV_DIR"
fi

# 3. Install dependencies
echo ""
echo "[3/6] Installing Python dependencies..."
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$RAG_DIR/requirements.txt" -q
echo "  Dependencies installed."

# 4. Install OpenClaw skill
echo ""
echo "[4/6] Installing OpenClaw skill..."
mkdir -p "$(dirname "$SKILL_DST")"
cp "$SKILL_SRC" "$SKILL_DST"
echo "  Copied SKILL.md to $SKILL_DST"

# 5. Install and start systemd service
echo ""
echo "[5/6] Installing systemd service..."
mkdir -p "$(dirname "$SERVICE_DST")"
cp "$SERVICE_SRC" "$SERVICE_DST"
systemctl --user daemon-reload
systemctl --user enable personal-rag.service
systemctl --user start personal-rag.service
echo "  Service installed, enabled, and started."

# 6. Initial sync
echo ""
echo "[6/6] Running initial data sync (this may take a minute)..."
sleep 3
if curl -sf http://127.0.0.1:8300/health > /dev/null 2>&1; then
    SYNC_RESULT=$(curl -s -X POST http://127.0.0.1:8300/sync)
    echo "  $SYNC_RESULT"
else
    echo "  WARNING: Service not responding yet. Run sync manually:"
    echo "    curl -s -X POST http://localhost:8300/sync"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Quick test:"
echo "  curl -s http://localhost:8300/health"
echo "  curl -s -X POST http://localhost:8300/query -H 'Content-Type: application/json' -d '{\"query\": \"What is Arnaldo working on?\"}'"
