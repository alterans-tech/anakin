# Implementation Plan: Windows to Ubuntu Migration Guide

**Feature**: `00-foundation`
**Created**: 2026-02-02
**Spec**: [spec.md](./spec.md)

---

## Constitution Check

| Principle | Alignment | Notes |
|-----------|-----------|-------|
| I. Security-First | ✅ | Not applicable to OS migration (pre-OpenClaw) |
| II. Test-Before-Destroy | ✅ | Core focus: hardware testing before wipe |
| III. Cost-Aware | ✅ | Not applicable (no API usage) |
| IV. Documentation-Driven | ✅ | Step-by-step guide with exact commands |
| V. Local-First Privacy | ✅ | All backups to user-controlled storage |
| VI. Idempotent Automation | N/A | Manual guide, no scripts in this phase |
| VII. Graceful Degradation | ✅ | Edge cases with fallback options |

**Gate Status**: PASS - All applicable principles satisfied.

---

## Technical Context

| Item | Value | Status |
|------|-------|--------|
| Target OS | Ubuntu 24.04 LTS | Confirmed |
| Source OS | Windows 10/11 | Confirmed |
| Hardware | Dell laptop (2018+) | Confirmed |
| USB Tool | Rufus (Windows) | Confirmed |
| Boot Key | F12 (Dell boot menu) | Confirmed |
| BIOS Key | F2 (Dell BIOS setup) | Confirmed |

**No NEEDS CLARIFICATION items** - All technical details resolved from spec and Dell documentation.

---

## Research Findings

### Dell OEM Windows Licensing

**Decision**: Document key extraction but emphasize BIOS-embedded activation

**Rationale**: Dell OEM licenses are stored in UEFI firmware. Windows will auto-activate on same hardware even without explicit key entry. However, documenting the key provides:
1. Peace of mind for users
2. Support scenarios where key may be requested
3. Proof of license if hardware changes

**Key Extraction Methods**:
```powershell
# Method 1: PowerShell (recommended)
(Get-WmiObject -query 'select * from SoftwareLicensingService').OA3xOriginalProductKey

# Method 2: Command Prompt
wmic path softwarelicensingservice get OA3xOriginalProductKey
```

**Dell Service Tag**: Located on bottom of laptop or via `wmic bios get serialnumber`

---

### Ubuntu 24.04 LTS Compatibility

**Decision**: Target Ubuntu 24.04.1 LTS (latest point release)

**Rationale**:
- LTS = 5 years support (until April 2029)
- Point release includes hardware enablement stack
- Better driver support for newer Dell hardware

**Download**: https://ubuntu.com/download/desktop

**Checksum Verification**:
```powershell
# Windows PowerShell
Get-FileHash ubuntu-24.04.1-desktop-amd64.iso -Algorithm SHA256
```

---

### Bootable USB Creation

**Decision**: Recommend Rufus (primary), Balena Etcher (alternative)

**Rationale**:
- Rufus: Most reliable for UEFI boot, handles Secure Boot
- Balena Etcher: Simpler UI, cross-platform

**Rufus Settings**:
| Setting | Value |
|---------|-------|
| Partition scheme | GPT |
| Target system | UEFI (non-CSM) |
| File system | FAT32 (Large) |
| Cluster size | Default |

---

### Dell BIOS Configuration

**Decision**: Document both Secure Boot disable and UEFI boot

**Required BIOS Changes**:
1. **Secure Boot**: Disable (Settings → Secure Boot → Secure Boot Enable → Disabled)
2. **Boot Mode**: UEFI (not Legacy)
3. **Boot Sequence**: Add USB to boot order or use F12 one-time boot

**Access Keys**:
- F2 at Dell logo = BIOS Setup
- F12 at Dell logo = One-time boot menu

---

### Hardware Testing Checklist

**Decision**: Prioritize critical components with clear pass/fail criteria

| Component | Test Method | Pass Criteria | Fail Action |
|-----------|-------------|---------------|-------------|
| WiFi | Settings → WiFi → Connect | Connects to network | Try ethernet, USB adapter, or abort |
| Display | Settings → Displays | Correct resolution, brightness slider works | Usually works; check proprietary drivers |
| Audio | Settings → Sound → Test | Sound from speakers | Check PulseAudio settings |
| Touchpad | Use gestures | Two-finger scroll, tap-to-click | Usually works; check Synaptics |
| Keyboard | Type, test Fn keys | All keys register, brightness/volume Fn keys | Check function key mode in BIOS |
| USB | Plug in device | Device mounts | Usually works |
| Webcam | Cheese app | Video appears | Check if proprietary driver needed |
| Bluetooth | Settings → Bluetooth | Devices discoverable | May need firmware |

**Go/No-Go Criteria**:
- WiFi: MUST work (critical for updates, OpenClaw)
- Display: MUST work at usable resolution
- Audio: SHOULD work (not blocking)
- Input: MUST work (keyboard/touchpad)
- Others: Nice to have

---

### Browser Password Export

**Decision**: Cover Chrome, Firefox, Edge (most common)

**Chrome/Edge** (Chromium-based):
1. Settings → Passwords → three-dot menu → Export passwords
2. Confirm with Windows password
3. Save CSV to external drive

**Firefox**:
1. Settings → Privacy & Security → Logins and Passwords → three-dot menu → Export Logins
2. Confirm with Windows password
3. Save CSV to external drive

**Security Note**: Delete CSV after importing to new system password manager

---

### WiFi Password Recovery

**Decision**: Provide both GUI and command-line methods

**GUI Method**:
1. Control Panel → Network and Sharing Center
2. Click WiFi network name → Wireless Properties → Security tab
3. Check "Show characters"

**Command Line** (all networks):
```cmd
netsh wlan show profiles
netsh wlan show profile name="NetworkName" key=clear
```

---

### Post-Install Node.js 22

**Decision**: Use NodeSource repository for latest LTS

**Commands**:
```bash
# Update system first
sudo apt update && sudo apt upgrade -y

# Install Node.js 22.x via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Verify
node --version  # Should show v22.x.x
npm --version
```

---

## Guide Structure

The implementation will produce a single comprehensive guide with these sections:

1. **Overview** - What we're doing, time estimate, requirements
2. **Phase 0: Create Bootable USB** - Download Ubuntu, create USB (DO THIS FIRST)
3. **Phase 1: Preparation (Windows)** - License key, backups
4. **Phase 2: Hardware Testing (Live USB)** - Boot, test checklist, go/no-go
5. **Phase 3: Installation** - BIOS setup, installation wizard, first boot
6. **Phase 4: Post-Install** - Updates, Node.js, restore credentials
7. **Troubleshooting** - Common issues and fixes
8. **Appendix** - Commands reference, Dell-specific notes

**Execution Order Note**: Phase 0 (USB creation) should be done FIRST because:
- USB download takes time (~5GB) - start early
- Can run hardware tests while doing Windows prep
- Gives early confidence that boot media works

---

## Artifacts to Generate

| Artifact | Location | Purpose |
|----------|----------|---------|
| Migration Guide | `guides/windows-to-ubuntu-migration.md` | Main step-by-step guide |
| Pre-Migration Checklist | `checklists/pre-migration.md` | Printable backup checklist |
| Hardware Test Checklist | `checklists/hardware-test.md` | Printable test checklist |
| Post-Install Checklist | `checklists/post-install.md` | Verification checklist |

---

## Next Steps

Run `/speckit.tasks` to generate Jira-ready work items (Epics, Stories, Tasks) for implementing these artifacts.
