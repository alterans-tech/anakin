# OpenClaw (Moltbot/Clawdbot) - Complete Research Summary

> Research compiled: 2026-02-02

## What is OpenClaw?

**OpenClaw** is an open-source personal AI assistant created by Peter Steinberger. It was renamed twice (Clawdbot → Moltbot → OpenClaw) after Anthropic requested trademark changes. It gained **100,000+ GitHub stars** in 2 months, becoming one of the fastest-growing open-source projects ever.

**Key Differentiator:** Runs locally on YOUR hardware with full system access - not a cloud service.

---

## Core Capabilities

| Feature | Description |
|---------|-------------|
| **Multi-Channel** | WhatsApp, Telegram, Discord, Slack, Signal, iMessage, Teams |
| **System Access** | Shell commands, file management, browser automation |
| **Persistent Memory** | Remembers context across sessions via Markdown files |
| **700+ Skills** | Community plugins for everything from Spotify to Kubernetes |
| **Model Agnostic** | Claude, GPT-4, or local models |

---

## Architecture Overview

### Core Components

1. **Gateway** - Background service managing messaging platform connections
2. **Agent** - The LLM reasoning engine (Claude, GPT-4, local models)
3. **Skills** - Modular capabilities (browser automation, file access, integrations)
4. **Memory** - Persistent Markdown-based storage for context retention

### How It Works

```
User Message (WhatsApp/Telegram/etc.)
         ↓
    Gateway (Port 18789)
         ↓
    Agent (LLM reasoning)
         ↓
    Skills (execute actions)
         ↓
    Response back to user
```

---

## Top 10 Real-World Use Cases

### 1. Remote System Operations
Manage servers from WhatsApp - organize directories, trigger batch jobs, check disk usage from anywhere.

### 2. Automated Trading
Polymarket predictions based on real-time news sentiment monitoring.

### 3. Customer Support Automation
Handle "Where's my order?" tickets autonomously - 70% reduction in human ticket volume.

### 4. Personal Chief of Staff
Morning briefings, inbox cleanup (15k+ emails), calendar management, Stripe MRR checks.

### 5. Research & Summarization
YouTube transcripts to Apple Notes, Reddit discussions, news digests with citations.

### 6. Document Processing
Receipt OCR to spreadsheets, file organization by type, image watermarking.

### 7. Multi-Agent Development
6 agents handling trading, security, job scouting, Twitter growth, deployment.

### 8. Travel Automation
Research and booking via voice commands, meal planning with grocery delivery.

### 9. D&D Dungeon Master
Full campaigns with DALL-E map generation, HP/inventory tracking.

### 10. Serverless Monitoring
Uptime checks, log monitoring, API status tracking on Cloudflare Workers.

---

## Cost Reality Check

### Monthly Cost by Usage Level

| Usage Level | Monthly Cost | Token Usage | Notes |
|-------------|--------------|-------------|-------|
| Light | $10-30 | 2-5M tokens | Few commands/day |
| Moderate | $35-95 | 5-15M tokens | Regular daily use |
| Heavy | $210-525 | 15-50M tokens | Multiple automated jobs |
| Power User | $500-3,700+ | 50-180M tokens | 24/7 automation |

### API Pricing (Per Million Tokens)

**Anthropic Claude:**
| Model | Input | Output |
|-------|-------|--------|
| Claude Opus 4.5 | $5 | $25 |
| Claude Sonnet 4.5 | $3 | $15 |
| Claude Haiku 4.5 | $1 | $5 |

**OpenAI:**
| Model | Input | Output |
|-------|-------|--------|
| GPT-4 | $10 | $30 |
| GPT-4o | $5 | $15 |
| GPT-4o-mini | $0.15 | $0.60 |

### Real-World Cost Examples

- **Federico Viticci (MacStories):** $3,600 first month (180M tokens)
- **Single monitoring cron (every 5 min):** ~$128/month
- **Moderate developer:** $100-150/month total
- **Runaway automation loop:** $200 in ONE DAY

### Cost Breakdown

| Component | Cost Range |
|-----------|------------|
| OpenClaw Software | FREE (MIT License) |
| Hosting (local) | $0 |
| Hosting (cloud VPS) | $5-25/month |
| API Usage | $10-3,700+/month |
| **Total** | **$10-3,700+/month** |

---

## Security Assessment

### Critical Risks

| Risk | Severity | Description |
|------|----------|-------------|
| Prompt Injection | CRITICAL | Malicious emails/web content can hijack agent |
| Full System Access | CRITICAL | Compromise = total access to machine |
| Exposed Instances | HIGH | 1,800+ instances leaked API keys via Shodan |
| Supply Chain | HIGH | 14 malicious skills on ClawHub (Jan 2026) |
| Data Exfiltration | HIGH | Bypasses traditional DLP/proxies |

### The "Lethal Trifecta" (Palo Alto Networks)

1. Access to private data (emails, files, calendars)
2. Exposure to untrusted content (web pages, attachments)
3. Ability to communicate externally

### Essential Security Mitigations

1. **Docker Sandbox Mode**
   ```yaml
   agents.defaults.sandbox.mode: "non-main"
   ```

2. **Tailscale VPN** - Never expose gateway publicly

3. **Gateway Binding**
   ```yaml
   gateway.bind: "loopback"  # Local only
   ```

4. **DM Pairing Policy**
   ```yaml
   channels.whatsapp.dmPolicy: "pairing"  # Require approval
   ```

5. **Dedicated Accounts** - Never connect personal email/browser

6. **File Permissions**
   ```bash
   chmod 700 ~/.openclaw
   chmod 600 ~/.openclaw/openclaw.json
   ```

### Security Audit Commands

```bash
openclaw security audit --deep
openclaw security audit --fix
openclaw health
```

### OCSAS Security Levels

| Level | Name | Use Case |
|-------|------|----------|
| L1 | Solo/Local | Individual users |
| L2 | Team/Network | Family/team deployments |
| L3 | Enterprise | Compliance requirements |

---

## Skill Ecosystem (700+ Skills)

### Skill Categories

| Category | Count | Examples |
|----------|-------|----------|
| DevOps & Cloud | 41 | Kubernetes, Azure, Cloudflare, Vercel |
| Notes & PKM | 44 | Obsidian, Notion, note-taking |
| Marketing & Sales | 42 | CRM, automation, lead gen |
| Productivity | 42 | Task management, workflows |
| AI & LLMs | 38 | Model integrations |
| Transportation | 34 | Travel, navigation |
| Smart Home & IoT | 31 | HomeKit, Hue, automation |
| Finance | 29 | Banking, crypto, tracking |
| Media & Streaming | 29 | Spotify, YouTube, podcasts |
| Health & Fitness | 26 | Workout tracking, monitoring |
| Communication | 26 | Email, messaging, video |
| Search & Research | 23 | Tavily, Brave, arXiv |
| Shopping | 22 | E-commerce, price tracking |
| Speech & Transcription | 21 | Voice recognition |
| Image & Video | 19 | Flux, ComfyUI, Figma |
| Calendar | 16 | Scheduling, sync |
| Coding Agents | 15 | Claude Code, Cursor |
| Apple Apps | 14 | Music, Photos, HomeKit |
| Web & Frontend | 14 | Discord, Slack, UI tools |
| iOS/macOS Dev | 13 | Apple platform tools |
| PDF & Documents | 12 | Processing, manipulation |
| Browser & Automation | 11 | Playwright, CDP |
| Self-Hosted | 11 | Automation platforms |
| Git & GitHub | 9 | PR management, docs |
| Security | 6 | 1Password, Bitwarden |

### Top 20 Most Useful Skills

**Development:**
1. GitHub Integration - PR management, issues
2. Claude Code - AI coding assistance
3. Cursor - IDE integration
4. Git-Notes - Persistent memory via Git
5. Frontend Design - UI/UX auditing

**DevOps:**
6. Kubernetes - Container orchestration
7. Cloudflare - CDN/DNS management
8. Azure CLI - Cloud operations
9. Vercel - Deployment automation
10. Proxmox - Virtualization

**Productivity:**
11. Obsidian - Knowledge management
12. Todoist - Task management
13. LanceDB - Vector database memory
14. Notion - Workspace management
15. Calendar Sync - Multi-platform

**Search & Research:**
16. Tavily Search - AI-powered search
17. Brave Search - Privacy-focused
18. arXiv - Academic papers
19. YouTube Transcripts - Video extraction
20. Exa Search - Advanced web search

### Installing Skills

```bash
# Install from ClawHub
clawhub install <skill-slug>

# Search for skills
clawhub search "calendar"

# Update all skills
clawhub update --all

# List installed
clawhub list
```

### Creating Custom Skills

```markdown
---
name: my-skill
description: What this skill does
user-invocable: true
---

# Skill Instructions

Your instructions for the AI here...
```

Save as `skills/my-skill/SKILL.md`

---

## Installation Guide

### Requirements

- **Node.js:** 22+
- **OS:** Linux (preferred), macOS, Windows (WSL2 only)
- **RAM:** 4GB minimum
- **API Key:** Anthropic or OpenAI

### Quick Install

```bash
# Install OpenClaw
curl -fsSL https://openclaw.ai/install.sh | bash

# Run setup wizard (installs daemon)
openclaw onboard --install-daemon

# Verify installation
openclaw status
openclaw health
```

### Alternative: npm Install

```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

### Channel Setup

**WhatsApp:**
```bash
openclaw channels login
# Scan QR code with WhatsApp → Settings → Linked Devices
```

**Telegram:**
1. Create bot via @BotFather
2. Store token in config or `TELEGRAM_BOT_TOKEN` env
3. Send `/start` to bot
4. Approve pairing code

**Discord:**
1. Create bot in Discord Developer Portal
2. Configure permissions and intents
3. Store token in `DISCORD_BOT_TOKEN`

### Gateway Commands

```bash
openclaw gateway start
openclaw gateway stop
openclaw gateway restart
openclaw gateway status
```

---

## Configuration

### Main Config File

Location: `~/.openclaw/openclaw.json`

```json
{
  "gateway": {
    "bind": "loopback",
    "port": 18789,
    "auth": {
      "mode": "token",
      "token": "your-secure-token"
    }
  },
  "channels": {
    "whatsapp": {
      "dmPolicy": "pairing",
      "groups": {
        "*": { "requireMention": true }
      }
    }
  },
  "sandbox": {
    "mode": "all",
    "scope": "agent",
    "workspaceAccess": "rw"
  }
}
```

### Environment Variables

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export TELEGRAM_BOT_TOKEN="your-token"
export DISCORD_BOT_TOKEN="your-token"
```

---

## Memory System

### Two-Layer Architecture

1. **Daily Logs** (`memory/YYYY-MM-DD.md`)
   - Append-only Markdown
   - Day-to-day context
   - Loaded at session start

2. **Long-term Memory** (`MEMORY.md`)
   - Curated facts and preferences
   - Decisions and durable information
   - Loaded in private sessions only

### Vector Search

- Hybrid retrieval (semantic + BM25)
- ~400-token chunks with 80-token overlap
- Providers: OpenAI, Gemini, local embeddings

---

## Best Practices

### Security Best Practices

| Category | Recommendation |
|----------|----------------|
| DM Access | Default to `pairing` mode |
| Groups | Require `@mentions` in public rooms |
| Tools | Use sandbox mode for execution |
| Models | Opus 4.5 for tool-enabled agents |
| Network | Loopback bind + Tailscale |
| Auth | Token-based with rotation |
| Filesystem | 700/600 permissions |
| Secrets | Never in agent-reachable paths |
| Skills | Review before enabling |
| Browser | Dedicated profile only |

### Cost Optimization

1. **Model Selection** - Use Haiku for simple tasks, Opus for complex
2. **Limit Automation** - Reduce cron frequency
3. **Monitor Usage** - `openclaw status --usage`
4. **Local Models** - $4K-6K upfront, no API costs

### Operational Best Practices

1. Test with simple tasks first
2. Monitor for hallucination
3. Be prepared for manual intervention
4. Regular security audits
5. Keep skills updated

---

## Troubleshooting

### Common Issues

**Gateway Won't Start:**
```bash
openclaw gateway logs
node --version  # Must be 22+
```

**WhatsApp Disconnected:**
```bash
openclaw channels login
# Re-scan QR code
```

**High API Costs:**
```bash
openclaw status --usage
# Check for runaway automations
```

**Skills Not Loading:**
```bash
clawhub list
clawhub update --all
```

---

## Links & Resources

### Official

- [OpenClaw Official](https://openclaw.ai/)
- [Documentation](https://docs.openclaw.ai/start/getting-started)
- [GitHub](https://github.com/openclaw/openclaw)
- [ClawHub Skills](https://clawhub.com)

### Setup Guides

- [Aman Khan: Setup in an Afternoon](https://amankhan1.substack.com/p/how-to-get-clawdbotmoltbotopenclaw) - **Best beginner guide**
- [DigitalOcean Quickstart](https://www.digitalocean.com/community/tutorials/moltbot-quickstart-guide)
- [Codecademy Tutorial](https://www.codecademy.com/article/open-claw-tutorial-installation-to-first-chat-setup)
- [NXCode Complete Guide](https://www.nxcode.io/resources/news/openclaw-complete-guide-2026)

### Security

- [Cisco: Security Nightmare](https://blogs.cisco.com/ai/personal-ai-agents-like-openclaw-are-a-security-nightmare)
- [OCSAS Security Framework](https://github.com/gensecaihq/ocsas)
- [Pulumi: Secure Deployment](https://www.pulumi.com/blog/deploy-openclaw-aws-hetzner/)
- [Dark Reading: AI Runs Wild](https://www.darkreading.com/application-security/openclaw-ai-runs-wild-business-environments)

### Cost Analysis

- [Fast Company: Gets Pricey Fast](https://www.fastcompany.com/91484506/what-is-clawdbot-moltbot-openclaw)
- [DEV: My $500 Reality Check](https://dev.to/thegdsks/i-tried-the-free-ai-agent-with-124k-github-stars-heres-my-500-reality-check-2885)
- [eesel.ai: Realistic Pricing](https://www.eesel.ai/blog/openclaw-ai-pricing)
- [Medium: Practical Cost Guide](https://medium.com/modelmind/how-much-does-it-cost-to-run-clawdbot-moltbot-a-practical-cost-guide-bee6774c6464)

### Community

- [Awesome OpenClaw Skills](https://github.com/VoltAgent/awesome-openclaw-skills) - 700+ skills
- [Hacker News Discussion](https://news.ycombinator.com/item?id=46838946)
- [Wikipedia](https://en.wikipedia.org/wiki/OpenClaw)
- [Discord Community](https://discord.gg/clawd)

### Deep Dives

- [IBM: Vertical Integration](https://www.ibm.com/think/news/clawdbot-ai-agent-testing-limits-vertical-integration)
- [Armin Ronacher: Pi Agent](https://lucumr.pocoo.org/2026/1/31/pi/)
- [Gary Marcus: Disaster Waiting](https://garymarcus.substack.com/p/openclaw-aka-moltbot-is-everywhere)
- [AIMultiple: Use Cases](https://research.aimultiple.com/moltbot/)

### Deployment

- [DigitalOcean One-Click](https://www.digitalocean.com/blog/moltbot-on-digitalocean)
- [Cloudflare Moltworker](https://github.com/cloudflare/moltworker)
- [Vultr Deployment](https://docs.vultr.com/how-to-deploy-openclaw-autonomous-ai-agent-platform)

---

## Key Warnings

1. **Don't underestimate costs** - API usage adds up fast, especially with automation
2. **Never run on primary machine** - Use separate hardware, VM, or cloud
3. **Prompt injection is real** - Malicious content can hijack your agent
4. **Skills can be malicious** - 14 bad skills found on ClawHub in Jan 2026
5. **Context corruption** - Can cause expensive token overages
6. **No enterprise security** - You are responsible for everything
7. **WhatsApp sessions expire** - Need to re-scan QR periodically

---

## Ecosystem Projects

- **Moltbook** - AI agent social network (agents-only posting)
- **ClawHub** - Official skills marketplace
- **Moltworker** - Cloudflare Workers deployment

---

## Summary for Your Setup

For your 2018 Dell laptop:

1. **Install Ubuntu 24.04 LTS** (best driver support for Dell)
2. **Use Docker** for OpenClaw isolation
3. **Get dedicated eSIM** for WhatsApp ($5-10/month)
4. **Use Anthropic API** (Claude recommended)
5. **Start with basic skills**, expand as needed
6. **Budget $50-100/month** for moderate use
7. **Never connect personal accounts** - use dedicated ones
