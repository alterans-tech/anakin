# OpenClaw Rate Limit & Context Optimization

## Problem

Anthropic free tier caps at 30k input tokens/min. With `contextTokens: 200000` and soft pruning at 30% (60k tokens), a single request can blow through the rate limit instantly, triggering HTTP 429 errors. The fallback chain then kicks in (landing on `gpt-4o`), but the root cause is context bloat — not provider availability.

## Solution

Reduce the context window and tighten pruning thresholds so requests stay well under the rate limit.

## Changes Applied

All changes are in `~/.openclaw/openclaw.json` under `agents.defaults`.

### Context token budget

```
contextTokens: 200000 → 80000
```

80k is generous for Sonnet (200k native window) but keeps individual requests under the rate limit. Most conversations rarely need >50k tokens of context.

### Context pruning thresholds

```json
"contextPruning": {
  "mode": "cache-ttl",
  "ttl": "1h",
  "keepLastAssistants": 2,
  "softTrimRatio": 0.2,
  "hardClearRatio": 0.35,
  "minPrunableToolChars": 20000
}
```

| Setting | Before | After | Effect |
|---------|--------|-------|--------|
| `keepLastAssistants` | 3 | 2 | Trims more aggressively, keeps conversation fresh |
| `softTrimRatio` | 0.3 | 0.2 | Soft trim at ~16k tokens (was ~60k) |
| `hardClearRatio` | 0.5 | 0.35 | Hard clear at ~28k tokens (was ~100k) |
| `minPrunableToolChars` | 50000 | 20000 | Prunes smaller tool outputs that accumulate |

### Compaction

```json
"compaction": {
  "mode": "safeguard",
  "reserveTokensFloor": 16000,
  "memoryFlush": {
    "enabled": true,
    "softThresholdTokens": 4000
  }
}
```

| Setting | Before | After | Effect |
|---------|--------|-------|--------|
| `reserveTokensFloor` | 24000 | 16000 | Triggers compaction earlier (24k was 30% of 80k) |
| `memoryFlush.softThresholdTokens` | 6000 | 4000 | Saves durable notes sooner |

### Max concurrent requests

```
maxConcurrent: 4 → 2
```

4 concurrent Anthropic requests each sending 20k+ tokens immediately exceeds 30k/min. Reducing to 2 limits parallel token consumption.

## How It Works Together

With the 80k window:
- Soft trim kicks in at ~16k tokens — trims oversized tool results early
- Hard clear kicks in at ~28k tokens — stays under 30k rate limit per request
- Compaction reserve at 16k ensures the system compacts before hitting limits
- Max 2 concurrent requests prevent parallel requests from stacking up

The fallback chain remains: `Sonnet → GPT-4o → Gemini (needs key) → Haiku`.

## Verification

```bash
# Restart service
systemctl --user restart openclaw-gateway.service

# Check status — should show (80k ctx)
openclaw status

# Watch logs for 429 errors (should be none)
journalctl --user -u openclaw-gateway.service -f

# After a few messages, check context utilization
openclaw sessions
```

## Session Reset

If an existing session is stuck on a fallback model with bloated context from old settings, clear it:

```bash
systemctl --user stop openclaw-gateway.service

# Reset sessions (bot starts fresh on next message)
echo '{}' > ~/.openclaw/agents/main/sessions/sessions.json

systemctl --user start openclaw-gateway.service
```

Old session JSONL files remain on disk in `~/.openclaw/agents/main/sessions/` and can be inspected if needed.

## Valid Config Values Reference

| Setting | Valid Values |
|---------|-------------|
| `contextPruning.mode` | `off`, `cache-ttl` |
| `tts.auto` | `off`, `always`, `inbound`, `tagged` |
| `compaction.mode` | `safeguard` |

**Do not use** `adaptive` or `aggressive` for `contextPruning.mode` — these crash the gateway.
