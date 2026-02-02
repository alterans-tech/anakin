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

## important-instruction-reminders

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary
- ALWAYS prefer editing existing files
- Never save working files to the root folder
