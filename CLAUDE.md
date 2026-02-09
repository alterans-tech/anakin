# Anakin

> **MUST READ: `../.uatu/UATU.md`** — Required framework rules for all tasks.

Personal AI assistant orchestration project - OpenClaw setup and configuration guides.

---

## Project Overview

Anakin provides setup guides, configuration scripts, and automation for deploying personal AI assistants (OpenClaw/Moltbot) on Linux systems.

---

## Status Overview

### Running Services

| Service | Port | Status | systemd unit |
|---------|------|--------|-------------|
| **OpenClaw Gateway** | 18789 | Running | `openclaw-gateway.service` |
| **AIAvatarKit** | 8100 | Running | `aiavatarkit` |
| **Voice Auth** | 8200 | Running (0 speakers enrolled) | `voice-auth` |
| **Personal RAG** | 8300 | Running (78 docs indexed) | `personal-rag` |
| **Voice-call Plugin** | 3334 | Running (needs Twilio/Telnyx for calls) | via OpenClaw |
| **Docker** | - | Installed (user in docker group) | `docker.service` |

### Done

| Component | Details |
|-----------|---------|
| **OpenClaw Gateway** | v2026.2.6-3, Telegram bot `@anakin_moltbot` |
| **Primary model** | Claude Sonnet 4.5 (cost-optimized from Opus) |
| **Fallback chain** | Sonnet → GPT-4o → Gemini → Haiku |
| **Heartbeat** | gpt-4o-mini (cheapest) |
| **Sub-agents** | Claude Haiku 4.5 |
| **TTS** | OpenAI gpt-4o-mini-tts, voice `echo`, auto=off (on-demand) |
| **STT** | gpt-4o-mini-transcribe (~3.2s per voice note) |
| **Memory plugin** | OpenAI text-embedding-3-small for vectors |
| **TTS /tmp/ patch** | `isValidMedia()` patched, script: `scripts/patch-openclaw-tts.sh` |
| **Rate limit tuning** | contextTokens: 80k, maxConcurrent: 2, cache-ttl pruning |
| **IPv6 DNS fix** | `NODE_OPTIONS=--dns-result-order=ipv4first` in systemd env |
| **AIAvatarKit** | Browser avatar on :8100, Claude + OpenAI TTS/STT + Silero VAD |
| **Voice Auth service** | SpeechBrain ECAPA-TDNN on :8200, skill installed (always-on) |
| **Personal RAG** | ChromaDB + nomic-embed-text + qwen3:4b on :8300, skill installed (always-on) |
| **Ollama** | qwen3:4b + nomic-embed-text installed, used by Personal RAG |
| **System packages** | tmux 3.4, ripgrep 14.1, sox, v4l2loopback, docker 28.2 |
| **Fine-tune notebook** | `configs/personal-rag/finetune_qwen3_4b.ipynb` (Colab-ready) |
| **Calendar cron scripts** | `scripts/calendar-{morning-briefing,meeting-reminder,weekly-review}.sh` (ready, needs gog) |
| **Training data** | 71 pairs exported (12 preference-filtered), need 200+ for fine-tuning |
| **ClawHub skills** | liveavatar, ollama-local, heygen-avatar-lite, notion-api-skill, trello-api |

### In Progress

| Item | Status | What's left |
|------|--------|-------------|
| **Voice Auth enrollment** | Service running, no voiceprint | Send 5-10 voice notes to Moltbot |
| **Fine-tuning data** | 71 pairs extracted (need 200-500+) | Accumulate conversations, run `scripts/extract-training-data.py --stats-only` weekly |

### Pending (manual setup required)

| Item | Effort | Guide / Reference |
|------|--------|-------------------|
| **Voice Auth enrollment** | 5 min | Send 5-10 voice notes to `@anakin_moltbot` on Telegram |
| **WhatsApp QR pairing** | 5 min | `openclaw channels login` — scan QR |
| **Google Calendar (gog)** | 15 min | `guides/gog-calendar-setup.md` — OAuth flow, install binary, env vars. Cron scripts ready at `scripts/calendar-*.sh` |
| **Google Gemini API key** | 2 min | aistudio.google.com/apikey — free tier fallback |
| **LiveAvatar API key** | 2 min | Get free key from app.liveavatar.com |
| **OpenHue (Hue lights)** | 10 min | `docker pull openhue/cli` + bridge button press |
| **LG ThinQ AC** | 10 min | PAT token + thinqconnect-mcp |
| **Notion integration** | 5 min | Create integration, share pages, add API key |
| **Trello integration** | 5 min | Get API key + token from trello.com/app-key |
| **Twilio/Telnyx for voice calls** | 15 min | Voice-call plugin running, needs telephony provider |

---

## Jira

| Key | Value |
|-----|-------|
| **Board** | ANI |
| **Project Key** | ANI |

Use Jira MCP tools to manage tasks:
- `mcp__atlassian__jira_get_board_issues` - View board issues
- `mcp__atlassian__jira_create_issue` - Create new tasks
- `mcp__atlassian__jira_transition_issue` - Update task status

---

## Project Structure

```
anakin/
├── guides/              # Step-by-step installation guides
├── scripts/             # Automation scripts
├── configs/             # Configuration templates
└── docs/                # Additional documentation
```

---

## Quick Commands

```bash
# Service management
systemctl --user {status,restart,stop} openclaw-gateway
systemctl --user {status,restart,stop} aiavatarkit
systemctl --user {status,restart,stop} voice-auth
systemctl --user {status,restart,stop} personal-rag

# Health checks
curl http://localhost:8200/health   # Voice Auth
curl http://localhost:8300/health   # Personal RAG

# RAG operations
curl -s -X POST http://localhost:8300/sync  # Re-sync knowledge base
python3 scripts/extract-training-data.py --stats-only  # Training data stats

# Manual start scripts
./scripts/start-avatar.sh
./scripts/start-voice-auth.sh
./scripts/start-personal-rag.sh
```

---

## Key Technologies

- **Target Platform**: Linux (Ubuntu 24.04 LTS preferred)
- **Runtime**: Node.js 22+
- **AI Backend**: OpenClaw (formerly Clawdbot/Moltbot)
- **Scripting**: Bash, Python

---

## Related Projects

| Project | Path | Relationship |
|---------|------|--------------|
| uatu | `../uatu/` | AI orchestration framework (parent) |
| claude-flow | `../claude-flow/` | Multi-agent coordination |

---

## Uatu Integration

This project follows the Uatu framework. Before starting work:

1. Read `../.uatu/UATU.md`
2. Run Sequential Thinking for complex tasks
3. Deliver artifacts to `../.uatu/delivery/`

---

## File Organization

| Directory | Purpose |
|-----------|---------|
| `guides/` | Installation and setup guides |
| `scripts/` | Bash/Python automation |
| `configs/` | Template configurations |
| `docs/` | Reference documentation |

---

## OpenClaw Patches

After every `npm install -g openclaw@latest`, re-apply patches and restart:

```bash
./scripts/patch-openclaw-tts.sh
systemctl --user restart openclaw-gateway.service
```

| Patch | Script | Guide |
|-------|--------|-------|
| TTS voice note delivery (MEDIA: /tmp/ path fix) | `scripts/patch-openclaw-tts.sh` | `guides/openclaw-tts-patch.md` |

---

## AIAvatarKit (Avatar Chat)

Local browser-based avatar with voice interaction, powered by Claude + OpenAI TTS/STT.

| Item | Value |
|------|-------|
| **Location** | `configs/aiavatarkit/` |
| **Web UI** | http://localhost:8100/static/index.html |
| **Service** | `systemctl --user {status,restart,stop} aiavatarkit` |
| **Port** | 8100 |
| **LLM** | Claude Sonnet 4.5 (Anthropic API) |
| **TTS** | OpenAI gpt-4o-mini-tts, voice "echo" |
| **STT** | OpenAI Whisper |
| **VAD** | Silero (local, CPU) |

---

## Voice Authentication

Local speaker verification using SpeechBrain ECAPA-TDNN. Gates admin operations (credentials, config changes, privileged commands) behind voice identity verification. Zero cost, full privacy — all processing stays on-device.

| Item | Value |
|------|-------|
| **Location** | `configs/voice-auth/` |
| **Service** | `systemctl --user {status,restart,stop} voice-auth` |
| **Port** | 8200 (localhost only) |
| **Model** | SpeechBrain ECAPA-TDNN (0.80% EER) |
| **RAM** | ~300-500 MB |
| **Latency** | 100-300ms (runs in parallel with STT, zero added wall-clock time) |
| **Threshold** | 0.25 cosine similarity (configurable via `VOICE_AUTH_THRESHOLD` env var) |
| **Voiceprints** | `~/.openclaw/voice-auth/voiceprints/` |
| **Samples** | `~/.openclaw/voice-auth/samples/` |
| **Skill** | `~/.openclaw/workspace/skills/voice-auth/SKILL.md` (always-on) |
| **Setup** | `./scripts/setup-voice-auth.sh` |
| **Guide** | `guides/voice-auth-setup.md` |
| **Research** | `docs/voice-recognition-research.md` |

### Admin scope (requires voice verification)

- Sharing passwords, API keys, credentials, secrets
- Modifying OpenClaw config, SOUL.md, system prompt, skills
- Running `sudo` commands, changing systemd services

Text-only admin requests are **always denied** — the user must send a voice note. Verification is session-based (valid for 2 hours). If the service is down, admin operations **fail closed** (denied).

### Quick commands

```bash
# Setup (one-time)
./scripts/setup-voice-auth.sh

# Service management
systemctl --user {status,restart,stop} voice-auth

# Health check
curl http://localhost:8200/health

# Enroll a voice sample
curl -F "file=@voice.ogg" -F "name=arnaldo" http://localhost:8200/enroll

# Verify a voice sample
curl -F "file=@voice.ogg" http://localhost:8200/verify

# List enrolled speakers
curl http://localhost:8200/speakers
```

### Dependencies note

SpeechBrain 1.0.x requires `torch<2.7`, `torchaudio<2.7`, and `huggingface-hub<0.26`. These are pinned in `configs/voice-auth/requirements.txt`.

---

## Personal RAG (Local Knowledge)

Local knowledge base that indexes OpenClaw conversations and memory into ChromaDB, answers personal questions using Ollama qwen3:4b. Zero cloud cost — fully local inference.

| Item | Value |
|------|-------|
| **Location** | `configs/personal-rag/` |
| **Service** | `systemctl --user {status,restart,stop} personal-rag` |
| **Port** | 8300 (localhost only) |
| **Embedding model** | Ollama nomic-embed-text (768d) |
| **Chat model** | Ollama qwen3:4b |
| **Vector store** | ChromaDB at `~/.openclaw/personal-rag/chromadb/` |
| **Skill** | `~/.openclaw/workspace/skills/personal-knowledge/SKILL.md` (always-on) |
| **Setup** | `./scripts/setup-personal-rag.sh` |
| **Plan** | `docs/local-learning-implementation-plan.md` |

### How it works

1. OpenClaw's cloud LLM (Sonnet) sees the `personal-knowledge` skill (always loaded)
2. For personal/routine questions, it calls `curl http://localhost:8300/query`
3. RAG service embeds the query locally, searches ChromaDB, generates answer with qwen3:4b
4. Cloud LLM uses the local answer directly or augments it

### Quick commands

```bash
# Health check
curl http://localhost:8300/health

# Query personal knowledge
curl -s -X POST http://localhost:8300/query -H "Content-Type: application/json" \
  -d '{"query": "What is Arnaldo working on?"}'

# Re-sync from OpenClaw conversations
curl -s -X POST http://localhost:8300/sync

# Check training data stats (for future fine-tuning)
python3 scripts/extract-training-data.py --stats-only
```

### Fine-tuning (when 200+ pairs accumulated)

1. Re-export data: `python3 scripts/extract-training-data.py --filter-preferences --include-memory -o configs/personal-rag/training-data.jsonl`
2. Open `configs/personal-rag/finetune_qwen3_4b.ipynb` in Google Colab (free T4)
3. Upload the JSONL, run all cells, download the GGUF
4. Import: `ollama create anakin-personal -f configs/personal-rag/Modelfile-anakin`
5. Update `personal-rag.service` → `CHAT_MODEL=anakin-personal`, restart

Current stats: 71 total pairs, 12 preference-filtered. See `docs/local-learning-implementation-plan.md`.

---

## Google Calendar (gog CLI)

Multi-calendar management via `gog` CLI (gogcli). Manages personal, shared, family, and subscribed calendars through a single Google OAuth login. Includes proactive morning briefings and meeting reminders via cron jobs.

| Item | Value |
|------|-------|
| **Binary** | `/usr/local/bin/gog` (v0.9.0) |
| **Config** | `~/.config/gogcli/config.json` |
| **Bundled skill** | `gog` (OpenClaw built-in) |
| **ClawHub skill** | `gog-calendar` v1.0.0 (calendar-specific optimizations) |
| **Guide** | `guides/gog-calendar-setup.md` |
| **Env vars** | `GOG_ACCOUNT`, `GOG_KEYRING_PASSWORD` (in systemd unit) |

---

## OpenClaw Config Tuning

| Tuning | Guide | Key Settings |
|--------|-------|-------------|
| Rate limit & context optimization | `guides/openclaw-rate-limit-tuning.md` | `contextTokens: 80000`, `maxConcurrent: 2`, tighter pruning thresholds |
| API cost optimization | `guides/cost-optimization.md` | Gemini Flash primary, Ollama local fallback, OAuth for Claude Code |

**Do not use** `adaptive` or `aggressive` for `contextPruning.mode` — only `off` or `cache-ttl` are valid (others crash the gateway).

---

## Guides & Docs Reference

| Document | Path | Purpose |
|----------|------|---------|
| Enhancement plan (master) | `docs/openclaw-enhancement-plan.md` | Full roadmap with all pending setup steps |
| Voice recognition research | `docs/voice-recognition-research.md` | Speaker ID research (SpeechBrain deployed) |
| Complete research summary | `guides/openclaw-complete-research-summary.md` | OpenClaw overview + 700+ skills catalog |
| Linux installation guide | `guides/detailed-linux-installation-guide.md` | Ubuntu install from scratch |
| Windows migration plan | `guides/windows-to-linux-openclaw-migration-plan.md` | Migration reference (already on Linux) |
| TTS patch guide | `guides/openclaw-tts-patch.md` | /tmp/ path fix for voice note delivery |
| Rate limit tuning | `guides/openclaw-rate-limit-tuning.md` | Context pruning + concurrency settings |
| Cost optimization | `guides/cost-optimization.md` | Gemini Flash, Ollama, OAuth strategies |
| Google Calendar setup | `guides/gog-calendar-setup.md` | gog CLI OAuth + cron setup |
| Voice auth setup | `guides/voice-auth-setup.md` | SpeechBrain enrollment + API reference |
| Local learning plan | `docs/local-learning-implementation-plan.md` | RAG + fine-tuning roadmap |

---

## Sudo Access

The sudo password is stored in the private memory file (not in this repo). Rules:

- **NEVER** use sudo without **explicit permission from the user in the current conversation**
- One-time permission does NOT carry over — ask again every time
- If in doubt, ask before running any sudo command

---

## important-instruction-reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- Never save working files to the root folder
