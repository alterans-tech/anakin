# Detailed Linux Installation Guide for Developers New to OS Installation

This guide assumes technical background but zero experience with OS installation, dual boot, or BIOS configuration.

---

## Table of Contents

1. [SD Card vs USB - Which to Use?](#1-sd-card-vs-usb---which-to-use)
2. [Creating Bootable Media - Detailed Steps](#2-creating-bootable-media---detailed-steps)
3. [Booting Live Environment - Testing Hardware](#3-booting-live-environment---testing-hardware)
4. [Dual Boot vs Clean Install - What's Best?](#4-dual-boot-vs-clean-install---whats-best)
5. [The Recommended Path](#5-the-recommended-path)

---

## 1. SD Card vs USB - Which to Use?

### Short Answer: Use USB

**SD Card Problems on Dell:**
- Most Dell consumer laptops (Inspiron, XPS) do NOT support booting from internal SD card reader
- Even models with "SD Card Boot" option in BIOS often don't work reliably
- The internal SD reader is detected AFTER the OS loads drivers, so BIOS can't see it at boot time

**Workaround if you only have SD card:**
- Buy a USB SD card reader ($5-10)
- Insert SD card into the USB reader
- Plug USB reader into laptop
- This WILL work because BIOS sees it as a USB device

**Recommended: Just use a USB flash drive**
- 8GB minimum, 16GB recommended
- Any brand works (SanDisk, Kingston, Samsung, generic)
- USB 3.0 is faster but USB 2.0 works fine
- The drive will be COMPLETELY ERASED

---

## 2. Creating Bootable Media - Detailed Steps

### Step 2.1: Download Ubuntu ISO

1. Open browser, go to: https://ubuntu.com/download/desktop
2. Click "Download Ubuntu Desktop"
3. Select "Ubuntu 24.04 LTS" (LTS = Long Term Support = 5 years of updates)
4. Click the download button
5. File will be ~5GB, named something like `ubuntu-24.04.1-desktop-amd64.iso`
6. Save to your Downloads folder
7. **DO NOT extract it** - leave it as .iso file

### Step 2.2: Download Rufus

1. Go to: https://rufus.ie/
2. Scroll down to "Download"
3. Click "Rufus 4.x" (the standard version, not portable)
4. Download completes instantly (~1MB)
5. **No installation needed** - it's a portable app

### Step 2.3: Prepare USB Drive

1. Insert USB drive into your Windows laptop
2. **IMPORTANT**: Copy any files you want to keep OFF the drive
3. The entire drive will be erased
4. Note which drive letter Windows assigns (e.g., E:, F:, G:)

### Step 2.4: Run Rufus - Exact Clicks

1. Double-click `rufus-4.x.exe` in your Downloads
2. If Windows asks "Allow this app to make changes?" → Click **Yes**
3. Rufus window opens

**Configure these settings (top to bottom):**

```
┌─────────────────────────────────────────────────────────┐
│ Device                                                  │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ [Your USB drive - e.g., "SanDisk (E:) 16GB"]     ▼│ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ Boot selection                                          │
│ ┌───────────────────────────────────┐ ┌───────────────┐ │
│ │ Disk or ISO image (please select) │ │   SELECT    │ │
│ └───────────────────────────────────┘ └───────────────┘ │
│                                                         │
│ Partition scheme        Target system                   │
│ ┌─────────────────┐     ┌─────────────────────────────┐ │
│ │ GPT          ▼│     │ UEFI (non CSM)            ▼│ │
│ └─────────────────┘     └─────────────────────────────┘ │
│                                                         │
│ Volume label                                            │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ Ubuntu 24.04                                        │ │
│ └─────────────────────────────────────────────────────┘ │
│                                                         │
│ File system             Cluster size                    │
│ ┌─────────────────┐     ┌─────────────────────────────┐ │
│ │ FAT32        ▼│     │ Default                   ▼│ │
│ └─────────────────┘     └─────────────────────────────┘ │
│                                                         │
│                                    ┌─────────────────┐  │
│                                    │      START      │  │
│                                    └─────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

**Detailed steps:**

4. **Device dropdown**: Make sure it shows YOUR USB drive
   - If wrong drive selected, click dropdown and choose correct one
   - **TRIPLE CHECK THIS** - wrong selection = wrong drive erased

5. Click **SELECT** button (right side of Boot selection)
   - Navigate to Downloads folder
   - Select `ubuntu-24.04.1-desktop-amd64.iso`
   - Click Open

6. **Partition scheme**: Select **GPT**
   - 2018 Dell laptops use UEFI, which needs GPT
   - If your laptop is ancient and doesn't support UEFI, use MBR

7. **Target system**: Should auto-change to **UEFI (non CSM)**
   - Leave it as-is

8. **Volume label**: Auto-fills to "Ubuntu 24.04"
   - You can leave this or change it

9. **File system**: **FAT32** (default, leave it)

10. **Cluster size**: **Default** (leave it)

11. Click **START**

### Step 2.5: Handle Prompts

**Prompt 1: ISOHybrid Image Detected**
```
┌──────────────────────────────────────────────────────────────┐
│ ISOHybrid image detected                                     │
│                                                              │
│ This image can be written in two modes:                      │
│                                                              │
│ ○ Write in ISO Image mode (Recommended)                      │
│ ○ Write in DD Image mode                                     │
│                                                              │
│                              [OK]  [Cancel]                  │
└──────────────────────────────────────────────────────────────┘
```
→ Keep "ISO Image mode" selected → Click **OK**

**Prompt 2: Download Required**
```
┌──────────────────────────────────────────────────────────────┐
│ Syslinux version mismatch                                    │
│                                                              │
│ Rufus needs to download additional files. Download now?      │
│                                                              │
│                              [Yes]  [No]                     │
└──────────────────────────────────────────────────────────────┘
```
→ Click **Yes** (small download, takes seconds)

**Prompt 3: Warning - Data Destruction**
```
┌──────────────────────────────────────────────────────────────┐
│ WARNING: ALL DATA ON DEVICE 'SANDISK (E:)' WILL BE DESTROYED │
│                                                              │
│ To continue, click OK. To quit, click CANCEL.                │
│                                                              │
│                              [OK]  [Cancel]                  │
└──────────────────────────────────────────────────────────────┘
```
→ Verify correct drive one more time → Click **OK**

### Step 2.6: Wait for Completion

- Progress bar fills up (takes 5-15 minutes depending on USB speed)
- Status shows various stages: "Copying ISO files...", "Creating file system..."
- When done: Status bar turns **GREEN** and says **READY**
- Click **CLOSE**

**Your bootable USB is ready!** Do NOT remove it yet if you're about to test.

---

## 3. Booting Live Environment - Testing Hardware

### What is "Live Environment"?

Ubuntu can run entirely from the USB drive without installing anything. This lets you:
- Test if all your hardware works (WiFi, display, audio, etc.)
- Browse the internet, use apps
- Nothing is saved - reboot and it's gone
- Zero risk to Windows

### Step 3.1: Access Boot Menu on Dell

1. **Save all work in Windows and shut down** (not restart)
2. Insert your bootable USB
3. Press **power button** to turn on
4. **Immediately start tapping F12** repeatedly (like a woodpecker)
   - F12 = One-time boot menu on most Dell laptops
   - Alternative: Some Dells use F2 for BIOS, then navigate to boot
5. You should see a screen like:

```
┌──────────────────────────────────────────────────────────────┐
│                     BOOT MENU                                │
│                                                              │
│   > Windows Boot Manager                                     │
│   > UEFI: SanDisk Ultra USB 3.0                             │
│   > UEFI: SAMSUNG MZNLN256 (your hard drive)                │
│                                                              │
│   Use ↑↓ to select, Enter to boot                           │
└──────────────────────────────────────────────────────────────┘
```

6. Use arrow keys to select **UEFI: [Your USB drive name]**
7. Press **Enter**

### Step 3.2: If F12 Doesn't Work

**Try these alternatives:**

| Key | Purpose |
|-----|---------|
| F2 | Enter BIOS Setup (then navigate to Boot) |
| F12 | One-time boot menu |
| Esc | Some Dell models use this |
| Del | Alternative BIOS entry |

**If USB doesn't appear in boot menu:**

1. Enter BIOS (F2)
2. Navigate to: **Boot** or **Boot Sequence**
3. Look for: **Secure Boot** → Set to **Disabled**
4. Look for: **UEFI Boot** → Set to **Enabled**
5. Save (F10) and Exit
6. Try F12 again on reboot

### Step 3.3: GRUB Menu (First Ubuntu Screen)

After selecting USB, you'll see:

```
┌──────────────────────────────────────────────────────────────┐
│                         GNU GRUB                             │
│                                                              │
│   *Try or Install Ubuntu                                     │
│    Ubuntu (safe graphics)                                    │
│    OEM install (for manufacturers)                           │
│    Boot from next volume                                     │
│    UEFI Firmware Settings                                    │
│                                                              │
│   Use ↑↓ to select, Enter to boot                           │
└──────────────────────────────────────────────────────────────┘
```

→ Select **Try or Install Ubuntu**
→ Press **Enter**
→ Wait 1-2 minutes for Ubuntu to load

### Step 3.4: Ubuntu Welcome Screen

You'll see:

```
┌──────────────────────────────────────────────────────────────┐
│                     Welcome to Ubuntu                        │
│                                                              │
│  What would you like to do?                                  │
│                                                              │
│  ┌────────────────────┐  ┌────────────────────┐             │
│  │                    │  │                    │             │
│  │   Try Ubuntu       │  │   Install Ubuntu   │             │
│  │                    │  │                    │             │
│  └────────────────────┘  └────────────────────┘             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

→ Click **Try Ubuntu** (NOT Install yet!)

### Step 3.5: Test Your Hardware

You're now in Ubuntu live environment. Run through this checklist:

#### WiFi Test
1. Click the **network icon** in top-right corner (looks like signal bars or a down arrow)
2. Click your WiFi network name
3. Enter password
4. If connects → **WiFi works**
5. Open Firefox (in dock) and browse to google.com to confirm

**If WiFi doesn't appear:**
- Open Terminal (right-click desktop → "Open Terminal")
- Run: `lspci | grep -i wireless`
- Note the chipset name (e.g., "Intel Wireless 8265" or "Broadcom BCM43142")
- Search "[chipset name] Ubuntu" to find if there's a known fix

#### Display Test
- Does the screen look correct? Not stretched/squished?
- Try brightness keys (usually Fn + F11/F12 or sun icons)
- Check Settings → Displays for resolution options

#### Audio Test
1. Open Firefox
2. Go to YouTube
3. Play any video
4. Can you hear sound?
5. Try volume keys (usually Fn + F1/F2/F3 or speaker icons)

#### Touchpad Test
- Move cursor around
- Single click (tap or click)
- Right-click (two-finger tap or bottom-right click)
- Scroll (two-finger scroll up/down)
- If touchpad feels weird, check Settings → Mouse & Touchpad

#### Keyboard Test
1. Open Text Editor (search in Activities)
2. Type: `The quick brown fox jumps over the lazy dog 1234567890`
3. Test special characters: `@#$%^&*()_+-=[]{}|;':",./<>?`
4. Test function keys (F1-F12)
5. Test Fn combinations (brightness, volume, etc.)

#### USB Ports Test
- Plug another USB device (mouse, flash drive) into each port
- Verify it's detected

#### Webcam Test
1. Search for "Cheese" in Activities
2. Open it - should show your camera feed
3. If no camera detected, run in Terminal: `lsusb | grep -i cam`

#### Bluetooth Test
1. Click Settings (gear icon)
2. Click Bluetooth
3. Toggle ON
4. See if it scans for devices

### Step 3.6: Document Results

| Component | Status | Notes |
|-----------|--------|-------|
| WiFi | ✅/❌ | |
| Display | ✅/❌ | |
| Audio | ✅/❌ | |
| Touchpad | ✅/❌ | |
| Keyboard | ✅/❌ | |
| USB Ports | ✅/❌ | |
| Webcam | ✅/❌ | |
| Bluetooth | ✅/❌ | |

**If everything works → You're ready to install!**
**If something doesn't work → Search for solution before proceeding**

---

## 4. Dual Boot vs Clean Install - What's Best?

### Option A: Dual Boot First, Then Remove Windows Later

**How it works:**
- Shrink Windows partition
- Install Ubuntu alongside Windows
- On boot, choose which OS to load
- Later, delete Windows partition and expand Ubuntu

**Pros:**
- Safety net if you need Windows for something
- Can gradually migrate over weeks/months
- If hardware issue discovered later, still have Windows

**Cons:**
- More complex partition setup
- Disk space split between two OSes
- Need to maintain two systems (updates, etc.)
- Removing Windows later requires:
  - Booting from live USB
  - Using GParted to delete Windows partition
  - Expanding Ubuntu partition
  - Fixing GRUB bootloader
  - Cleaning up EFI partition

**Removing Windows later (summary of steps):**
1. Boot from Ubuntu live USB
2. Open GParted (disk partition tool)
3. Delete Windows partitions (usually C: and recovery)
4. Resize Ubuntu partition to fill the space
5. Mount EFI partition and delete Windows folder
6. Run `sudo update-grub` to clean up boot menu

### Option B: Clean Install (Wipe Everything)

**How it works:**
- Erase entire disk
- Install only Ubuntu
- Windows gone completely

**Pros:**
- Simpler, cleaner setup
- Full disk space for Ubuntu
- No bootloader complications
- Faster installation
- No cleanup work later

**Cons:**
- No going back (without reinstalling Windows from scratch)
- Must have all credentials/files backed up
- If critical hardware doesn't work, you're stuck

### My Recommendation: Hybrid Approach

```
1. Test in live USB first (you're already doing this)
   ↓
2. If ALL hardware works perfectly → Clean install
   ↓
3. If something doesn't work but you found a fix → Clean install
   ↓
4. If something critical doesn't work and no fix found:
   → Dual boot (keep Windows as fallback)
   → Or reconsider if Linux is right for this laptop
```

**The key insight:** If you tested thoroughly in the live environment and everything works, dual boot provides no real safety benefit. The live USB test IS your safety test.

---

## 5. The Recommended Path

### For You (2018 Dell, OpenClaw is the goal):

**My recommendation: Test in live USB → Clean install**

**Reasoning:**
- 2018 Dell is old enough that Linux driver support is mature
- OpenClaw only needs Node.js 22 + network - not exotic hardware
- You have technical background to troubleshoot
- Clean install is simpler and you get full disk space
- You already want to ditch Windows ("rip off Windows")

### Pre-Installation Checklist

Before clicking "Install Ubuntu":

- [ ] All browser passwords exported to CSV and saved on external drive
- [ ] All WiFi passwords documented
- [ ] All important files backed up to external drive/cloud
- [ ] Anthropic API key saved (for OpenClaw)
- [ ] 2FA recovery codes saved
- [ ] Tested WiFi in live USB - **works**
- [ ] Tested display in live USB - **works**
- [ ] Tested audio in live USB - **works**
- [ ] Tested keyboard/touchpad in live USB - **works**

### Installation Steps (Quick Version)

1. In live Ubuntu, click "Install Ubuntu" on desktop
2. Select language → Continue
3. Keyboard layout → Continue
4. "What apps would you like to install?" → **Normal installation**
5. Check: "Download updates" and "Install third-party software"
6. **Installation type** → **Erase disk and install Ubuntu**
   - This wipes Windows completely
7. Click "Install Now" → Confirm
8. Select timezone
9. Create user account (name, computer name, password)
10. Wait ~20 minutes
11. Restart → Remove USB when prompted
12. Done! Ubuntu boots

### After Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Run setup
openclaw onboard --install-daemon

# Verify
openclaw status
```

---

## Quick Reference: Dell Boot Keys

| Key | Function |
|-----|----------|
| F2 | Enter BIOS Setup |
| F12 | One-time Boot Menu |
| F8 | Safe Mode (Windows, not relevant here) |
| Fn + Power | Diagnostics (some models) |

---

## Sources

- [Ubuntu Official: Create Bootable USB with Rufus](https://ubuntu.com/tutorials/create-a-usb-stick-on-windows)
- [Dell Community: SD Card Boot Issues](https://www.dell.com/community/en/conversations/inspiron-desktops/how-do-i-boot-form-an-sd-card/647fa12df4ccf8a8de65c7c9)
- [Ubuntu Community: Remove Windows from Dual Boot](https://help.ubuntu.com/community/HowToRemoveWindows)
- [OSTechNix: Safely Remove Windows from Dual Boot](https://ostechnix.com/remove-windows-from-windows-linux-dual-boot/)
