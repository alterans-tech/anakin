# Feature Specification: Windows to Ubuntu Migration Guide

**Feature Branch**: `00-foundation`
**Created**: 2026-02-02
**Status**: Draft
**Input**: Step-by-step instructions to wipe Windows on Dell laptop, install Ubuntu, verify hardware compatibility before wiping, and preserve Windows license key for potential recovery

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Preserve Windows License Key (Priority: P1)

A Dell laptop owner wants to save their Windows license key before wiping the system, in case they ever need to reinstall Windows or for warranty/support purposes.

**Why this priority**: Once Windows is wiped, the license key may be difficult to recover. Dell OEM licenses are embedded in BIOS/UEFI firmware, but documenting them provides peace of mind and may be needed for support scenarios.

**Independent Test**: User retrieves and documents their Windows product key using provided methods, and can verify the key is valid before proceeding.

**Acceptance Scenarios**:

1. **Given** a Dell laptop running Windows, **When** user runs the license key extraction command, **Then** the Windows product key is displayed and can be saved
2. **Given** a Dell OEM Windows installation, **When** user checks BIOS-embedded key, **Then** they understand that Dell licenses are tied to hardware and auto-activate on reinstall
3. **Given** the extracted license key, **When** user saves it to external storage, **Then** key is documented with laptop service tag for future reference

---

### User Story 2 - Test Hardware on Ubuntu Live USB (Priority: P1)

A Dell laptop owner wants to verify that all critical hardware (WiFi, display, audio, touchpad, keyboard) works with Ubuntu BEFORE wiping Windows, to avoid being stuck with a non-functional system.

**Why this priority**: This is the safety net. If hardware doesn't work, user can abort and keep Windows. Testing first prevents catastrophic data loss scenarios.

**Independent Test**: User boots into Ubuntu live USB, runs through hardware verification checklist, and receives clear pass/fail results for each component.

**Acceptance Scenarios**:

1. **Given** a bootable Ubuntu live USB, **When** user boots the Dell laptop from USB, **Then** Ubuntu live environment loads successfully
2. **Given** Ubuntu live environment running, **When** user tests WiFi, **Then** they can scan for and connect to their home network
3. **Given** Ubuntu live environment running, **When** user tests display, **Then** resolution is correct and brightness controls work
4. **Given** Ubuntu live environment running, **When** user tests audio, **Then** speakers and headphone jack produce sound
5. **Given** Ubuntu live environment running, **When** user tests touchpad and keyboard, **Then** all gestures and function keys work
6. **Given** any hardware failing, **When** user reviews results, **Then** they receive guidance on whether to proceed, troubleshoot, or abort

---

### User Story 3 - Create Bootable Ubuntu USB (Priority: P1)

A Dell laptop owner needs to create a bootable Ubuntu USB drive from their Windows system to use for live testing and installation.

**Why this priority**: Required before any testing or installation can happen. This is the first physical step in the migration process.

**Independent Test**: User downloads Ubuntu ISO, creates bootable USB, and can successfully boot from it on their Dell laptop.

**Acceptance Scenarios**:

1. **Given** Windows with internet access, **When** user downloads Ubuntu 24.04 LTS ISO, **Then** the correct ISO file is obtained from official source
2. **Given** Ubuntu ISO and blank USB drive (8GB+), **When** user runs USB creation tool, **Then** bootable USB is created successfully
3. **Given** bootable USB, **When** user restarts Dell laptop and presses F12, **Then** USB appears in boot menu
4. **Given** USB selected in boot menu, **When** laptop boots, **Then** Ubuntu live environment loads

---

### User Story 4 - Backup Critical Data Before Wipe (Priority: P1)

A Dell laptop owner wants to ensure all critical data and credentials are backed up to external storage before wiping Windows.

**Why this priority**: Data loss is irreversible. This must happen before any destructive action.

**Independent Test**: User completes backup checklist, verifies backups are readable on external storage, and confirms nothing critical remains only on the laptop.

**Acceptance Scenarios**:

1. **Given** important files on Windows, **When** user copies to external drive, **Then** files are verified readable on the external drive
2. **Given** browser with saved passwords, **When** user exports passwords, **Then** CSV file is saved to external storage
3. **Given** saved WiFi networks, **When** user documents passwords, **Then** WiFi credentials are recorded for re-entry on Ubuntu
4. **Given** SSH keys or API keys, **When** user backs them up, **Then** keys are copied to external storage
5. **Given** completed backup, **When** user reviews checklist, **Then** all critical items are confirmed backed up

---

### User Story 5 - Install Ubuntu (Wipe Windows) (Priority: P2)

A Dell laptop owner, having verified hardware compatibility and completed backups, wants to wipe Windows and install Ubuntu as the sole operating system.

**Why this priority**: P2 because it depends on P1 stories being completed first. This is the point of no return.

**Independent Test**: User boots from USB, follows installation wizard, wipes Windows, and has a working Ubuntu installation that boots successfully.

**Acceptance Scenarios**:

1. **Given** hardware tests passed and backups complete, **When** user boots from Ubuntu USB, **Then** installation wizard starts
2. **Given** installation wizard, **When** user selects "Erase disk and install Ubuntu", **Then** they understand this will delete all Windows data
3. **Given** installation in progress, **When** partitioning completes, **Then** Ubuntu files are copied to disk
4. **Given** installation complete, **When** user removes USB and restarts, **Then** Ubuntu boots successfully
5. **Given** fresh Ubuntu installation, **When** user logs in, **Then** desktop environment is functional

---

### User Story 6 - Post-Install Setup (Priority: P2)

A Dell laptop owner with fresh Ubuntu installation wants to complete essential post-installation tasks to have a fully functional system ready for Moltbot.

**Why this priority**: Required to prepare the system for Moltbot, but not blocking the core installation.

**Independent Test**: User completes post-install checklist and has a fully updated Ubuntu system with Node.js 22+ installed.

**Acceptance Scenarios**:

1. **Given** fresh Ubuntu installation, **When** user runs system updates, **Then** all packages are updated to latest versions
2. **Given** updated Ubuntu, **When** user installs Node.js 22+, **Then** `node --version` shows v22.x.x
3. **Given** WiFi credentials from backup, **When** user connects to WiFi, **Then** internet access is restored
4. **Given** backed up SSH keys, **When** user restores them, **Then** SSH authentication works as before

---

### Edge Cases

- What happens if WiFi doesn't work in Ubuntu live environment?
  - Try ethernet cable if available, or USB WiFi adapter
  - Check if proprietary drivers are needed (common for Broadcom)
  - If no workaround, consider dual-boot or abort migration
- What happens if Dell BIOS doesn't show USB boot option?
  - Disable Secure Boot in BIOS settings
  - Enable Legacy Boot / CSM if needed
  - Ensure USB is properly formatted as bootable
- What happens if Windows license key extraction fails?
  - Dell OEM keys are embedded in UEFI firmware
  - Windows will auto-activate on same hardware without key
  - Document Dell Service Tag as alternative recovery path
- What happens if installation fails midway?
  - Boot from USB again and retry installation
  - If disk errors, run disk check from live environment
- What happens if Ubuntu won't boot after installation?
  - Boot from USB, use "Try Ubuntu" to access installed system
  - Check GRUB bootloader installation
  - May need to repair bootloader

---

## Requirements *(mandatory)*

### Functional Requirements

**Windows License Preservation**

- **FR-001**: Guide MUST explain how to extract Windows product key using built-in commands
- **FR-002**: Guide MUST explain Dell OEM licensing (keys embedded in BIOS, auto-activate on same hardware)
- **FR-003**: Guide MUST recommend saving license key with Dell Service Tag to external storage

**Bootable USB Creation**

- **FR-004**: Guide MUST provide official Ubuntu 24.04 LTS download link
- **FR-005**: Guide MUST explain how to verify ISO integrity (checksum)
- **FR-006**: Guide MUST provide step-by-step instructions for creating bootable USB on Windows
- **FR-007**: Guide MUST explain how to access Dell boot menu (F12 at startup)

**Hardware Testing**

- **FR-008**: Guide MUST provide checklist of hardware components to test in live environment
- **FR-009**: Guide MUST explain how to test WiFi connectivity
- **FR-010**: Guide MUST explain how to test display (resolution, brightness)
- **FR-011**: Guide MUST explain how to test audio (speakers, headphones)
- **FR-012**: Guide MUST explain how to test touchpad and keyboard function keys
- **FR-013**: Guide MUST provide clear go/no-go criteria based on test results

**Data Backup**

- **FR-014**: Guide MUST provide pre-migration backup checklist
- **FR-015**: Guide MUST explain how to export browser passwords
- **FR-016**: Guide MUST explain how to find/document WiFi passwords
- **FR-017**: Guide MUST explain how to backup SSH keys and important files
- **FR-018**: Guide MUST emphasize verifying backups before proceeding

**Ubuntu Installation**

- **FR-019**: Guide MUST explain BIOS settings needed for Ubuntu (Secure Boot, boot order)
- **FR-020**: Guide MUST provide step-by-step installation wizard walkthrough
- **FR-021**: Guide MUST clearly explain "Erase disk" option consequences
- **FR-022**: Guide MUST explain disk partitioning options (default recommended for beginners)
- **FR-023**: Guide MUST explain what to do when prompted to remove USB and restart

**Post-Installation**

- **FR-024**: Guide MUST provide commands for system update
- **FR-025**: Guide MUST provide commands for installing Node.js 22+
- **FR-026**: Guide MUST explain how to restore WiFi connection
- **FR-027**: Guide MUST explain how to restore SSH keys
- **FR-028**: Guide MUST confirm system is ready for Moltbot installation

---

### Key Entities

- **Windows License**: Product key, Dell Service Tag, OEM activation status
- **Bootable USB**: Ubuntu ISO version, USB creation tool used, boot verification status
- **Hardware Test Results**: Component name, test method, pass/fail status, notes
- **Backup Checklist**: Item category, backup location, verification status
- **Ubuntu Installation**: Version, partition scheme, installation outcome

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User can retrieve and document Windows license key before any destructive action
- **SC-002**: User can create bootable Ubuntu USB and successfully boot from it on first attempt
- **SC-003**: All critical hardware (WiFi, display, audio, input devices) is tested before Windows is wiped
- **SC-004**: Zero data loss - all critical files and credentials are backed up and verified readable
- **SC-005**: User completes full migration from Windows to Ubuntu in under 2 hours (excluding download times)
- **SC-006**: Ubuntu boots successfully after installation with no manual bootloader repair needed
- **SC-007**: System is ready for Moltbot with Node.js 22+ installed and verified

---

## Assumptions

1. **Dell Laptop Model**: 2018 or newer Dell laptop with Intel/AMD processor (no ARM/Qualcomm)
2. **Current OS**: Windows 10 or Windows 11 with valid license
3. **USB Drive**: User has access to USB drive 8GB or larger
4. **External Storage**: User has external storage for backups (USB drive, external HDD, or cloud)
5. **Internet**: Reliable internet for downloading Ubuntu ISO (~5GB)
6. **BIOS Access**: User can access Dell BIOS with F2 and boot menu with F12
7. **Target Ubuntu**: Ubuntu 24.04 LTS (current LTS release)

---

## Dependencies

1. **Ubuntu ISO**: Official Ubuntu 24.04 LTS ISO must be available from ubuntu.com
2. **USB Creation Tool**: Rufus or Balena Etcher available for Windows
3. **Dell BIOS**: Standard Dell BIOS/UEFI with accessible boot menu
4. **Hardware Drivers**: Ubuntu kernel must include drivers for Dell laptop hardware (or drivers available via Additional Drivers)

---

## Out of Scope

- Dual-boot setup (keeping Windows alongside Ubuntu)
- Data recovery after wipe
- Troubleshooting exotic hardware failures
- Moltbot installation (separate guide)
- Windows reinstallation procedures
- Corporate/enterprise Dell deployments with BitLocker or domain policies
