# Anakin - Constitution Prompt

Use this prompt with `/speckit.constitution` to create or refine the project constitution.

---

## Prompt

```
Anakin Constitution for OpenClaw Setup Assistant

## Project Identity

**Name**: Anakin
**Purpose**: Automated setup assistant for deploying OpenClaw (formerly Moltbot/Clawdbot) personal AI assistants on Linux systems.
**Tagline**: "From Windows to personal AI butler in under 3 hours"

## Core Principles (7 total)

### I. Security-First (CRITICAL)

OpenClaw grants FULL SYSTEM ACCESS. A compromised agent means total machine compromise. This is the "Lethal Trifecta" (Palo Alto Networks):
1. Access to private data (emails, files, calendars)
2. Exposure to untrusted content (web pages, attachments)
3. Ability to communicate externally

**Non-Negotiables**:
- Docker sandbox mode MUST be enabled (`sandbox.mode: "non-main"`)
- Gateway MUST bind to loopback only (`gateway.bind: "loopback"`)
- Public access MUST use Tailscale VPN, never direct exposure
- DM pairing MUST require approval (`dmPolicy: "pairing"`)
- File permissions MUST be 700 (dirs) and 600 (files) on ~/.openclaw
- Dedicated accounts MUST be used - NEVER personal email/browser
- Skills MUST be reviewed before enabling - 14 malicious skills found on ClawHub in Jan 2026
- Browser profiles MUST be dedicated - treat browser access as operator access

### II. Test-Before-Destroy

Irreversible actions (wiping Windows, deleting data) MUST be preceded by verification.

**Non-Negotiables**:
- Live USB testing MUST complete before OS installation
- ALL hardware (WiFi, display, audio, touchpad, keyboard, USB, webcam, Bluetooth) MUST pass testing
- Credential backup MUST be verified readable before proceeding
- Document test results with checkboxes before any destructive action
- If critical hardware fails with no known fix → dual boot or reconsider

### III. Cost-Aware Operations

OpenClaw is free. API usage is NOT. Costs range from $10/month to $3,700+/month.

**Non-Negotiables**:
- Document expected costs for each usage tier (light/moderate/heavy/power)
- Include cost warnings in all automation documentation
- Runaway loops MUST be highlighted (single monitoring cron = $128/month)
- Usage monitoring MUST be enabled (`openclaw status --usage`)
- Model selection guidance: Haiku for simple, Sonnet for moderate, Opus for complex
- Cost alerts SHOULD be configurable

### IV. Documentation-Driven Development

Every process MUST be reproducible by a developer who has never done it before.

**Non-Negotiables**:
- Step-by-step guides with exact commands (copy-pasteable)
- Expected outputs shown for verification
- Visual guides for BIOS/boot menus (ASCII diagrams acceptable)
- Troubleshooting sections for common failures
- Sources cited for external procedures
- Version/date stamps on all guides

### V. Local-First Privacy

Personal AI assistants run on user-owned hardware with user-controlled data.

**Non-Negotiables**:
- No cloud dependencies for core functionality
- All data stored locally in ~/.openclaw
- User controls what data leaves the machine
- Only external communication: API calls to user's chosen model provider
- Memory stored as local Markdown (inspectable, editable)
- Sessions logged locally (transcripts at ~/.openclaw/agents/*/sessions/)

### VI. Idempotent Automation

Scripts can be re-run safely without side effects.

**Non-Negotiables**:
- All scripts MUST check current state before making changes
- Running a script twice MUST produce the same result as running once
- Scripts MUST NOT fail if already in target state
- Backup before modify - rollback if failure
- Progress indicators for long operations
- Clear success/failure output

### VII. Graceful Degradation

Partial failures should not block the entire workflow.

**Non-Negotiables**:
- If one channel fails (WhatsApp), others should still work (Telegram)
- If one skill fails to install, continue with others
- Network failures should retry with exponential backoff
- Human intervention points clearly marked (QR codes, OAuth flows)
- Offline mode for configuration preparation

## Security Requirements Section

Include the OCSAS security levels:

| Level | Name | Use Case | Key Controls |
|-------|------|----------|--------------|
| L1 | Solo/Local | Individual user | Loopback binding, token auth, pairing DMs |
| L2 | Team/Network | Family/team | Session isolation, group mention gating, sandbox |
| L3 | Enterprise | Compliance needs | Full sandboxing, mDNS disabled, audit logging |

Include mandatory security audit commands:
```bash
openclaw security audit --deep
openclaw security audit --fix
openclaw health
```

## Operational Standards Section

### System Requirements
- OS: Ubuntu 24.04 LTS (primary), Debian-based (secondary)
- Node.js: 22+
- RAM: 4GB minimum
- Storage: 8GB+ for OS, additional for OpenClaw data

### Pre-Installation Checklist
- [ ] Browser passwords exported to CSV on external drive
- [ ] WiFi passwords documented
- [ ] Files backed up to external drive/cloud
- [ ] API keys saved (Anthropic/OpenAI)
- [ ] 2FA recovery codes saved
- [ ] Hardware tested in live USB environment
- [ ] Anthropic API key obtained (recommended provider)

### Post-Installation Verification
- [ ] Node.js version 22+ confirmed
- [ ] OpenClaw status shows healthy
- [ ] Gateway running as daemon
- [ ] At least one channel connected
- [ ] Security audit passes

## Governance Section

### Amendment Process
1. Propose change with rationale
2. Document impact on existing guides
3. Update all affected documentation
4. Increment version per semantic versioning

### Versioning Policy
- MAJOR: Principle removal or incompatible redefinition
- MINOR: New principle or section added
- PATCH: Clarifications, typos, non-semantic changes

### Compliance Review
- All guides MUST align with security principles
- All scripts MUST include safety checks
- All documentation MUST cite sources for external procedures
- Quarterly security audit of all materials

## Reference Context

Based on research from:
- OpenClaw official documentation (docs.openclaw.ai)
- OCSAS Security Framework (github.com/gensecaihq/ocsas)
- Security analyses from Cisco, Palo Alto Networks, Dark Reading
- Cost analyses from Fast Company, eesel.ai, user reports
- Community guides and real-world deployment experiences
```

---

## Usage

Run the following command in the anakin project directory:

```bash
/speckit.constitution
```

Then paste the prompt above (everything between the ``` markers).

---

## What This Generates

The speckit will:
1. Update `/memory/constitution.md` with the 7 principles
2. Add detailed security requirements (OCSAS levels)
3. Add operational standards (checklists)
4. Set up governance with versioning policy
5. Generate a Sync Impact Report
6. Suggest follow-up actions for template updates

---

## Notes

- The current constitution is v1.0.0 with 5 principles
- This prompt expands to 7 principles with more operational detail
- Security is emphasized given OpenClaw's full system access
- Cost awareness is elevated to principle level
- Adds OCSAS security levels for different deployment scenarios
