# Anakin - OpenClaw Setup Assistant

## Speckit Specification Prompt

Use this prompt with `/speckit.specify` to generate the project specification.

---

## Prompt

```
Anakin: An automated setup assistant for deploying OpenClaw (formerly Moltbot/Clawdbot) on Linux systems.

## Vision

A CLI tool and collection of scripts that automates the entire journey from Windows laptop to fully configured OpenClaw personal AI assistant—handling credential backup, Linux installation guidance, OpenClaw setup, security hardening, and ongoing management.

## Target User

Developer with technical background but no experience with OS installation or self-hosted AI assistants. Has a 2018 Dell laptop, wants to wipe Windows and run OpenClaw on Ubuntu.

## Problem Statement

1. **Complex migration**: Moving from Windows to Linux requires backing up credentials, creating bootable media, testing hardware compatibility, and installing the OS—each step has gotchas.

2. **OpenClaw setup friction**: OpenClaw requires Node.js 22+, proper gateway configuration, channel authentication (WhatsApp QR codes, Telegram tokens), security hardening, and skill installation.

3. **Security complexity**: OpenClaw has full system access—users need proper sandboxing (Docker), network isolation (Tailscale), file permissions (700/600), and DM pairing policies.

4. **Cost surprises**: API costs can reach $400+/month without monitoring. Users need usage tracking and alerts.

5. **No unified tool**: Currently users must follow multiple guides, run manual commands, and remember configuration steps.

## Core Features

### Phase 1: Pre-Migration (Windows)
- Credential backup wizard (browser passwords, WiFi passwords, SSH keys)
- Bootable USB creator (wrapper around Rufus/Balena Etcher)
- Hardware compatibility checker (fetch Dell model info, check known issues)
- Checklist generator (personalized pre-migration checklist)

### Phase 2: Linux Setup Guidance
- Interactive installation guide (step-by-step with screenshots/descriptions)
- Hardware test script (run in live USB to verify WiFi, audio, display, touchpad)
- Post-install setup script (updates, drivers, essential packages)
- Node.js 22 installer

### Phase 3: OpenClaw Installation
- One-command OpenClaw installer with sensible defaults
- Interactive onboarding (API key setup, model selection)
- Channel setup wizards (WhatsApp, Telegram, Discord)
- Gateway configuration generator (secure defaults)
- Daemon installer (systemd service)

### Phase 4: Security Hardening
- Security audit runner (wraps `openclaw security audit`)
- Docker sandbox configurator
- Tailscale VPN setup assistant
- File permission fixer (700/600 on ~/.openclaw)
- DM policy configurator (pairing mode by default)
- Dedicated account setup guide (separate email, browser profile)

### Phase 5: Skills & Customization
- Skill browser and installer (wraps clawhub)
- Popular skills bundle installer (Obsidian, GitHub, Calendar)
- Custom skill scaffolder
- IDENTITY.md generator (persona configuration)

### Phase 6: Management & Monitoring
- Status dashboard (gateway, channels, API usage)
- Cost tracker with alerts (daily/weekly/monthly reports)
- Health checker (connectivity, authentication, disk space)
- Backup/restore for OpenClaw configuration
- Update manager

## Technical Constraints

- **Primary language**: Bash scripts + Python for complex logic
- **Target OS**: Ubuntu 24.04 LTS (primary), other Debian-based (secondary)
- **Dependencies**: Minimal—should work with base Ubuntu install
- **No GUI required**: CLI-first, but can output to web dashboard later
- **Idempotent**: Scripts can be re-run safely

## Success Criteria

1. User can go from Windows laptop to working OpenClaw in under 3 hours
2. All security best practices applied by default
3. User understands their monthly cost within first week
4. Zero credential exposure during migration
5. Hardware compatibility issues detected BEFORE wiping Windows

## Out of Scope

- Windows-native OpenClaw setup (WSL only mentioned in docs)
- macOS setup (different project)
- Enterprise/multi-tenant deployment
- Custom AI model training
- Building OpenClaw itself (we configure, not develop)

## Reference Materials

The following guides in `guides/` inform this specification:
- `windows-to-linux-openclaw-migration-plan.md` - Migration phases
- `detailed-linux-installation-guide.md` - USB creation, BIOS, live testing
- `openclaw-complete-research-summary.md` - Features, costs, security, skills
```

---

## Usage

Run the following command in the anakin project directory:

```bash
/speckit.specify
```

Then paste the prompt above (everything between the ``` markers).

---

## Expected Output

The speckit will generate a `spec.md` with:
- Prioritized user stories (P1-P3)
- Functional requirements
- Acceptance criteria
- Edge cases
- Success metrics

---

## Notes

- This is a **tools/scripts project**, not a web application
- Focus on CLI experience and automation
- Security is a first-class concern throughout
- Cost awareness is critical given OpenClaw's API pricing
