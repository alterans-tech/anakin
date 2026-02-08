"""
AIAvatarKit WebSocket Server — connected to OpenClaw via Claude LLM + OpenAI TTS/STT.

Usage:
    source .venv/bin/activate
    python -m uvicorn server:app --host 0.0.0.0 --port 8100

Web UI:  http://localhost:8100/static/index.html
Admin:   http://localhost:8100/admin
"""

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from aiavatar.adapter.websocket.server import AIAvatarWebSocketServer
from aiavatar.sts.llm.claude import ClaudeService
from aiavatar.sts.tts.openai import OpenAISpeechSynthesizer

# --- Load .env ---
from pathlib import Path
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

# --- Claude LLM ---
llm = ClaudeService(
    anthropic_api_key=ANTHROPIC_API_KEY,
    model="claude-sonnet-4-5",
    temperature=0.7,
    system_prompt=(
        "You are Anakin's personal AI assistant. "
        "You are helpful, concise, and friendly. "
        "Keep responses short and conversational since they will be spoken aloud. "
        "Avoid markdown formatting, code blocks, or long lists in your responses."
    ),
)

# --- OpenAI TTS (uses gpt-4o-mini-tts, voice echo) ---
tts = OpenAISpeechSynthesizer(
    openai_api_key=OPENAI_API_KEY,
    model="gpt-4o-mini-tts",
    speaker="echo",
)

# --- Avatar WebSocket Server ---
aiavatar_app = AIAvatarWebSocketServer(
    openai_api_key=OPENAI_API_KEY,  # Used for STT (Whisper)
    llm=llm,
    tts=tts,
    debug=True,
)

# --- FastAPI ---
app = FastAPI(title="AIAvatarKit — Anakin")
router = aiavatar_app.get_websocket_router()
app.include_router(router)

# Serve the character web UI
app.mount("/static", StaticFiles(directory="html"), name="static")

# Admin panel
try:
    from aiavatar.admin import setup_admin_panel
    setup_admin_panel(app, adapter=aiavatar_app)
except ImportError:
    pass
