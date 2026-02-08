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
| **Voice-call Plugin** | 3334 | Running (needs Twilio/Telnyx for calls) | via OpenClaw |

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
| **ClawHub skills** | liveavatar, ollama-local, heygen-avatar-lite, notion-api-skill, trello-api |

### In Progress

| Item | Status | What's left |
|------|--------|-------------|
| **Ollama local models** | Installing | Pull models, configure as fallback sub-agent |
| **Voice Auth enrollment** | Service running, no voiceprint | Send 5-10 voice notes to Moltbot |

### Pending (manual setup required)

| Item | Effort | Guide / Reference |
|------|--------|-------------------|
| **WhatsApp QR pairing** | 5 min | `openclaw channels login` — scan QR |
| **LiveAvatar API key** | 2 min | Get free key from app.liveavatar.com |
| **Google Calendar (gog)** | 15 min | `guides/gog-calendar-setup.md` — OAuth flow, install binary, env vars |
| **OpenHue (Hue lights)** | 10 min | Docker + bridge button press |
| **LG ThinQ AC** | 10 min | PAT token + thinqconnect-mcp |
| **Notion integration** | 5 min | Create integration, share pages, add API key |
| **Trello integration** | 5 min | Get API key + token from trello.com/app-key |
| **Google Gemini API key** | 2 min | aistudio.google.com/apikey — free tier fallback |
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

# Start AIAvatarKit (manual)
./scripts/start-avatar.sh

# Start Voice Auth (manual)
./scripts/start-voice-auth.sh

# Voice Auth health check
curl http://localhost:8200/health
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
