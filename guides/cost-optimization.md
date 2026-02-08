# API Cost Optimization Guide

> Strategies for minimizing API spend by leveraging subscriptions, free tiers, and local models.

---

## Subscriptions & What They Cover

| Subscription | Monthly | Covers |
|---|---|---|
| Claude Max (Pro) | $200 | Unlimited Opus/Sonnet/Haiku on claude.ai, Claude Code (OAuth) |
| ChatGPT Plus | $20 | Unlimited GPT-4o, DALL-E image gen, browsing on chatgpt.com |

### Key Insight

Use **claude.ai** and **Claude Code (OAuth)** for all interactive/personal work. Use **chatgpt.com** for image gen and GPT-4o browsing. Only OpenClaw's autonomous Telegram bot needs API keys.

### Claude Code OAuth Setup

```bash
# Authenticate Claude Code with your Max subscription (not API key)
claude login
# Or:
claude config set --global apiKeySource oauth
```

This makes all Claude Code usage $0 incremental cost.

---

## OpenClaw Model Routing (Cost Tiers)

### Recommended Model Chain

```
Primary:    google/gemini-2.5-flash        (free tier: 15 RPM, 1M TPM)
Fallback 1: anthropic/claude-haiku-4-5     (cheap cloud backup)
Fallback 2: anthropic/claude-sonnet-4-5    (complex reasoning only)
Fallback 3: ollama/qwen3:4b               (offline/last resort, free)
Heartbeat:  google/gemini-2.5-flash-lite   (free)
Sub-agents: ollama/qwen3:4b               (free, ~5-10 tok/s on CPU)
```

### Config Changes (`~/.openclaw/openclaw.json`)

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "google/gemini-2.5-flash",
        "fallbacks": [
          "anthropic/claude-haiku-4-5",
          "anthropic/claude-sonnet-4-5",
          "ollama/qwen3:4b"
        ]
      },
      "heartbeat": {
        "every": "30m",
        "model": "google/gemini-2.5-flash-lite"
      },
      "subagents": {
        "maxConcurrent": 8,
        "model": "ollama/qwen3:4b"
      }
    }
  }
}
```

### Cost Comparison

| Component | Before | After |
|---|---|---|
| Primary chat | claude-sonnet-4-5 ($3/$15 per M) | gemini-2.5-flash (free tier) |
| Fallback | gpt-4o ($5/$15 per M) | haiku ($1/$5 per M) |
| Heartbeat | gpt-4o-mini (~$0.15/$0.60 per M) | gemini-2.5-flash-lite (free) |
| Sub-agents | claude-haiku-4-5 ($1/$5 per M) | ollama/qwen3:4b (free) |
| Claude Code | API-billed | $0 (Max subscription OAuth) |
| Personal chat | API via OpenClaw | $0 (claude.ai) |

**Estimated monthly API: ~$2-5** (down from ~$20-40)

---

## Ollama Setup (Local Inference)

### Hardware Requirements

| Spec | Minimum | This System |
|---|---|---|
| RAM | 8 GB free | ~8 GB free (16 GB total) |
| CPU | 4+ cores | i7-10510U (4c/8t) |
| GPU | Optional (MX230 too small) | CPU-only inference |

### Install

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Recommended Models

| Model | Size | Speed (CPU) | Use Case |
|---|---|---|---|
| `qwen3:4b` | ~2.5 GB | ~10-15 tok/s | Heartbeat, simple sub-agents |
| `qwen2.5-coder:7b` | ~4.5 GB | ~5-10 tok/s | Code tasks |
| `llama3.3:8b` | ~4.7 GB | ~5-8 tok/s | General chat fallback |

```bash
ollama pull qwen3:4b
```

### OpenClaw Integration

Add to systemd environment (`~/.config/systemd/user/openclaw-gateway.service`):

```ini
Environment="OLLAMA_API_KEY=ollama-local"
```

OpenClaw auto-discovers tool-capable Ollama models. No explicit provider config needed.

The `ollama-local` ClawHub skill (already installed) provides model management commands through the bot.

---

## Google Gemini Free Tier

### Get API Key

1. Go to https://aistudio.google.com/apikey
2. Create a key (free, no billing required)

### Free Tier Limits (Gemini 2.5 Flash)

| Limit | Value |
|---|---|
| Requests per minute | 15 |
| Tokens per minute | 1,000,000 |
| Requests per day | 1,500 |

For a personal Telegram bot, this is more than enough.

### Add to OpenClaw

Edit `~/.openclaw/agents/main/agent/auth-profiles.json`:

```json
{
  "google:default": {
    "provider": "google",
    "mode": "api_key",
    "apiKey": "YOUR_GEMINI_API_KEY"
  }
}
```

Then restart: `systemctl --user restart openclaw-gateway`

---

## Cleanup Actions

### Disable Unused Plugins

WhatsApp plugin (not linked, generates fetch errors every ~10s):

```json
// In openclaw.json > plugins.entries
"whatsapp": { "enabled": false }
```

### Remove Stale Cron Jobs

```json
// In ~/.openclaw/cron/jobs.json - set enabled: false
"enabled": false
```

### Re-index Memory

```bash
openclaw memory index
```

---

## Summary: Where Each Dollar Goes

| Activity | Tool | Cost |
|---|---|---|
| Coding, file editing | Claude Code (OAuth) | $0 (Max sub) |
| Personal conversations | claude.ai | $0 (Max sub) |
| Image generation | chatgpt.com (DALL-E) | $0 (Plus sub) |
| Web research | chatgpt.com browsing | $0 (Plus sub) |
| Telegram bot (simple) | Gemini Flash | $0 (free tier) |
| Telegram bot (complex) | Claude Haiku/Sonnet | ~$2-5/mo |
| Heartbeat | Gemini Flash Lite | $0 (free tier) |
| Sub-agents | Ollama local | $0 |
| Voice notes (STT) | OpenAI gpt-4o-mini-transcribe | ~$1-2/mo |
| Voice replies (TTS) | OpenAI gpt-4o-mini-tts | ~$0.50-1/mo |
