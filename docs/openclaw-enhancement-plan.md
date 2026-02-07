# OpenClaw Enhancement Plan

> **This document persists across sessions.** Re-read after every compaction.
> Last updated: 2026-02-07

---

## Table of Contents

1. [Changes Already Made](#changes-already-made)
2. [Local Model Training & Offline Learning](#local-model-training--offline-learning)
3. [Video Avatar Calls](#video-avatar-calls)
4. [Smart Home Integration](#smart-home-integration)
5. [Productivity Skills](#productivity-skills)
6. [Manual Setup Instructions](#manual-setup-instructions)

---

## Changes Already Made

### 1. OpenClaw Updated to v2026.2.6-3
- Updated from v2026.2.3-1 via `npm install -g openclaw@latest`
- Systemd service description and version updated

### 2. Persistent Fetch Errors Fixed
- **Root cause**: Node.js IPv6 DNS resolution for `api.telegram.org` on flaky WiFi
- **Fix**: Added `NODE_OPTIONS=--dns-result-order=ipv4first` to systemd service

### 3. Memory Plugin Enabled
- Added OpenAI API key to `~/.openclaw/agents/main/agent/auth-profiles.json`
- Memory uses `text-embedding-3-small` from OpenAI
- Built index: `openclaw memory index`
- Status: vector ready, FTS ready

### 4. Cost-Optimized Model Routing
**Before**: Opus as primary (~$5/$25 per MTok)
**After**:
| Role | Model | Cost (input/output per MTok) |
|------|-------|------------------------------|
| Primary | claude-sonnet-4-5 | $3 / $15 |
| Fallback 1 | gpt-4o | $2.50 / $10 |
| Fallback 2 | claude-haiku-4-5 | $1 / $5 |
| Heartbeat (30m) | gpt-4o-mini | $0.15 / $0.60 |
| Sub-agents | claude-haiku-4-5 | $1 / $5 |

6 model aliases configured: opus, opus45, sonnet, haiku, gpt4o, mini

**Future optimization** (even cheaper options to consider adding):
| Model | Cost (input/output per MTok) | Best For |
|-------|------------------------------|----------|
| Gemini 2.5 Flash-Lite | $0.10 / $0.40 | Cheapest mainstream, heartbeats |
| DeepSeek V3.1 Chat | $0.15 / $0.75 | Budget sub-agents, classification |
| DeepSeek R1 Reasoner | $0.55 / $2.19 | Strong reasoning at 90% less than Opus |
| OpenRouter Auto | Varies | Auto-picks cheapest capable model |

To add these, get API keys from deepseek.com and ai.google.dev, then add as providers
in `openclaw.json` under a `models.providers` section (see model routing research).
Budget limits: `openclaw config set daily_budget_usd 5.00` / `monthly_budget_usd 50.00`
Mid-session switching: `/model opus` to escalate, `/model haiku` for simple tasks

### 5. Voice Capabilities Enabled
- **TTS**: Edge TTS (free, no API key) - voice: `en-US-GuyNeural`
- **TTS mode**: `inbound` (reads incoming messages aloud when user sends voice)
- **STT**: Built-in audio pipeline using `gpt-4o-mini-transcribe` (~3.2s for 15s clip vs ~49s local Whisper)
- **Voice-call plugin**: Enabled, running on `:3334`
- **Whisper**: Local `openai-whisper` skill ready as fallback (no API key needed)
- **TTS slash commands**: `/tts off|always|inbound|tagged`, `/tts provider edge|openai|elevenlabs`
- **Voice note bubbles**: Use `[[audio_as_voice]]` tag in Telegram responses for round bubble UI

### 6. OPENAI_API_KEY in Environment
- Added to systemd service for skills like `openai-image-gen` and `openai-whisper-api`

### 7. WhatsApp Channel Configured
- Added to `openclaw.json` with `dmPolicy: "pairing"`
- Plugin enabled
- **Status**: Needs QR code pairing (see Manual Setup section)

### 8. ClawHub Skills Installed
- `clawhub` CLI installed globally via npm
- Skills installed from ClawHub:
  - `liveavatar` - Real-time video avatar (LiveAvatar API)
  - `ollama-local` - Local Ollama model management
  - `heygen-avatar-lite` - HeyGen AI avatar video generation
  - `notion-api-skill` - Notion API integration
  - `trello-api` - Trello board management

### 9. Fast Voice Note Transcription
- Added `tools.media.audio` config with `gpt-4o-mini-transcribe`
- Voice notes now transcribed in ~3.2s (was ~49s with local Whisper on CPU)
- Uses existing `OPENAI_API_KEY`, no additional cost setup needed
- Falls back to local Whisper CLI if cloud unavailable

### 10. Cleaned Up
- Removed empty `/home/anakin/moltbot/` directory

---

## Local Model Training & Offline Learning

### Goal
Enable the assistant to learn from user interactions, fine-tune on specific tasks, and run models locally for offline capability and cost savings.

### Architecture

```
┌─────────────────────────────────────────────────┐
│              OpenClaw Gateway                     │
│  ┌─────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ Cloud    │  │ Ollama   │  │ RAG Pipeline   │  │
│  │ Models   │  │ Local    │  │ (ChromaDB +    │  │
│  │ (Sonnet, │  │ Models   │  │  local embed)  │  │
│  │  GPT-4o) │  │ (Qwen,   │  │                │  │
│  │          │  │  Llama)  │  │                │  │
│  └─────────┘  └──────────┘  └────────────────┘  │
│       ↕              ↕              ↕             │
│  ┌──────────────────────────────────────────┐    │
│  │        Model Router / Fallback           │    │
│  └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────┘
         ↕
┌─────────────────────┐
│  Training Pipeline  │
│  (Unsloth / Axolotl)│
│  Fine-tune LoRA     │
│  adapters from      │
│  conversation logs  │
└─────────────────────┘
```

### Hardware Profile (Dell Vostro 5490)
| Component | Spec | Implication |
|-----------|------|-------------|
| CPU | Intel i7-10510U (4C/8T) | AVX2 capable, good for small model inference |
| RAM | 16GB DDR4 | Can run 7B quantized models |
| GPU | MX230 (2GB GDDR5) | Too little VRAM for training; marginal for inference offload |
| Storage | SSD | Adequate for models (1-6GB each) |

**Bottom line**: MX230 is unusable for fine-tuning (minimum 6GB VRAM needed). This is a **CPU-inference** and **RAG** workstation. Training must happen on cloud GPUs (free Colab/Kaggle) with results deployed locally.

### Phase 1: Local Inference with Ollama (No Training)
**Approach**: Run quantized models via Ollama for simple, repetitive tasks

**Expected performance on your CPU**:
- 1-3B models: ~30-50 tok/s
- 7B Q4: ~8-15 tok/s

1. **Install Ollama**:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```

2. **Pull lightweight models** (CPU-friendly):
   ```bash
   ollama pull qwen2.5:3b       # Fast, good reasoning, 2GB
   ollama pull phi3:mini         # Microsoft's small model, 2.3GB
   ollama pull llama3.2:3b       # Meta compact model, 2GB
   ollama pull nomic-embed-text  # Local embeddings, 274MB
   ```

3. **Configure OpenClaw** to use Ollama as fallback:
   Add to `openclaw.json` under `agents.defaults.models`:
   ```json
   "ollama/qwen3:4b": { "alias": "local" }
   ```

4. **Use for sub-agents**: The `ollama-local` skill (already installed) enables:
   ```python
   sessions_spawn(task="...", model="ollama/qwen3:4b", label="local-task")
   ```

### Phase 2: RAG with Local Embeddings (Learn from Documents)
**Purpose**: Let the assistant learn from your specific documents, notes, and conversation history without retraining.

1. **Local embeddings** via Ollama:
   ```bash
   ollama pull nomic-embed-text   # 274MB, outperforms OpenAI ada-002
   ```

2. **ChromaDB** for vector storage:
   ```bash
   pip install chromadb
   ```

3. **Custom knowledge pipeline**:
   - Feed business documents, meeting notes, project files
   - OpenClaw's built-in memory already does this partially
   - ChromaDB adds domain-specific knowledge retrieval

### Phase 3: Fine-Tuning with LoRA (Cloud GPU - Free)
**Purpose**: Train small models to handle your specific patterns, tone, and tasks.
**Where**: Google Colab (free T4, 15GB VRAM) or Kaggle (free P100/T4, 16GB)

1. **Unsloth** (recommended, most efficient LoRA training):
   - 2x faster training, 70% less VRAM than standard
   - Free Colab T4 handles 3B-7B models with QLoRA
   - Supports Llama, Mistral, Qwen, Phi, Gemma, DeepSeek
   - Native GGUF export for Ollama deployment

2. **Workflow** (train on cloud, deploy locally):
   ```
   a. Prepare training data locally (JSONL format)
   b. Upload to Google Colab
   c. Fine-tune with Unsloth QLoRA (free GPU)
   d. Export to GGUF format
   e. Download GGUF file locally
   f. Import into Ollama with Modelfile:
      FROM qwen2.5:3b
      ADAPTER ./my-adapter.gguf
      SYSTEM "Your custom system prompt"
   g. Register in OpenClaw as ollama/anakin-custom
   ```

3. **Axolotl** (alternative for complex pipelines):
   - YAML-based config, supports SFT + DPO + GRPO
   - Better for combining multiple datasets
   - Use when Unsloth's simple LoRA isn't enough

4. **Cost**: $0 with Colab/Kaggle free tier. If you need more: RunPod ~$0.50/hr, Vast.ai ~$0.30/hr

### Phase 4: Continuous Learning Loop
**Purpose**: The assistant improves over time from your feedback.

```
User interaction → Log to memory → Periodic batch:
  1. Extract high-quality Q&A pairs
  2. User rates/corrects responses
  3. Fine-tune LoRA adapter (DPO/RLHF via Hugging Face TRL)
  4. Deploy updated model
  5. Repeat
```

### Hardware Recommendations
| Setup | VRAM | RAM | What You Can Run |
|-------|------|-----|-----------------|
| Current (CPU) | 0 | 8-16GB | Qwen 4B, Phi Mini (slow) |
| + eGPU (RTX 3060) | 12GB | 16GB | 7B models, LoRA training |
| Cloud (Lambda/Vast) | 24-80GB | 32GB+ | Full fine-tuning, 13B+ models |

---

## Video Avatar Calls

### Goal
Enable face-to-face video calls with the AI assistant using a realistic avatar.

### Option 1: LiveAvatar (Recommended - Easiest)
**Already installed** as a ClawHub skill.

**Setup**:
1. Get free API key at https://app.liveavatar.com
2. Add to `openclaw.json`:
   ```json
   "skills": {
     "entries": {
       "liveavatar": {
         "env": { "LIVEAVATAR_API_KEY": "your_key" }
       }
     }
   }
   ```
3. Run `/liveavatar` in Telegram/WhatsApp to start
4. Opens browser at `http://localhost:3001` with webcam/mic
5. Full voice-to-voice with lip-synced avatar

**Pros**: Zero setup complexity, free tier, real-time lip-sync
**Cons**: Cloud-dependent, needs API key

### Option 2: HeyGen Avatar (High Quality)
**Already installed** as `heygen-avatar-lite` skill.

**Setup**:
1. Get API key at https://app.heygen.com
2. Free tier includes limited minutes
3. Best quality avatars, enterprise-grade

**Pros**: Professional quality, many avatar choices
**Cons**: Paid after free tier (~$24/mo for 15 min/mo)

### Option 3: Pipecat + Open-Source (Self-Hosted)
**For future consideration** - most flexible but complex.

**Architecture**:
```
Microphone → STT (Whisper) → OpenClaw → TTS (Edge) → Avatar → Virtual Camera → Video Call
```

**Components**:
- **Pipecat**: Open-source voice/video AI framework by Daily.co
- **MuseTalk**: Real-time lip-sync (needs 12GB+ VRAM for real-time)
- **SadTalker**: Face animation from audio (batch, not real-time)
- **v4l2loopback**: Linux virtual camera to pipe avatar into any app
- **pyvirtualcam**: Python library to send frames to virtual camera

**Limitations on current hardware**:
- MuseTalk needs 12GB+ VRAM for real-time (30fps on V100)
- SadTalker is batch-only, not real-time
- Would need external GPU or cloud rendering

### Option 4: Generic Virtual Camera Approach
**Works with any video call app** (Zoom, Google Meet, etc.)

```bash
# Install v4l2loopback (needs sudo)
sudo apt install v4l2loopback-dkms v4l2loopback-utils
sudo modprobe v4l2loopback

# Then use pyvirtualcam in Python to pipe AI avatar frames
pip install pyvirtualcam
```

This creates a virtual webcam device that appears in Zoom/Meet/Teams.

### Option 5: Hedra + LiveKit (Best Bang-for-Buck Cloud)
**Sub-100ms latency**, $0.05/min, open-source LiveKit Agents plugin.
```bash
pip install livekit livekit-agents livekit-plugins-hedra
```
Self-host LiveKit server (Go binary, free), pay only for avatar rendering.

### Video Avatar Cost Comparison
| Solution | Cost/min | Real-Time | Self-Hosted | Quality |
|----------|----------|-----------|-------------|---------|
| LiveAvatar | Free tier | Yes | No | Good |
| Hedra | $0.05 | Yes (<100ms) | Partial | High |
| Simli | $0.05 | Yes (<300ms) | No | Good |
| D-ID | $0.56-1.12 | Yes | No | High |
| HeyGen | $0.50-0.99 | Yes | No | Very High |
| MuseTalk | Free | Yes (30fps) | Yes | High |

### Platform Limitations
- **Telegram**: Video in group calls via pytgcalls (userbot, not official bot). No 1-on-1 video call API.
- **WhatsApp**: NO video call bot API. Only workaround: virtual camera + WhatsApp Desktop.
- **Zoom**: SDK supports bot participants. Alternative: virtual camera + desktop app.
- **Google Meet**: Media API (developer preview). Alternative: virtual camera + browser.
- **Custom WebRTC** (via LiveKit): Full control, best approach for dedicated interface.

### Recommendation
Start with **LiveAvatar** (Option 1) - it's already installed and requires only a free API key. For production use, **Hedra + LiveKit** (Option 5) offers the best price/performance at $0.05/min. Upgrade to **MuseTalk** when you have RTX 3090+ GPU for fully self-hosted avatar rendering.

---

## Smart Home Integration

### Philips Hue Lights

**Skill**: `openhue` (bundled with OpenClaw, requires CLI binary)

**Install OpenHue CLI**:
```bash
# Option A: Docker (no sudo needed)
docker pull openhue/cli
alias openhue='docker run -v "${HOME}/.openhue:/.openhue" --rm --name=openhue -it openhue/cli'

# Option B: Homebrew (if available)
brew tap openhue/cli && brew install openhue-cli

# Option C: Go install (if Go is available)
go install github.com/openhue/openhue-cli@latest
```

**Setup** (requires physical access to Hue Bridge):
```bash
openhue discover          # Find bridge on network
openhue setup             # Press bridge button when prompted
openhue get light --json  # Verify
```

**Example commands**:
```bash
openhue set light "Living Room" --on --brightness 80
openhue set light "Bedroom" --off
openhue set scene "Relax"
openhue set light "Office" --on --rgb #FF6600
```

### LG Air Conditioning (ThinQ)

**Method**: `thinqconnect-mcp` (MCP server) or `pythinqconnect` (Python SDK)

**Get PAT Token**:
1. Go to https://smartsolution.developer.lge.com/en/apiManage/thinq_connect
2. Sign in with your LG ThinQ account
3. Navigate to Cloud Developer > ThinQ Connect
4. Generate Personal Access Token (PAT)

**Option A: MCP Server (Recommended - Direct OpenClaw integration)**:
```bash
pip install thinqconnect-mcp
```

Add to `~/.openclaw/openclaw.json`:
```json
{
  "mcpServers": {
    "thinqconnect-mcp": {
      "command": "uvx",
      "args": ["thinqconnect-mcp"],
      "env": {
        "THINQ_PAT": "your_personal_access_token",
        "THINQ_COUNTRY": "BR"
      }
    }
  }
}
```

MCP tools available: `get_device_list`, `get_device_status`, `get_device_available_controls`, `post_device_control`

**Option B: Python SDK (for custom scripts)**:
```bash
pip install thinqconnect
```

**Supported AC controls**: Temperature, mode (cool/heat/fan/dry/auto), fan speed, on/off, timer, wind direction (52 properties total)

**PAT URL**: https://connect-pat.lgthinq.com (simpler than the developer portal)

### Google Calendar (Family Calendar)

**Skill**: `gog` (bundled with OpenClaw, requires CLI binary)

**Install gog CLI**:
```bash
# Homebrew (recommended)
brew tap steipete/tap && brew install gogcli

# Or download binary from https://gogcli.sh
```

**Setup Google OAuth**:
1. Go to https://console.cloud.google.com
2. Create a new project (or use existing)
3. Enable Gmail API, Calendar API, Drive API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download `client_secret.json`

**Configure gog**:
```bash
gog auth credentials /path/to/client_secret.json
gog auth add your@gmail.com --services gmail,calendar,drive,contacts
gog auth list  # Verify
```

**Example calendar commands**:
```bash
# List today's events
gog calendar events primary --from $(date -I) --to $(date -I -d '+1 day')

# Create event
gog calendar create primary --summary "Family Dinner" \
  --from "2026-02-08T19:00:00" --to "2026-02-08T21:00:00"

# List shared calendars
gog calendar list
```

**Set default account**:
```bash
export GOG_ACCOUNT=your@gmail.com
```

### Home Assistant (Optional Unified Hub)

If you want a single integration point for ALL devices:

```bash
# Install Home Assistant in Docker
docker run -d --name homeassistant \
  --restart=unless-stopped \
  -v /home/anakin/.homeassistant:/config \
  -e TZ=America/Sao_Paulo \
  --network=host \
  ghcr.io/home-assistant/home-assistant:stable
```

Then use `ha-mcp` to connect OpenClaw → Home Assistant → all devices.

---

## Productivity Skills

### Skill Priority for Entrepreneur/Developer
| Priority | Skill | Why |
|----------|-------|-----|
| 1 | github | Core dev workflow - PRs, issues, CI/CD |
| 2 | coding-agent | Delegate coding tasks to AI sub-agents |
| 3 | summarize | Research acceleration - URLs, PDFs, YouTube |
| 4 | model-usage | Budget control (needs CodexBar, Linux pending) |
| 5 | skill-creator | Build custom automations for your business |
| 6 | himalaya | Email triage and management |
| 7 | tmux | Infrastructure for coding-agent |
| 8 | notion | Knowledge management and project tracking |
| 9 | openai-image-gen | Quick visual asset generation |
| 10 | trello | Project board management |

### Already Working
| Skill | Status | Description |
|-------|--------|-------------|
| github | Ready | PR management, issues, CI runs |
| coding-agent | Ready | Run Claude Code, Codex, etc. |
| himalaya | Ready | Email via IMAP/SMTP |
| weather | Ready | No API key needed |
| nano-pdf | Ready | PDF editing |
| skill-creator | Ready | Create custom skills |
| healthcheck | Ready | Security auditing |
| voice-call | Ready | Voice calls on :3334 |
| blogwatcher | Ready | RSS/Atom feed monitoring |

### Newly Installed (Need API Keys)
| Skill | Source | Setup Required |
|-------|--------|---------------|
| liveavatar | ClawHub | LiveAvatar API key (free) |
| ollama-local | ClawHub | Ollama installed locally |
| heygen-avatar-lite | ClawHub | HeyGen API key |
| notion-api-skill | ClawHub | Notion integration token |
| trello-api | ClawHub | Trello API key + token |

### Bundled Skills Needing Setup
| Skill | Requires | Setup |
|-------|----------|-------|
| openhue | `openhue` CLI | Docker or Homebrew install + bridge button |
| gog | `gog` CLI | Binary install + Google OAuth |
| notion | `NOTION_API_KEY` env | Create integration at notion.so |
| tmux | `tmux` binary | `sudo apt install tmux` |
| session-logs | `jq` binary | Already installed |
| openai-image-gen | `OPENAI_API_KEY` | Already set in systemd env |
| openai-whisper-api | `OPENAI_API_KEY` | Already set in systemd env |
| summarize | binary deps | TBD |
| slack | Slack bot token | Create Slack app |

---

## Manual Setup Instructions

These require your interaction. Do them when you're back.

### Priority 1: System Packages (needs sudo password)

```bash
sudo apt-get update && sudo apt-get install -y \
  ffmpeg \
  tmux \
  ripgrep \
  sox \
  v4l2loopback-dkms \
  v4l2loopback-utils \
  python3-pip \
  docker.io
```

After installing, add yourself to docker group:
```bash
sudo usermod -aG docker $USER
# Log out and back in for group to take effect
```

### Priority 2: WhatsApp QR Pairing

```bash
openclaw channels login
# Select "WhatsApp"
# A QR code will appear in terminal
# On your phone: WhatsApp → Settings → Linked Devices → Link a Device
# Scan the QR code
```

### Priority 3: Ollama Installation

```bash
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull qwen3:4b
ollama pull nomic-embed-text
```

Verify with: `ollama list`

### Priority 4: LiveAvatar API Key

1. Go to https://app.liveavatar.com
2. Create free account
3. Copy API key
4. Add to config:
   ```bash
   # Edit ~/.openclaw/openclaw.json
   # Under skills.entries, add:
   "liveavatar": {
     "env": { "LIVEAVATAR_API_KEY": "your_key" }
   }
   ```
5. Restart gateway: `systemctl --user restart openclaw-gateway`

### Priority 5: OpenHue CLI (Hue Lights)

```bash
# Docker method (easiest, no sudo for CLI itself):
docker pull openhue/cli

# Create alias
echo 'alias openhue="docker run -v \"\${HOME}/.openhue:/.openhue\" --rm --name=openhue -it openhue/cli"' >> ~/.bashrc
source ~/.bashrc

# Setup (press Hue bridge button when prompted!)
openhue discover
openhue setup
```

### Priority 6: Google Calendar (gog CLI)

```bash
# Download gog binary
# Check https://gogcli.sh for latest release URL
# Or if brew is available:
brew tap steipete/tap && brew install gogcli
```

Then:
1. Create Google Cloud project at https://console.cloud.google.com
2. Enable Calendar API and Gmail API
3. Create OAuth credentials (Desktop app)
4. Download `client_secret.json`
5. Run:
   ```bash
   gog auth credentials ~/Downloads/client_secret.json
   gog auth add your@gmail.com --services gmail,calendar,drive,contacts
   ```

### Priority 7: LG ThinQ AC

1. Go to https://connect-pat.lgthinq.com
2. Sign in with your LG ThinQ account
3. Click "ADD NEW TOKEN" → grant all scopes
4. Copy the PAT token
5. Install MCP server:
   ```bash
   pip install thinqconnect-mcp
   ```
6. Add MCP config to `~/.openclaw/openclaw.json` (see Smart Home section)
7. Restart gateway: `systemctl --user restart openclaw-gateway`
8. Test: ask the assistant "list my LG devices"

### Priority 8: Notion Integration

1. Go to https://notion.so/my-integrations
2. Create new integration
3. Copy API key (starts with `ntn_` or `secret_`)
4. Store it:
   ```bash
   mkdir -p ~/.config/notion
   echo "ntn_your_key_here" > ~/.config/notion/api_key
   ```
5. Share target pages/databases with the integration in Notion UI

### Priority 9: Trello Integration

1. Get API key from https://trello.com/app-key
2. Generate token via the link on that page
3. Configure in the trello-api skill settings

---

## Voice Capabilities Reference

### TTS Providers Available
| Provider | Cost | Quality | Offline | Voice Calls |
|----------|------|---------|---------|-------------|
| Edge TTS (current) | Free | Good | No | No (no PCM) |
| OpenAI TTS (`gpt-4o-mini-tts`) | Paid | Very Good | No | Yes |
| ElevenLabs | Paid | Excellent | No | Yes |
| sherpa-onnx-tts | Free | Fair | Yes | No |

**Note**: Edge TTS does NOT work for voice calls (telephony needs PCM format). If voice calls are needed, switch to OpenAI or ElevenLabs TTS.

### STT Providers (Audio Transcription)
| Provider | Model | Speed (15s clip) | Cost |
|----------|-------|-------------------|------|
| OpenAI (current) | gpt-4o-mini-transcribe | ~3.2s | Cheap |
| OpenAI | gpt-4o-transcribe | ~3.5s | More accurate |
| Deepgram | nova-3 | Fast | Competitive |
| Local Whisper | whisper CLI | ~49s (CPU) | Free |
| sherpa-onnx | offline | Varies | Free |

### TTS Runtime Commands
```
/tts off           # Disable TTS
/tts always        # Every reply gets voice
/tts inbound       # Only when user sends voice (current)
/tts tagged        # Only when model tags reply
/tts provider edge # Switch to Edge TTS
/tts provider openai  # Switch to OpenAI TTS
```

### Voice Call Setup (When Ready)
Voice calls require a telecom provider (Twilio/Telnyx/Plivo) and a public webhook URL. Config:
```json
{
  "plugins": {
    "entries": {
      "voice-call": {
        "enabled": true,
        "config": {
          "provider": "twilio",
          "fromNumber": "+15550001234",
          "twilio": { "accountSid": "ACxxx", "authToken": "xxx" },
          "serve": { "port": 3334, "path": "/voice/webhook" },
          "expose": { "method": "tunnel" }
        }
      }
    }
  }
}
```

### Offline Voice (Fully Local, No Internet)
For offline TTS, install `sherpa-onnx-tts` skill:
```bash
npx add-skill https://github.com/openclaw/openclaw/sherpa-onnx-tts
# Download runtime + voice model to ~/.openclaw/tools/sherpa-onnx-tts/
```

---

## Current System Status

```
Gateway:       v2026.2.6-3, running, ws://127.0.0.1:18789
Primary Model: claude-sonnet-4-5 (1000k context)
Heartbeat:     gpt-4o-mini every 30m
Sub-agents:    claude-haiku-4-5 (max 8 concurrent)
TTS:           Edge TTS (free) - en-US-GuyNeural
STT:           gpt-4o-mini-transcribe (~3.2s per voice note)
Voice-call:    Running on :3334
Telegram:      ON, OK (@anakin_moltbot)
WhatsApp:      ON, WARN (needs QR pairing)
Memory:        Vector + FTS ready
Skills:        16/49 bundled ready + 5 ClawHub installed
Errors:        Zero fetch errors (IPv4-first fix)
```

---

## Next Steps After Manual Setup

Once the manual steps above are done:
1. Run `openclaw status --deep` to verify all channels
2. Run `openclaw skills list` to verify new skills are ready
3. Test each integration via Telegram:
   - "What's on my calendar today?"
   - "Turn on the living room lights"
   - "Set AC to 22 degrees cool mode"
   - "/liveavatar" to start video avatar
4. Consider `openclaw security audit --deep` after adding new integrations
