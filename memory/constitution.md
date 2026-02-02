<!--
Sync Impact Report
==================
Version change: 1.0.0 → 2.0.0 (MINOR bump with significant additions)
Modified principles:
  - "II. Test-Before-Commit" → "II. Test-Before-Destroy" (renamed for clarity)
  - "III. Documentation-Driven" → "IV. Documentation-Driven Development" (reordered)
  - "IV. Cost-Aware" → "III. Cost-Aware Operations" (reordered, expanded)
Added sections:
  - Principle VI: Idempotent Automation (new)
  - Principle VII: Graceful Degradation (new)
  - Project Identity section with tagline
  - OCSAS Security Levels (L1/L2/L3)
  - Post-Installation Verification checklist
  - Quarterly compliance review requirement
Removed sections:
  - None
Templates requiring updates:
  - ⚠ pending: No templates directory exists yet in anakin/templates/
Follow-up TODOs:
  - Create templates/ directory when needed
  - Add plan-template.md, spec-template.md, tasks-template.md
-->

# Anakin Constitution

**Personal AI Assistant Orchestration - OpenClaw Setup & Configuration**

> *"From Windows to personal AI butler in under 3 hours"*

---

## Project Identity

| Field | Value |
|-------|-------|
| **Name** | Anakin |
| **Purpose** | Automated setup assistant for deploying OpenClaw (formerly Moltbot/Clawdbot) personal AI assistants on Linux systems |
| **Target User** | Developer with technical background, no prior OS installation experience |
| **Primary Platform** | Ubuntu 24.04 LTS |

---

## Core Principles

### I. Security-First (CRITICAL)

OpenClaw grants FULL SYSTEM ACCESS. A compromised agent means total machine compromise. This is the "Lethal Trifecta" (Palo Alto Networks):
1. Access to private data (emails, files, calendars)
2. Exposure to untrusted content (web pages, attachments)
3. Ability to communicate externally

**Non-Negotiables**:
- Docker sandbox mode MUST be enabled (`sandbox.mode: "non-main"`)
- Gateway MUST bind to loopback only (`gateway.bind: "loopback"`)
- Public access MUST use Tailscale VPN; direct exposure is PROHIBITED
- DM pairing MUST require approval (`dmPolicy: "pairing"`)
- File permissions MUST be 700 (directories) and 600 (files) on ~/.openclaw
- Dedicated accounts MUST be used; NEVER connect personal email/browser
- Skills MUST be reviewed before enabling (14 malicious skills found on ClawHub in Jan 2026)
- Browser profiles MUST be dedicated; treat browser access as operator access

---

### II. Test-Before-Destroy

Irreversible actions (wiping Windows, deleting data) MUST be preceded by verification.

**Non-Negotiables**:
- Live USB testing MUST complete before OS installation
- ALL hardware (WiFi, display, audio, touchpad, keyboard, USB, webcam, Bluetooth) MUST pass testing
- Credential backup MUST be verified readable before proceeding
- Test results MUST be documented with checkboxes before any destructive action
- If critical hardware fails with no known fix → dual boot or reconsider platform

---

### III. Cost-Aware Operations

OpenClaw is free. API usage is NOT. Costs range from $10/month to $3,700+/month.

**Non-Negotiables**:
- Document expected costs for each usage tier (light/moderate/heavy/power)
- Include cost warnings in all automation documentation
- Runaway loops MUST be highlighted (single monitoring cron = $128/month)
- Usage monitoring MUST be enabled (`openclaw status --usage`)
- Model selection guidance MUST be provided: Haiku for simple, Sonnet for moderate, Opus for complex
- Cost alerts SHOULD be configurable

**Cost Reference**:
| Usage Level | Monthly Cost | Token Usage |
|-------------|--------------|-------------|
| Light | $10-30 | 2-5M tokens |
| Moderate | $35-95 | 5-15M tokens |
| Heavy | $210-525 | 15-50M tokens |
| Power User | $500-3,700+ | 50-180M tokens |

---

### IV. Documentation-Driven Development

Every process MUST be reproducible by a developer who has never done it before.

**Non-Negotiables**:
- Step-by-step guides with exact commands (copy-pasteable)
- Expected outputs shown for verification
- Visual guides for BIOS/boot menus (ASCII diagrams acceptable)
- Troubleshooting sections for common failures
- Sources MUST be cited for external procedures
- Version/date stamps on all guides

---

### V. Local-First Privacy

Personal AI assistants MUST run on user-owned hardware with user-controlled data.

**Non-Negotiables**:
- No cloud dependencies for core functionality
- All data stored locally in ~/.openclaw
- User controls what data leaves the machine
- Only external communication: API calls to user's chosen model provider
- Memory stored as local Markdown (inspectable, editable)
- Sessions logged locally (transcripts at `~/.openclaw/agents/*/sessions/`)

---

### VI. Idempotent Automation

Scripts MUST be safe to re-run without side effects.

**Non-Negotiables**:
- All scripts MUST check current state before making changes
- Running a script twice MUST produce the same result as running once
- Scripts MUST NOT fail if already in target state
- Backup before modify; rollback if failure
- Progress indicators MUST be shown for long operations
- Clear success/failure output MUST be provided

---

### VII. Graceful Degradation

Partial failures MUST NOT block the entire workflow.

**Non-Negotiables**:
- If one channel fails (WhatsApp), others MUST still work (Telegram)
- If one skill fails to install, continue with others
- Network failures MUST retry with exponential backoff
- Human intervention points MUST be clearly marked (QR codes, OAuth flows)
- Offline mode MUST be available for configuration preparation

---

## Security Requirements

OpenClaw presents the "Lethal Trifecta" (Palo Alto Networks):
1. Access to private data (emails, files, calendars)
2. Exposure to untrusted content (web pages, attachments)
3. Ability to communicate externally

### OCSAS Security Levels

| Level | Name | Use Case | Key Controls |
|-------|------|----------|--------------|
| **L1** | Solo/Local | Individual user | Loopback binding, token auth, pairing DMs |
| **L2** | Team/Network | Family/team | Session isolation, group mention gating, sandbox |
| **L3** | Enterprise | Compliance needs | Full sandboxing, mDNS disabled, audit logging |

### Mandatory Mitigations

| Control | Configuration |
|---------|---------------|
| Sandbox Mode | `agents.defaults.sandbox.mode: "non-main"` |
| Gateway Binding | `gateway.bind: "loopback"` |
| DM Policy | `channels.whatsapp.dmPolicy: "pairing"` |
| File Permissions | `chmod 700 ~/.openclaw && chmod 600 ~/.openclaw/openclaw.json` |
| Network Access | Tailscale VPN for remote access; never expose gateway publicly |

### Security Audit Commands

Run these commands regularly:
```bash
openclaw security audit --deep
openclaw security audit --fix
openclaw health
```

---

## Operational Standards

### System Requirements

| Requirement | Value |
|-------------|-------|
| OS | Ubuntu 24.04 LTS (primary), Debian-based (secondary) |
| Node.js | 22+ |
| RAM | 4GB minimum |
| Storage | 8GB+ for OS, additional for OpenClaw data |

### Pre-Installation Checklist

Before any OS installation:
- [ ] Browser passwords exported to CSV on external drive
- [ ] WiFi passwords documented
- [ ] Files backed up to external drive/cloud
- [ ] API keys saved (Anthropic/OpenAI)
- [ ] 2FA recovery codes saved
- [ ] Hardware tested in live USB environment
- [ ] Anthropic API key obtained (recommended provider)

### Post-Installation Verification

After installation:
- [ ] Node.js version 22+ confirmed (`node --version`)
- [ ] OpenClaw status shows healthy (`openclaw status`)
- [ ] Gateway running as daemon (`openclaw gateway status`)
- [ ] At least one channel connected
- [ ] Security audit passes (`openclaw security audit --deep`)

---

## Governance

This constitution supersedes all other practices for Anakin project development.

### Amendment Process

1. Propose change with rationale
2. Document impact on existing guides
3. Update all affected documentation
4. Increment version per semantic versioning

### Versioning Policy

| Change Type | Version Bump | Example |
|-------------|--------------|---------|
| Principle removal or incompatible redefinition | MAJOR | 2.0.0 → 3.0.0 |
| New principle or section added | MINOR | 2.0.0 → 2.1.0 |
| Clarifications, typos, non-semantic changes | PATCH | 2.0.0 → 2.0.1 |

### Compliance Review

- All guides MUST align with security principles
- All scripts MUST include safety checks
- All documentation MUST cite sources for external procedures
- Quarterly security audit of all materials MUST be conducted

---

## Reference Sources

This constitution is based on research from:
- [OpenClaw Official Documentation](https://docs.openclaw.ai)
- [OCSAS Security Framework](https://github.com/gensecaihq/ocsas)
- Security analyses from Cisco, Palo Alto Networks, Dark Reading
- Cost analyses from Fast Company, eesel.ai, user reports
- Community guides and real-world deployment experiences

---

**Version**: 2.0.0 | **Ratified**: 2026-02-02 | **Last Amended**: 2026-02-02
