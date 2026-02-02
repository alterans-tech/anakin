# Feature Specification: Anakin - OpenClaw Setup Assistant

**Feature Branch**: `00-foundation`
**Created**: 2026-02-02
**Status**: Draft
**Input**: Automated setup assistant for deploying OpenClaw personal AI assistants on Linux systems

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Pre-Migration Credential Backup (Priority: P1)

A developer with a Windows laptop wants to safely backup all credentials before wiping the system to install Linux. They need confidence that nothing critical will be lost.

**Why this priority**: Zero credential loss is a foundational requirement. Without safe backup, users risk losing access to accounts, services, and data permanently. This must work before any destructive action.

**Independent Test**: User runs the credential backup wizard on Windows, receives a checklist of items backed up, and can verify the backup is readable on an external drive before proceeding.

**Acceptance Scenarios**:

1. **Given** a Windows system with browser passwords, **When** user runs the credential backup wizard, **Then** all passwords are exported to CSV on the specified external drive
2. **Given** saved WiFi networks on Windows, **When** user runs the backup wizard, **Then** all WiFi passwords are extracted and documented
3. **Given** SSH keys in user's .ssh folder, **When** user runs the backup wizard, **Then** all SSH keys are copied to the backup location
4. **Given** API keys for various services, **When** user runs the backup wizard, **Then** a template is generated prompting user to document each API key location
5. **Given** 2FA recovery codes stored locally, **When** user runs the backup wizard, **Then** user is prompted to verify and backup each 2FA recovery code

---

### User Story 2 - Hardware Compatibility Testing (Priority: P1)

A developer wants to verify their laptop's hardware works with Linux before wiping Windows. They need to test WiFi, display, audio, touchpad, keyboard, USB, webcam, and Bluetooth in a live USB environment.

**Why this priority**: Testing hardware BEFORE destroying Windows prevents catastrophic scenarios where critical hardware (like WiFi) doesn't work, leaving the user with an unusable system.

**Independent Test**: User boots into live USB, runs the hardware test script, and receives a clear pass/fail report for each component before making any installation decision.

**Acceptance Scenarios**:

1. **Given** a live Ubuntu USB boot, **When** user runs the hardware test script, **Then** WiFi adapter is detected and can connect to a network
2. **Given** a live Ubuntu USB boot, **When** user runs the hardware test script, **Then** display resolution and brightness controls are verified working
3. **Given** a live Ubuntu USB boot, **When** user runs the hardware test script, **Then** audio output and input are tested with user confirmation
4. **Given** a live Ubuntu USB boot, **When** user runs the hardware test script, **Then** touchpad gestures and keyboard function keys are verified
5. **Given** any hardware component failing, **When** user views the test report, **Then** clear recommendation is shown (proceed, dual-boot, or reconsider)

---

### User Story 3 - One-Command OpenClaw Installation (Priority: P1)

A developer with a fresh Ubuntu installation wants to install OpenClaw with sensible secure defaults using a single command, without needing to understand all configuration options upfront.

**Why this priority**: This is the core value proposition. If installation is complex, users won't adopt the tool. One-command setup with secure defaults is essential for the "under 3 hours" goal.

**Independent Test**: User runs a single install command on fresh Ubuntu, completes interactive prompts for API key and model selection, and has a working OpenClaw installation with security hardening applied.

**Acceptance Scenarios**:

1. **Given** Ubuntu 24.04 with no prerequisites, **When** user runs the install command, **Then** Node.js 22+ is automatically installed if missing
2. **Given** OpenClaw installation in progress, **When** prompted for API key, **Then** user can paste their Anthropic API key and have it validated
3. **Given** successful API key entry, **When** installation completes, **Then** OpenClaw gateway is running as a systemd daemon
4. **Given** installation completes, **When** user runs status check, **Then** security audit passes with all mandatory mitigations applied
5. **Given** installation completes, **When** user checks file permissions, **Then** ~/.openclaw is 700 and config files are 600

---

### User Story 4 - Channel Setup Wizard (Priority: P2)

A developer wants to connect messaging channels (WhatsApp, Telegram, Discord) to their OpenClaw instance so they can interact with their AI assistant through familiar interfaces.

**Why this priority**: While OpenClaw can work without channels, the primary use case involves messaging. However, the base installation is functional without channels, making this P2.

**Independent Test**: User runs a channel setup wizard, follows prompts for their chosen channel (e.g., WhatsApp QR code scan), and can send a test message that receives an AI response.

**Acceptance Scenarios**:

1. **Given** a running OpenClaw gateway, **When** user selects WhatsApp setup, **Then** a QR code is displayed for authentication
2. **Given** successful WhatsApp authentication, **When** user sends a test message, **Then** OpenClaw responds through WhatsApp
3. **Given** a running OpenClaw gateway, **When** user selects Telegram setup, **Then** they are guided through bot token creation and configuration
4. **Given** DM pairing mode enabled, **When** an unknown sender messages the bot, **Then** pairing approval is required before responding

---

### User Story 5 - Cost Monitoring Dashboard (Priority: P2)

A developer wants to monitor their API usage costs to avoid surprise bills, with alerts when spending exceeds thresholds.

**Why this priority**: Cost awareness is critical but not blocking for initial use. Users can start using OpenClaw before setting up monitoring, but should do so within the first week.

**Independent Test**: User views the cost dashboard showing current usage, historical trends, and receives an alert when approaching a configured threshold.

**Acceptance Scenarios**:

1. **Given** OpenClaw with API usage, **When** user runs status dashboard, **Then** current day/week/month token usage and estimated cost is displayed
2. **Given** configured cost threshold, **When** usage approaches 80% of threshold, **Then** user receives a warning notification
3. **Given** historical usage data, **When** user views dashboard, **Then** trend graph shows daily costs for the past 30 days
4. **Given** different model usage, **When** user views breakdown, **Then** costs are separated by model tier (Haiku/Sonnet/Opus)

---

### User Story 6 - Security Hardening Verification (Priority: P2)

A developer wants to verify their OpenClaw installation meets security best practices and fix any issues found automatically.

**Why this priority**: Security is applied by default during installation, but users need ongoing verification. This enables periodic audits and remediation.

**Independent Test**: User runs security audit command, sees a report of all security controls and their status, and can auto-fix any issues found.

**Acceptance Scenarios**:

1. **Given** an OpenClaw installation, **When** user runs security audit, **Then** a report shows status of each OCSAS L1 control
2. **Given** sandbox mode disabled, **When** user runs security audit, **Then** it's flagged as a critical finding with fix command provided
3. **Given** security issues found, **When** user runs audit with --fix flag, **Then** all auto-fixable issues are remediated
4. **Given** issues requiring manual intervention, **When** user views audit report, **Then** clear instructions are provided for each manual fix

---

### User Story 7 - Skill Installation (Priority: P3)

A developer wants to extend OpenClaw's capabilities by installing skills from ClawHub (e.g., Obsidian, GitHub, Calendar integration).

**Why this priority**: Skills enhance OpenClaw but aren't required for basic functionality. Users can have a working assistant without any skills installed.

**Independent Test**: User browses available skills, installs one (e.g., Obsidian), and can use the new capability through their connected channel.

**Acceptance Scenarios**:

1. **Given** ClawHub access, **When** user runs skill browser, **Then** list of available skills with descriptions and ratings is shown
2. **Given** a selected skill, **When** user initiates install, **Then** skill source is shown for review before installation
3. **Given** skill installation, **When** user checks status, **Then** skill is listed as active and its capabilities are documented
4. **Given** a known malicious skill, **When** user attempts install, **Then** warning is displayed citing known security issues

---

### User Story 8 - Backup and Restore (Priority: P3)

A developer wants to backup their OpenClaw configuration so they can restore it on a new system or recover from issues.

**Why this priority**: Important for data safety but not blocking for initial use. Users typically need this after they've customized their setup.

**Independent Test**: User creates a backup, can view its contents, and successfully restores to a fresh OpenClaw installation.

**Acceptance Scenarios**:

1. **Given** a configured OpenClaw installation, **When** user runs backup command, **Then** configuration, skills, and memory are archived
2. **Given** a backup archive, **When** user runs restore on fresh install, **Then** all settings and data are restored
3. **Given** sensitive data in backup, **When** backup is created, **Then** user is warned about securing the backup file

---

### Edge Cases

- What happens when the user's laptop has no WiFi driver support in live USB?
  - Display clear warning and suggest USB WiFi adapter or ethernet
- What happens when the user's Anthropic API key is invalid?
  - Validate on entry, provide clear error, allow retry without restarting install
- What happens when OpenClaw installation fails midway?
  - Scripts are idempotent; re-running continues from failure point
- What happens when gateway port is already in use?
  - Detect conflict, offer alternative port, or help identify conflicting process
- What happens when user loses internet during installation?
  - Cache downloaded components where possible; resume on reconnection
- What happens when channel authentication expires?
  - Notify user, provide re-authentication steps
- What happens when disk space is insufficient?
  - Check before installation, provide clear minimum requirements

---

## Requirements *(mandatory)*

### Functional Requirements

**Pre-Migration (Windows)**

- **FR-001**: System MUST export browser passwords to CSV format on user-specified external storage
- **FR-002**: System MUST extract and document all saved WiFi passwords
- **FR-003**: System MUST copy SSH keys and provide verification of successful copy
- **FR-004**: System MUST generate a pre-migration checklist tracking all credential categories
- **FR-005**: System MUST support creating bootable Ubuntu USB drives

**Hardware Testing**

- **FR-006**: System MUST test WiFi adapter detection and connectivity in live USB environment
- **FR-007**: System MUST verify display functionality including resolution and brightness controls
- **FR-008**: System MUST test audio input/output with user confirmation
- **FR-009**: System MUST verify touchpad, keyboard function keys, and special keys
- **FR-010**: System MUST generate a hardware compatibility report with pass/fail for each component
- **FR-011**: System MUST provide clear recommendations based on test results (proceed/dual-boot/reconsider)

**OpenClaw Installation**

- **FR-012**: System MUST install Node.js 22+ if not present
- **FR-013**: System MUST install OpenClaw with a single command
- **FR-014**: System MUST prompt for and validate API key during setup
- **FR-015**: System MUST configure OpenClaw gateway with secure defaults (loopback binding, sandbox mode)
- **FR-016**: System MUST set file permissions to 700 for ~/.openclaw directory and 600 for config files
- **FR-017**: System MUST install and enable OpenClaw as a systemd service
- **FR-018**: System MUST apply all OCSAS L1 security controls by default

**Channel Management**

- **FR-019**: System MUST provide guided setup for WhatsApp channel including QR code display
- **FR-020**: System MUST provide guided setup for Telegram channel including bot token configuration
- **FR-021**: System MUST enable DM pairing mode by default requiring approval for unknown senders
- **FR-022**: System MUST verify channel connectivity with test message capability

**Security**

- **FR-023**: System MUST run comprehensive security audit on demand
- **FR-024**: System MUST auto-remediate fixable security issues when requested
- **FR-025**: System MUST warn about manual intervention items with clear instructions
- **FR-026**: System MUST prevent installation of known malicious skills

**Monitoring**

- **FR-027**: System MUST display current API usage and estimated costs
- **FR-028**: System MUST track historical usage with daily granularity
- **FR-029**: System MUST support configurable cost threshold alerts
- **FR-030**: System MUST break down costs by model tier

**Skills**

- **FR-031**: System MUST browse and display available skills from ClawHub
- **FR-032**: System MUST show skill source code for review before installation
- **FR-033**: System MUST track installed skills and their status

**Management**

- **FR-034**: System MUST backup OpenClaw configuration, skills, and memory
- **FR-035**: System MUST restore from backup to fresh installation
- **FR-036**: System MUST check OpenClaw health including connectivity, auth, and disk space

**Cross-Cutting**

- **FR-037**: All scripts MUST be idempotent (safe to re-run without side effects)
- **FR-038**: All scripts MUST provide clear progress indicators for long operations
- **FR-039**: All scripts MUST output clear success/failure messages
- **FR-040**: All operations MUST NOT block the entire workflow on partial failures

---

### Key Entities

- **Credential Set**: Collection of backed-up credentials (browser passwords, WiFi passwords, SSH keys, API keys, 2FA codes) with backup timestamp and verification status
- **Hardware Report**: Test results for each hardware component (WiFi, display, audio, touchpad, keyboard, USB, webcam, Bluetooth) with status and recommendations
- **OpenClaw Installation**: Configuration state including gateway settings, security controls, connected channels, installed skills, and API configuration
- **Channel**: Connected messaging platform (WhatsApp, Telegram, Discord) with authentication status and pairing mode settings
- **Skill**: Installed capability from ClawHub with source, status, and security review state
- **Usage Record**: API usage data including token counts, model tier, timestamp, and calculated cost
- **Backup Archive**: Snapshot of OpenClaw configuration, skills, and memory with creation timestamp

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users complete the entire journey from Windows laptop to working OpenClaw in under 3 hours
- **SC-002**: 100% of installations have all OCSAS L1 security controls applied by default
- **SC-003**: Zero credential loss during migration when using the backup wizard
- **SC-004**: Hardware compatibility issues are detected before Windows is wiped in 100% of cases
- **SC-005**: Users understand their expected monthly API cost within the first week of use
- **SC-006**: Installation script successfully completes on first run in 95% of cases (no manual intervention)
- **SC-007**: At least one messaging channel can be connected within 15 minutes of installation completion
- **SC-008**: Security audit identifies and provides fix commands for 100% of auto-remediable issues
- **SC-009**: All scripts can be safely re-run without causing errors or unintended state changes
- **SC-010**: Partial failures (e.g., one channel failing) do not block other functionality from working

---

## Assumptions

1. **Target Hardware**: 2018 or newer laptops with Intel/AMD processors; exotic hardware may require manual driver installation
2. **Network Availability**: Reliable internet connection available during installation; offline mode covers configuration preparation only
3. **User Skill Level**: Users can follow CLI instructions, boot from USB, and navigate BIOS menus with visual guidance
4. **API Provider**: Anthropic is the recommended and default API provider; other providers may work but are not explicitly supported
5. **Ubuntu Version**: Primary support for Ubuntu 24.04 LTS; other Debian-based distributions may work but are not tested
6. **Browser Support**: Credential export supports Chromium-based browsers and Firefox; other browsers may require manual export
7. **External Storage**: Users have access to USB drive or external storage for credential backup
8. **Cost Ranges**: API costs are based on current Anthropic pricing; actual costs may vary with pricing changes

---

## Dependencies

1. **OpenClaw**: Upstream OpenClaw project must remain available and maintain current installation method
2. **ClawHub**: Skill marketplace availability for skill browsing and installation features
3. **Ubuntu Repositories**: Standard package availability for Node.js and dependencies
4. **Anthropic API**: API availability and key validation endpoints

---

## Out of Scope

- Windows-native OpenClaw setup (WSL-only mentioned in upstream docs)
- macOS setup (separate project)
- Enterprise/multi-tenant deployment
- Custom AI model training
- Building or modifying OpenClaw itself (we configure, not develop)
- Support for non-Debian-based Linux distributions
- Graphical user interface (CLI-first approach)
