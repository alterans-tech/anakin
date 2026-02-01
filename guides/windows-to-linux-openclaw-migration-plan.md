# Windows to Linux Migration Plan for OpenClaw

**Target Device:** 2018 Dell Laptop
**Goal:** Fresh Linux install optimized for OpenClaw (formerly Clawdbot/Moltbot)
**Recommended Distro:** Ubuntu 24.04 LTS

---

## What is OpenClaw?

[OpenClaw](https://openclaw.ai/) is an open-source personal AI assistant created by Peter Steinberger. It was originally called **Clawdbot**, then renamed to **Moltbot** after Anthropic requested a trademark change (to avoid confusion with Claude), and is now called **OpenClaw**.

**Key Features:**
- Runs locally on your own hardware (privacy-focused)
- Connects to messaging platforms: WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Teams
- Can execute tasks: manage calendar, browse web, organize files, run terminal commands
- Supports multiple AI backends: Anthropic Claude, OpenAI, or local models
- Persistent memory across sessions

**Requirements:**
- Node.js 22+
- Linux (preferred), macOS, or Windows via WSL2
- API key for your LLM provider (Anthropic recommended)

---

## Phase 1: Backup Windows Credentials & Data

### 1.1 Browser Passwords

**Chrome:**
1. Open Chrome → Settings → Passwords
2. Click ⋮ (three dots) next to "Saved Passwords"
3. Select "Export passwords" → Save as CSV
4. Store CSV on USB drive (delete after importing to new system)

**Firefox:**
1. Open Firefox → Settings → Privacy & Security → Logins and Passwords
2. Click ⋮ → Export Logins → Save as CSV

**Edge:**
1. Open Edge → Settings → Passwords
2. Click ⋮ → Export passwords → Save as CSV

### 1.2 Windows Credential Manager

```powershell
# Run in PowerShell as Administrator
# View all credentials
cmdkey /list

# Document each credential manually (no direct export available)
# Take screenshots or copy to a secure note
```

### 1.3 WiFi Passwords

```powershell
# Run in PowerShell as Administrator
# List all saved WiFi networks
netsh wlan show profiles

# For each network, get the password:
netsh wlan show profile name="YOUR_WIFI_NAME" key=clear
```
Save the "Key Content" value for each network.

### 1.4 Application Licenses & API Keys

Document these:
- [ ] Microsoft Office product key
- [ ] **Anthropic API key** (for OpenClaw - get from console.anthropic.com)
- [ ] **OpenAI API key** (if using as alternative)
- [ ] Any other software license keys
- [ ] 2FA recovery codes

### 1.5 SSH Keys (if any)

```powershell
# Copy SSH keys if they exist
# Location: C:\Users\YOUR_USERNAME\.ssh\
```
Copy entire `.ssh` folder to USB drive.

### 1.6 General File Backup

- [ ] Documents folder
- [ ] Downloads folder
- [ ] Desktop files
- [ ] Any custom project folders

---

## Phase 2: Prepare Installation Media

### 2.1 Download Ubuntu 24.04 LTS

Download from: https://ubuntu.com/download/desktop

Verify SHA256 checksum after download.

### 2.2 Create Bootable USB

**On Windows (using Rufus):**
1. Download Rufus: https://rufus.ie/
2. Insert USB drive (8GB minimum)
3. Open Rufus
4. Select your USB drive
5. Click SELECT → Choose Ubuntu ISO
6. Partition scheme: GPT
7. File system: FAT32
8. Click START

**Alternative (using Balena Etcher):**
1. Download: https://etcher.balena.io/
2. Select Ubuntu ISO
3. Select USB drive
4. Flash

### 2.3 Document Dell BIOS Settings

Before changing anything, note current settings:
1. Restart laptop
2. Press F2 repeatedly during boot to enter BIOS
3. Document/photograph:
   - Boot order
   - Secure Boot status
   - SATA mode (AHCI vs RAID)

---

## Phase 3: Test Hardware Compatibility (CRITICAL)

**Do this BEFORE wiping Windows!**

### 3.1 Boot Live USB

1. Insert USB with Ubuntu
2. Restart laptop
3. Press F12 during boot for boot menu
4. Select USB drive
5. Choose "Try Ubuntu without installing"

### 3.2 Hardware Checklist

Test these in the live environment:

| Component | Test Method | Working? |
|-----------|-------------|----------|
| WiFi | Try connecting to network | [ ] |
| Ethernet | Plug in cable if available | [ ] |
| Display | Check resolution, brightness keys | [ ] |
| Audio | Play a YouTube video | [ ] |
| Touchpad | Gestures, clicking | [ ] |
| Keyboard | All keys, function keys | [ ] |
| USB Ports | Test with USB drive | [ ] |
| Webcam | Open Cheese app | [ ] |
| Bluetooth | Check Settings → Bluetooth | [ ] |

### 3.3 Identify Problem Hardware

If anything doesn't work:
```bash
# In live USB terminal
lspci -k  # Shows all hardware and drivers
lsusb     # Shows USB devices
```

Note the hardware model for any non-working components.

---

## Phase 4: Install Ubuntu 24.04 LTS

### 4.1 BIOS Configuration

1. Press F2 during boot
2. **Disable Secure Boot** (Security → Secure Boot → Disabled)
3. Set SATA mode to AHCI (if not already)
4. Save and exit (F10)

### 4.2 Installation Steps

1. Boot from USB (F12 → Select USB)
2. Click "Install Ubuntu"
3. Select language and keyboard
4. Choose "Normal installation"
5. Check:
   - [x] Download updates while installing
   - [x] Install third-party software (for WiFi, graphics, media)
6. Installation type: **"Erase disk and install Ubuntu"**
   - ⚠️ This wipes Windows completely
7. Select timezone
8. Create user account:
   - Your name
   - Computer name (e.g., `dell-laptop`)
   - Username
   - Strong password
9. Wait for installation to complete
10. Restart when prompted, remove USB

---

## Phase 5: Post-Installation Setup

### 5.1 System Updates

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install build-essential git curl wget -y
```

### 5.2 Install Additional Drivers (if needed)

```bash
# Open Software & Updates → Additional Drivers
# Or from terminal:
ubuntu-drivers devices
sudo ubuntu-drivers autoinstall
```

### 5.3 Install Node.js 22 (Required for OpenClaw)

```bash
# Install Node.js 22 via NodeSource
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Verify installation
node --version  # Should show v22.x.x
npm --version
```

### 5.4 Install OpenClaw

**Method 1: Quick Install (Recommended)**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Method 2: Via npm**
```bash
npm install -g openclaw@latest
```

### 5.5 Configure OpenClaw

Run the onboarding wizard with daemon installation:
```bash
openclaw onboard --install-daemon
```

The wizard will guide you through:
1. **LLM Provider** - Select Anthropic (recommended), OpenAI, or local model
2. **API Key** - Enter your Anthropic or OpenAI API key
3. **Workspace Setup** - Configure where OpenClaw stores data
4. **Channel Connections** - Link WhatsApp, Telegram, Discord, etc.
5. **Daemon Installation** - Installs systemd service to run on boot

### 5.6 Verify OpenClaw Installation

```bash
# Check status
openclaw status

# Health check
openclaw health

# View gateway logs
openclaw gateway logs
```

### 5.7 Connect Messaging Channels

**WhatsApp:**
```bash
openclaw channel add whatsapp
# Scan QR code with WhatsApp on your phone
```

**Telegram:**
```bash
openclaw channel add telegram
# Follow bot token setup instructions
```

**Discord:**
```bash
openclaw channel add discord
# Provide Discord bot token
```

### 5.8 Gateway Management Commands

```bash
openclaw gateway start    # Start the gateway
openclaw gateway stop     # Stop the gateway
openclaw gateway restart  # Restart the gateway
openclaw gateway status   # Check if running
```

---

## Phase 6: Restore Credentials

1. Import browser passwords from CSV into Firefox/Chrome
2. Reconnect to WiFi networks using saved passwords
3. Copy SSH keys back to `~/.ssh/` and fix permissions:
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_*
chmod 644 ~/.ssh/*.pub
```

---

## Troubleshooting Common Issues

### WiFi Not Working

```bash
# Check if hardware is detected
lspci | grep -i wireless

# For Broadcom chips:
sudo apt install bcmwl-kernel-source

# Restart network
sudo systemctl restart NetworkManager
```

### NVIDIA Graphics Issues

```bash
# Install NVIDIA drivers
sudo ubuntu-drivers autoinstall
sudo reboot
```

### OpenClaw Gateway Won't Start

```bash
# Check logs for errors
openclaw gateway logs

# Verify Node.js version
node --version  # Must be 22+

# Reinstall if needed
npm uninstall -g openclaw
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### OpenClaw Not Responding to Messages

```bash
# Check channel status
openclaw channel list

# Re-authenticate channel
openclaw channel reconnect whatsapp
```

---

## Security Considerations

OpenClaw requires significant system access to function. Consider these precautions:

1. **Sandbox Mode** - For group chats, enable Docker sandboxing:
   ```json
   // ~/.openclaw/openclaw.json
   {
     "sandbox": {
       "mode": "non-main"
     }
   }
   ```

2. **DM Pairing** - Enabled by default; unknown senders get pairing codes

3. **API Key Security** - Store keys in `~/.openclaw/` with proper permissions:
   ```bash
   chmod 600 ~/.openclaw/openclaw.json
   ```

---

## Cost Expectations

- **OpenClaw software:** Free (MIT License)
- **AI API costs:** ~$10-150/month depending on usage
  - Anthropic Claude: Pay-per-token
  - OpenAI: Pay-per-token
  - Local models: Free (but requires GPU)

---

## Quick Reference Card

| Task | Command |
|------|---------|
| Update system | `sudo apt update && sudo apt upgrade` |
| OpenClaw status | `openclaw status` |
| Start gateway | `openclaw gateway start` |
| View logs | `openclaw gateway logs` |
| Add WhatsApp | `openclaw channel add whatsapp` |
| Health check | `openclaw health` |
| List channels | `openclaw channel list` |

---

## Sources

- [OpenClaw Official Site](https://openclaw.ai/)
- [OpenClaw Documentation](https://docs.openclaw.ai/start/getting-started)
- [OpenClaw GitHub](https://github.com/openclaw/openclaw)
- [TechCrunch: Everything About Clawdbot/Moltbot](https://techcrunch.com/2026/01/27/everything-you-need-to-know-about-viral-personal-ai-assistant-clawdbot-now-moltbot/)
- [Dell Linux Support](https://www.dell.com/support/kbdoc/en-us/000138246/linux-on-dell-desktops-and-laptops)
- [Moltbot Quickstart - DigitalOcean](https://www.digitalocean.com/community/tutorials/moltbot-quickstart-guide)
