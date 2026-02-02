# Tasks: Windows to Ubuntu Migration Guide

**Feature**: `00-foundation`
**Created**: 2026-02-02
**Plan**: [plan.md](./plan.md)
**Spec**: [spec.md](./spec.md)

---

## Jira Structure

This task breakdown maps to Jira hierarchy:

| Jira Type | Mapping |
|-----------|---------|
| **Epic** | Phase (major milestone) |
| **Story** | User Story from spec |
| **Task** | Individual work item |
| **Subtask** | Checklist item within task |

---

## Epic 1: Create Bootable Ubuntu USB (Phase 0)

**Epic Key**: ANI-E1
**Priority**: Highest (DO FIRST - enables all other phases)
**Description**: Download Ubuntu ISO, verify integrity, create bootable USB drive

### Story: US0 - Create Bootable Ubuntu USB

**Story Key**: ANI-S0
**Points**: 2
**Acceptance**: User has verified bootable USB that successfully boots on Dell laptop

#### Tasks

- [ ] T001 [US0] Download Ubuntu 24.04.1 LTS ISO from ubuntu.com/download/desktop
- [ ] T002 [US0] Verify ISO checksum matches official SHA256 hash
- [ ] T003 [US0] Download and install Rufus from rufus.ie
- [ ] T004 [US0] Create bootable USB with Rufus (GPT, UEFI, FAT32 Large)
- [ ] T005 [US0] Test USB boots to Ubuntu live environment (F12 at Dell logo)

#### Documentation Tasks

- [ ] T006 [P] [US0] Write guide section: Download Ubuntu ISO in `guides/windows-to-ubuntu-migration.md`
- [ ] T007 [P] [US0] Write guide section: Verify ISO Checksum in `guides/windows-to-ubuntu-migration.md`
- [ ] T008 [P] [US0] Write guide section: Create Bootable USB with Rufus in `guides/windows-to-ubuntu-migration.md`
- [ ] T009 [P] [US0] Add Rufus settings screenshot/diagram to `guides/images/`

---

## Epic 2: Windows Preparation (Phase 1)

**Epic Key**: ANI-E2
**Priority**: High
**Description**: Backup all critical data and preserve Windows license before any destructive action

### Story: US1 - Preserve Windows License Key

**Story Key**: ANI-S1
**Points**: 1
**Acceptance**: Windows product key and Dell Service Tag documented on external storage

#### Tasks

- [ ] T010 [US1] Extract Windows product key using PowerShell command
- [ ] T011 [US1] Document Dell Service Tag (laptop bottom or `wmic bios get serialnumber`)
- [ ] T012 [US1] Save key + Service Tag to external storage with date

#### Documentation Tasks

- [ ] T013 [P] [US1] Write guide section: Extract Windows License Key in `guides/windows-to-ubuntu-migration.md`
- [ ] T014 [P] [US1] Write guide section: Dell OEM Licensing Explained in `guides/windows-to-ubuntu-migration.md`

---

### Story: US4 - Backup Critical Data

**Story Key**: ANI-S4
**Points**: 3
**Acceptance**: All credentials and files backed up to external storage and verified readable

#### Tasks

- [ ] T015 [US4] Export browser passwords (Chrome/Edge/Firefox) to CSV on external drive
- [ ] T016 [US4] Document all WiFi passwords using netsh command
- [ ] T017 [US4] Copy SSH keys from ~/.ssh to external storage
- [ ] T018 [US4] Copy important files/documents to external storage
- [ ] T019 [US4] Save API keys (Anthropic, OpenAI, etc.) to secure location
- [ ] T020 [US4] Save 2FA recovery codes
- [ ] T021 [US4] Verify all backups are readable on external storage

#### Documentation Tasks

- [ ] T022 [P] [US4] Write guide section: Export Browser Passwords in `guides/windows-to-ubuntu-migration.md`
- [ ] T023 [P] [US4] Write guide section: Document WiFi Passwords in `guides/windows-to-ubuntu-migration.md`
- [ ] T024 [P] [US4] Write guide section: Backup SSH Keys in `guides/windows-to-ubuntu-migration.md`
- [ ] T025 [P] [US4] Create pre-migration checklist in `checklists/pre-migration.md`

---

## Epic 3: Hardware Testing (Phase 2)

**Epic Key**: ANI-E3
**Priority**: High
**Description**: Test all hardware in Ubuntu live environment BEFORE wiping Windows

### Story: US2 - Test Hardware on Ubuntu Live USB

**Story Key**: ANI-S2
**Points**: 2
**Acceptance**: All critical hardware (WiFi, display, audio, input) tested with clear pass/fail results

#### Tasks

- [ ] T026 [US2] Boot Dell laptop from Ubuntu USB (F12 → select USB)
- [ ] T027 [US2] Test WiFi: scan networks, connect to home network
- [ ] T028 [US2] Test Display: check resolution, brightness controls
- [ ] T029 [US2] Test Audio: speakers, headphone jack
- [ ] T030 [US2] Test Touchpad: two-finger scroll, tap-to-click
- [ ] T031 [US2] Test Keyboard: all keys, Fn function keys
- [ ] T032 [US2] Test USB: plug in external device, verify mounts
- [ ] T033 [US2] Test Webcam: open Cheese app, verify video
- [ ] T034 [US2] Test Bluetooth: check if devices discoverable
- [ ] T035 [US2] Document results and make go/no-go decision

#### Documentation Tasks

- [ ] T036 [P] [US2] Write guide section: Boot from USB in `guides/windows-to-ubuntu-migration.md`
- [ ] T037 [P] [US2] Write guide section: Hardware Test Procedures in `guides/windows-to-ubuntu-migration.md`
- [ ] T038 [P] [US2] Create hardware test checklist in `checklists/hardware-test.md`
- [ ] T039 [P] [US2] Write guide section: Go/No-Go Decision Criteria in `guides/windows-to-ubuntu-migration.md`

---

## Epic 4: Ubuntu Installation (Phase 3)

**Epic Key**: ANI-E4
**Priority**: High
**Blocked By**: Epic 3 (hardware must pass first)
**Description**: Configure BIOS, install Ubuntu, verify successful boot

### Story: US5 - Install Ubuntu (Wipe Windows)

**Story Key**: ANI-S5
**Points**: 3
**Acceptance**: Ubuntu installed, boots successfully, desktop functional

#### Tasks

- [ ] T040 [US5] Access Dell BIOS (F2 at logo)
- [ ] T041 [US5] Disable Secure Boot in BIOS
- [ ] T042 [US5] Verify boot mode is UEFI (not Legacy)
- [ ] T043 [US5] Boot from Ubuntu USB and select "Install Ubuntu"
- [ ] T044 [US5] Follow installation wizard (language, keyboard, timezone)
- [ ] T045 [US5] Select "Erase disk and install Ubuntu" option
- [ ] T046 [US5] Create user account and password
- [ ] T047 [US5] Wait for installation to complete
- [ ] T048 [US5] Remove USB when prompted and restart
- [ ] T049 [US5] Verify Ubuntu boots successfully to desktop

#### Documentation Tasks

- [ ] T050 [P] [US5] Write guide section: Dell BIOS Configuration in `guides/windows-to-ubuntu-migration.md`
- [ ] T051 [P] [US5] Write guide section: Ubuntu Installation Wizard in `guides/windows-to-ubuntu-migration.md`
- [ ] T052 [P] [US5] Add BIOS screenshot/diagram to `guides/images/`
- [ ] T053 [P] [US5] Write guide section: First Boot Verification in `guides/windows-to-ubuntu-migration.md`

---

## Epic 5: Post-Installation Setup (Phase 4)

**Epic Key**: ANI-E5
**Priority**: Medium
**Blocked By**: Epic 4
**Description**: Update system, install Node.js, restore credentials, ready for Moltbot

### Story: US6 - Post-Install Setup

**Story Key**: ANI-S6
**Points**: 2
**Acceptance**: Ubuntu updated, Node.js 22+ installed, WiFi connected, SSH keys restored

#### Tasks

- [ ] T054 [US6] Connect to WiFi using saved credentials
- [ ] T055 [US6] Run system updates: `sudo apt update && sudo apt upgrade -y`
- [ ] T056 [US6] Install Node.js 22+ via NodeSource repository
- [ ] T057 [US6] Verify Node.js: `node --version` shows v22.x.x
- [ ] T058 [US6] Restore SSH keys to ~/.ssh with correct permissions (700/600)
- [ ] T059 [US6] Import browser passwords to password manager
- [ ] T060 [US6] Verify system ready for Moltbot installation

#### Documentation Tasks

- [ ] T061 [P] [US6] Write guide section: System Updates in `guides/windows-to-ubuntu-migration.md`
- [ ] T062 [P] [US6] Write guide section: Install Node.js 22 in `guides/windows-to-ubuntu-migration.md`
- [ ] T063 [P] [US6] Write guide section: Restore Credentials in `guides/windows-to-ubuntu-migration.md`
- [ ] T064 [P] [US6] Create post-install checklist in `checklists/post-install.md`

---

## Epic 6: Troubleshooting & Polish (Phase 5)

**Epic Key**: ANI-E6
**Priority**: Low
**Description**: Document common issues and complete guide polish

### Story: US-POLISH - Troubleshooting Documentation

**Story Key**: ANI-S-POLISH
**Points**: 2
**Acceptance**: All edge cases documented with solutions

#### Tasks

- [ ] T065 [P] Write troubleshooting: WiFi not working in `guides/windows-to-ubuntu-migration.md`
- [ ] T066 [P] Write troubleshooting: USB not booting in `guides/windows-to-ubuntu-migration.md`
- [ ] T067 [P] Write troubleshooting: Installation fails midway in `guides/windows-to-ubuntu-migration.md`
- [ ] T068 [P] Write troubleshooting: Ubuntu won't boot after install in `guides/windows-to-ubuntu-migration.md`
- [ ] T069 Write guide section: Overview and Requirements in `guides/windows-to-ubuntu-migration.md`
- [ ] T070 Write guide section: Appendix - Commands Reference in `guides/windows-to-ubuntu-migration.md`
- [ ] T071 Review entire guide for completeness and accuracy
- [ ] T072 Add version/date stamp to guide header

---

## Dependency Graph

```
Epic 1: Create USB (Phase 0)
    └── US0: Create Bootable USB
         ↓
Epic 2: Windows Prep (Phase 1) ──────────────────┐
    ├── US1: Preserve Windows License            │
    └── US4: Backup Critical Data                │
         ↓                                       │
Epic 3: Hardware Testing (Phase 2) ←─────────────┘
    └── US2: Test Hardware on Live USB
         ↓
         [GO/NO-GO DECISION POINT]
         ↓
Epic 4: Installation (Phase 3)
    └── US5: Install Ubuntu
         ↓
Epic 5: Post-Install (Phase 4)
    └── US6: Post-Install Setup
         ↓
Epic 6: Polish (Phase 5)
    └── Troubleshooting & Final Review
```

---

## Parallel Execution Opportunities

Tasks marked `[P]` can run in parallel within their phase:

| Phase | Parallel Tasks | Notes |
|-------|----------------|-------|
| Phase 0 | T006-T009 | Documentation can parallel with actual USB creation |
| Phase 1 | T013-T014, T022-T025 | All doc tasks parallel |
| Phase 2 | T036-T039 | Doc tasks after hardware tests complete |
| Phase 3 | T050-T053 | Doc tasks after installation complete |
| Phase 4 | T061-T064 | Doc tasks parallel |
| Phase 5 | T065-T068 | All troubleshooting sections parallel |

---

## Jira Import Summary

| Type | Count | Keys |
|------|-------|------|
| Epics | 6 | ANI-E1 through ANI-E6 |
| Stories | 7 | ANI-S0, ANI-S1, ANI-S2, ANI-S4, ANI-S5, ANI-S6, ANI-S-POLISH |
| Tasks | 72 | T001 through T072 |

**Story Points Total**: 15

---

## MVP Scope

**Minimum Viable Product**: Complete Epics 1-5 (Phases 0-4)

This delivers:
- Working bootable USB
- Windows license preserved
- All data backed up
- Hardware verified compatible
- Ubuntu installed and running
- Node.js ready for Moltbot

Epic 6 (Troubleshooting) can be added incrementally as issues are encountered.

---

## Suggested Execution Order

1. **Start**: T001-T005 (Create USB while planning)
2. **While USB downloads**: T010-T012 (Extract Windows key), T015-T021 (Backup data)
3. **After USB ready**: T026-T035 (Hardware testing)
4. **If GO decision**: T040-T049 (Install Ubuntu)
5. **After install**: T054-T060 (Post-install setup)
6. **Throughout**: Documentation tasks (can parallel)
7. **Last**: T069-T072 (Polish and review)
