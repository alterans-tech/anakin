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

## OpenClaw Config Tuning

| Tuning | Guide | Key Settings |
|--------|-------|-------------|
| Rate limit & context optimization | `guides/openclaw-rate-limit-tuning.md` | `contextTokens: 80000`, `maxConcurrent: 2`, tighter pruning thresholds |

**Do not use** `adaptive` or `aggressive` for `contextPruning.mode` — only `off` or `cache-ttl` are valid (others crash the gateway).

---

## important-instruction-reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- Never save working files to the root folder
