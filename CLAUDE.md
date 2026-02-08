# Anakin

> **MUST READ: `../.uatu/UATU.md`** — Required framework rules for all tasks.

Personal AI assistant orchestration project - OpenClaw setup and configuration guides.

---

## Project Overview

Anakin provides setup guides, configuration scripts, and automation for deploying personal AI assistants (OpenClaw/Moltbot) on Linux systems.

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
# Run setup script (when available)
./scripts/setup.sh

# Check system requirements
./scripts/check-requirements.sh

# Start AIAvatarKit (avatar chat UI)
./scripts/start-avatar.sh
```

---

## Development

```bash
# Install dependencies (if any)
npm install

# Run tests
npm test

# Lint
npm run lint
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

**Do not use** `adaptive` or `aggressive` for `contextPruning.mode` — only `off` or `cache-ttl` are valid (others crash the gateway).

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
