# Voice Authentication Setup Guide

Local speaker verification using SpeechBrain ECAPA-TDNN. Runs as a FastAPI microservice on `localhost:8200`. Zero cost, full privacy, zero additional latency (runs in parallel with STT).

---

## Prerequisites

- Python 3.10+
- ffmpeg (`sudo apt install ffmpeg`)
- ~1.5 GB disk (model + PyTorch + deps)
- ~300-500 MB RAM when running

## Quick Setup

```bash
./scripts/setup-voice-auth.sh
```

This will:
1. Create a Python venv at `configs/voice-auth/.venv/`
2. Install SpeechBrain, PyTorch, FastAPI, etc.
3. Download the ECAPA-TDNN model (~83 MB)
4. Create `~/.openclaw/voice-auth/{voiceprints,samples}/`
5. Copy the SKILL.md to `~/.openclaw/workspace/skills/voice-auth/`
6. Install and start the `voice-auth` systemd user service

## Service Management

```bash
# Status
systemctl --user status voice-auth

# Restart
systemctl --user restart voice-auth

# Stop
systemctl --user stop voice-auth

# Logs
journalctl --user -u voice-auth -f

# Manual start (development)
./scripts/start-voice-auth.sh
```

## Enrollment

Enroll your voice with 5-10 samples for a robust voiceprint. Use natural speech — different topics, energy levels, and environments.

### Via Telegram (recommended)

Send voice notes to Moltbot. Tell it: "I want to enroll my voice for authentication." It will guide you through the process using the voice-auth skill.

### Via curl

```bash
# Enroll a sample
curl -F "file=@voice_sample.ogg" -F "name=arnaldo" http://localhost:8200/enroll

# Check enrollment status
curl http://localhost:8200/speakers
```

### Tips for good enrollment

- Record 5-10 samples across different sessions/days
- Vary your energy: calm, energetic, tired
- Include different noise levels (quiet room, background noise)
- Speak naturally — don't recite scripts
- Each sample should be at least 5 seconds

## Verification

```bash
# Verify a voice sample
curl -F "file=@test_voice.ogg" http://localhost:8200/verify

# Response:
# {"verified": true, "speaker": "arnaldo", "confidence": 0.85, "threshold": 0.25}
```

## How It Works

1. User sends a voice note on Telegram
2. OpenClaw receives the audio and transcribes it via STT (3.2s)
3. **In parallel**, the voice-auth service extracts a speaker embedding (100-300ms)
4. If the request is admin-scoped, the agent checks voice verification
5. Verified → proceed. Not verified → ask for voice note.

### Admin scope (requires voice auth)

- Sharing passwords, API keys, credentials
- Modifying config, SOUL.md, skills
- Running sudo commands, changing services

### Not gated

- Casual chat, general questions, web search
- Smart home commands, calendar, reminders

## Threshold Tuning

Default threshold: `0.25` cosine similarity (lenient for personal use).

| Threshold | FAR | FRR | Use case |
|-----------|-----|-----|----------|
| 0.15 | ~5% | <0.5% | Very lenient (almost never rejects you) |
| 0.25 | ~3% | ~1% | **Default** — balanced for personal use |
| 0.35 | ~1% | ~3% | Stricter — may reject in noisy environments |
| 0.45 | <0.5% | ~5-10% | High security — frequent re-verification |

To change: set `VOICE_AUTH_THRESHOLD` in the systemd service file or pass `threshold` parameter in the verify request.

## API Reference

| Endpoint | Method | Body | Description |
|----------|--------|------|-------------|
| `/health` | GET | — | Service health + config |
| `/speakers` | GET | — | List enrolled speakers |
| `/enroll` | POST | `file` (audio), `name` (string) | Enroll a voice sample |
| `/verify` | POST | `file` (audio), `threshold` (optional float) | Verify speaker identity |
| `/speakers/{name}` | DELETE | — | Remove a speaker |

## Troubleshooting

### Service won't start

```bash
journalctl --user -u voice-auth -n 50
```

Common issues:
- Python venv missing: re-run `./scripts/setup-voice-auth.sh`
- Port 8200 in use: check `ss -tlnp | grep 8200`
- ffmpeg missing: `sudo apt install ffmpeg`

### Low confidence scores

- Enroll more samples (aim for 10+)
- Ensure enrollment samples match real usage conditions (same mic, similar noise)
- Lower threshold if needed (e.g., 0.15 for very noisy environments)

### Re-enrollment

```bash
# Delete existing voiceprint
curl -X DELETE http://localhost:8200/speakers/arnaldo

# Re-enroll with new samples
curl -F "file=@sample1.ogg" -F "name=arnaldo" http://localhost:8200/enroll
curl -F "file=@sample2.ogg" -F "name=arnaldo" http://localhost:8200/enroll
# ... repeat for 5-10 samples
```

## Data Locations

| Item | Path |
|------|------|
| Service code | `configs/voice-auth/speaker_service.py` |
| Pretrained model | `configs/voice-auth/pretrained_models/` |
| Voiceprints | `~/.openclaw/voice-auth/voiceprints/` |
| Individual samples | `~/.openclaw/voice-auth/samples/` |
| Systemd unit | `~/.config/systemd/user/voice-auth.service` |
| OpenClaw skill | `~/.openclaw/workspace/skills/voice-auth/SKILL.md` |

## Security Notes

- All processing is local — no audio leaves the machine
- Voiceprints are stored as numpy arrays, not raw audio
- Service binds to `127.0.0.1` only — not exposed to network
- Fail closed: if service is down, admin operations are denied
- Voice auth is an identity layer on top of Telegram's own authentication
