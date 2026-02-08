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

### Current Model Chain (Live)

```
Primary:    anthropic/claude-sonnet-4-5    (paid API)
Fallback 1: openai/gpt-4o                 (paid API)
Fallback 2: google/gemini-2.5-flash       (needs API key)
Fallback 3: anthropic/claude-haiku-4-5    (paid API)
Fallback 4: ollama/qwen3:4b              (FREE, local, offline)
Heartbeat:  openai/gpt-4o-mini            (paid API)
Sub-agents: anthropic/claude-haiku-4-5    (paid API)
```

### Target Model Chain (After Gemini Key)

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

**Status: Installed and running** (v0.15.6, system service)

### Hardware

| Spec | Value |
|---|---|
| CPU | i7-10510U (4c/8t) |
| RAM | 16 GB (8 GB free) |
| GPU | NVIDIA MX230 (2 GB VRAM — too small for inference, CPU-only) |
| Ollama service | `systemctl status ollama` |

### Installed Models

| Model | Size | Quantization | Context | Role |
|---|---|---|---|---|
| `qwen3:4b` | 2.5 GB | Q4_K_M | 125k | Fallback #4, alias `qwen` |

### Adding More Models

```bash
ollama pull qwen2.5-coder:7b   # Code tasks (~4.5 GB)
ollama pull llama3.3:8b         # General chat (~4.7 GB)
```

### OpenClaw Integration (Done)

Systemd env (`~/.config/systemd/user/openclaw-gateway.service`):

```ini
Environment="OLLAMA_API_KEY=ollama-local"
```

OpenClaw auto-discovers tool-capable Ollama models. Streaming is disabled for Ollama (prevents garbled tool-use responses).

The `ollama-local` ClawHub skill (installed v1.1.0) provides model management commands through the Telegram bot.

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

## Cleanup Actions (All Done)

### Disabled WhatsApp Plugin

Was not linked, generating `TypeError: fetch failed` every ~10s in logs.

```json
// In openclaw.json > plugins.entries
"whatsapp": { "enabled": false }
```

### Disabled Stale Cron Job

"Claude Code monitor - voice recognition research" ran every 60s but always skipped (empty heartbeat file).

```json
// In ~/.openclaw/cron/jobs.json
"enabled": false
```

### Re-indexed Memory

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
