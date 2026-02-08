#!/usr/bin/env bash
# Start Personal RAG service manually (for development/debugging)
# Production: use systemctl --user start personal-rag

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
RAG_DIR="$SCRIPT_DIR/../configs/personal-rag"

cd "$RAG_DIR"
source .venv/bin/activate
exec python -m uvicorn rag_service:app --host 127.0.0.1 --port 8300
