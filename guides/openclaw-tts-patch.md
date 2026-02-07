# OpenClaw TTS Patch — Fix Voice Note Delivery

## Problem

OpenClaw's TTS tool generates audio files at `/tmp/tts-xxx/voice-xxx.opus` and returns them as `MEDIA:/tmp/...` directives. The delivery pipeline's `isValidMedia()` function only accepts `./` relative paths and `http(s)://` URLs, so absolute `/tmp/` paths are rejected. This causes the literal text `MEDIA:/tmp/tts-xxx/voice-xxx.opus` to be sent to Telegram instead of the actual voice note.

## Root Cause

In `~/.npm-global/lib/node_modules/openclaw/dist/deliver-*.js`, the function:

```javascript
function isValidMedia(candidate, opts) {
    if (!candidate) return false;
    if (candidate.length > 4096) return false;
    if (!opts?.allowSpaces && /\s/.test(candidate)) return false;
    if (/^https?:\/\//i.test(candidate)) return true;
    return candidate.startsWith("./") && !candidate.includes("..");
}
```

Only accepts `./` relative paths and HTTP URLs. TTS generates files at `/tmp/` which fails validation.

## Fix

Add one line to accept `/tmp/` absolute paths (with path traversal protection):

```javascript
if (/^\/tmp\//.test(candidate) && !candidate.includes("..")) return true;
```

This is applied to all 3 `deliver-*.js` bundle files.

## Steps to Apply

### 1. Run the patch script

```bash
~/Workspace/alterans/anakin/scripts/patch-openclaw-tts.sh
```

### 2. Restart the gateway

```bash
systemctl --user restart openclaw-gateway.service
```

### 3. Verify

```bash
systemctl --user is-active openclaw-gateway.service
```

## After OpenClaw Updates

The patch is overwritten by `npm install -g openclaw@latest`. Re-run the patch script after every update:

```bash
~/Workspace/alterans/anakin/scripts/patch-openclaw-tts.sh
systemctl --user restart openclaw-gateway.service
```

## TTS Auto Mode

The `messages.tts.auto` setting in `~/.openclaw/openclaw.json` controls when audio is auto-generated:

| Value | Behavior |
|-------|----------|
| `off` | Audio only when user asks (bot uses TTS tool on demand) |
| `always` | Every reply gets a voice note |
| `inbound` | Voice reply only after receiving a voice note |
| `tagged` | Voice reply only when model emits `[[tts]]` tags |

Current setting: `off` — the bot sends audio only when explicitly asked.

## Files Modified

- `~/.npm-global/lib/node_modules/openclaw/dist/deliver-FdxL6NZx.js`
- `~/.npm-global/lib/node_modules/openclaw/dist/deliver-BIDW_mg2.js`
- `~/.npm-global/lib/node_modules/openclaw/dist/deliver-Ck-fH_m-.js`

## Patch Script

Location: `scripts/patch-openclaw-tts.sh`

Features:
- Idempotent (safe to run multiple times)
- Detects already-patched files
- Validates the patch was applied
- Supports custom install path via `OPENCLAW_DIST` env var
