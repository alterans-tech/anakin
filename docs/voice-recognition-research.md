# Voice Recognition / Speaker Identification Research

> Research conducted 2026-02-08 for OpenClaw personal assistant (Anakin/Moltbot).
> Current STT: gpt-4o-mini-transcribe (~3.2s). Goal: identify WHO is speaking by voice.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Cloud Voice Biometrics Services](#2-cloud-voice-biometrics-services)
3. [Open-Source / Local Solutions](#3-open-source--local-solutions)
4. [Node.js Integration Options](#4-nodejs-integration-options)
5. [Cost Analysis](#5-cost-analysis)
6. [Accuracy Comparison](#6-accuracy-comparison)
7. [Privacy & Legal Considerations](#7-privacy--legal-considerations)
8. [Pipeline Integration](#8-pipeline-integration)
9. [Anti-Spoofing](#9-anti-spoofing)
10. [Recommendations](#10-recommendations)

---

## 1. Executive Summary

**Key finding: All major cloud providers are exiting voice biometrics.** Azure Speaker Recognition retired Sep 2025, AWS Voice ID retiring May 2026, Google never offered it. This strongly favors local/self-hosted solutions.

**Recommended approach: Local SpeechBrain ECAPA-TDNN** running as a FastAPI microservice on localhost:8200, called in parallel with existing OpenAI STT. Zero additional latency (100-300ms vs 3.2s STT), zero monthly cost, full privacy. Alternative: sherpa-onnx npm package for pure Node.js integration without Python.

| Criterion | Value |
|-----------|-------|
| **Best accuracy (open-source)** | NVIDIA TitaNet-Large: 0.66% EER |
| **Best balance (accuracy + simplicity)** | SpeechBrain ECAPA-TDNN: 0.80% EER |
| **Best Node.js native** | sherpa-onnx + CAM++: 0.73% EER |
| **Real-world accuracy (Telegram audio)** | ~2-4% EER |
| **Monthly cost (local)** | $0 |
| **Latency impact** | 0ms (runs in parallel with STT) |

---

## 2. Cloud Voice Biometrics Services

### Critical: Big-3 Cloud Providers Are Exiting

| Provider | Service | Status |
|----------|---------|--------|
| **Microsoft Azure** | Speaker Recognition | **RETIRED Sep 30, 2025** |
| **AWS** | Amazon Connect Voice ID | **End of support May 20, 2026** (no new customers since May 2025) |
| **Google Cloud** | Speaker ID | **Never offered** -- only diarization (who-spoke-when) within Speech-to-Text |

### Azure Speaker Recognition (Retired)

- **API**: Azure AI Speaker Recognition (Cognitive Services / Speech Service)
- **Pricing**: Free tier: 10,000 tx/month. Standard: exact price never publicly disclosed ("$-" placeholder).
- **Features**: 1:1 verification (text-dependent + text-independent), 1:N identification (max 50 speakers), 30s enrollment audio
- **Node.js**: `microsoft-cognitiveservices-speech-sdk` npm package
- **Migration targets**: ID R&D (IDVoice), Picovoice Eagle, Veritone

### AWS Amazon Connect Voice ID (Retiring May 2026)

- **Pricing**: $0.025/transaction, free tier: 180 tx/month (12 months)
- **Features**: Passive text-independent verification, fraudster detection, voice spoofing detection, 30s enrollment / 10s verification
- **Node.js**: `@aws-sdk/client-voice-id` npm package
- **Migration target**: Pindrop (official AWS recommendation)

### Google Cloud (Diarization Only)

- **Pricing**: $0.016-0.036/min (bundled with STT). Free: 60 min/month.
- **Features**: Speaker diarization only (labels words by speaker number). No verification or identification.
- **Node.js**: `@google-cloud/speech`

### Specialized Providers

| Provider | Type | Pricing | Node.js | Key Feature |
|----------|------|---------|---------|-------------|
| **Picovoice Eagle** | On-device | Free (personal); ~$899+/mo (commercial) | `@picovoice/eagle-node` | Fully on-device, no cloud |
| **ID R&D (IDVoice)** | Cloud/on-prem | Not public | REST API | 0.3% EER, #1 benchmarks |
| **Pindrop** | Enterprise | Not public | No | 99% deepfake detection, 60ms latency |
| **Veridas** | Cloud/on-prem | Not public | REST API | 3s verification, NIST #2 |
| **Resemble AI** | Cloud | **$0.0005/search** (flex) | `resemble-node` | Cheapest public pricing |
| **ValidSoft** | Cloud/on-prem | Not public | No | 98-99% accuracy |
| **Phonexia** | On-prem | Not public | REST API | 20s enroll, 3s verify |

---

## 3. Open-Source / Local Solutions

### Technical Concepts

**Speaker embeddings** are fixed-dimensional vectors representing voice characteristics:

| Type | Architecture | Dimensions | Era | EER |
|------|-------------|------------|-----|-----|
| d-vectors | GE2E LSTM | 256 | 2018 | ~4.5% |
| x-vectors | TDNN + stats pooling | 512 | 2018 | ~1.7% |
| **ECAPA-TDNN** | SE-Res2Net + attentive stats | **192** | 2020 | **0.80%** |
| TitaNet | Depth-wise separable Conv1D | 192 | 2022 | 0.66% |
| **CAM++** | D-TDNN + context masking | **192** | 2023 | **0.73%** |

**Verification (1:1)**: "Is this the owner?" -- compare against one voiceprint.
**Identification (1:N)**: "Who is this?" -- compare against N voiceprints.
**Diarization**: "Who spoke when?" -- segment + cluster speakers in a recording.

### Solution Comparison

| Feature | Resemblyzer | SpeechBrain | pyannote | WeSpeaker | NeMo TitaNet | 3D-Speaker | sherpa-onnx |
|---------|------------|-------------|----------|-----------|-------------|------------|-------------|
| **GitHub Stars** | 3.2k | 11.2k | 9.1k | 1.2k | 16.7k | 2.1k | 10.2k |
| **License** | Apache-2.0 | Apache-2.0 | MIT | Apache-2.0 | Apache-2.0 | Apache-2.0 | Apache-2.0 |
| **Best EER** | ~4.5% | **0.80%** | 2.8% | **0.72%** | **0.66%** | **0.73%** | Model-dependent |
| **Model Size** | 17MB | 83MB | 50-70MB | 26MB (ONNX) | 90MB | 25MB (CAM++) | 25-90MB |
| **CPU Inference** | 50-200ms | 100-300ms | ~50ms | ONNX fast | 150-400ms | ONNX fast | 50-200ms |
| **RAM** | 100-200MB | 300-500MB | 400-600MB | 200-400MB | 400-600MB | 200-400MB | 200-400MB |
| **GPU Needed?** | No | No | No | No | No* | No | No |
| **Node.js** | Subprocess | Subprocess | Subprocess | ONNX/sherpa | Subprocess | sherpa | **Native npm** |
| **ONNX** | No | Community | No | **Official** | Community | **Official** | Pre-exported |
| **Maintenance** | Inactive | Moderate | **Active** | Moderate | Active | Active | **Very active** |
| **Setup** | Very easy | Easy | Easy-Med | Easy-Med | Med-Hard | Medium | **Easy** |

### Detailed Profiles

#### SpeechBrain ECAPA-TDNN (Recommended for accuracy)

```python
from speechbrain.inference.speaker import SpeakerRecognition

verifier = SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="pretrained_models/spkrec-ecapa-voxceleb"
)
score, prediction = verifier.verify_files("speaker1.wav", "speaker2.wav")
embedding = verifier.encode_batch(waveform)  # shape: (1, 192)
```

- **EER**: 0.80% (VoxCeleb1-O Clean)
- **Dependencies**: PyTorch, SpeechBrain, torchaudio, HuggingFace Hub
- **Enrollment**: 5-15s across multiple samples, L2-normalize + average

#### sherpa-onnx (Recommended for Node.js native)

```javascript
const sherpa = require('sherpa-onnx');

const extractor = new sherpa.SpeakerEmbeddingExtractor({
  model: './3dspeaker_speech_campplus_sv_en_voxceleb_16k.onnx',
  numThreads: 2,
});
const manager = new sherpa.SpeakerEmbeddingManager(extractor.dim);

// Enrollment
manager.add('owner', extractor.compute(enrollmentSamples));

// Identification
const speaker = manager.search(extractor.compute(testSamples), threshold);
```

- **npm**: `sherpa-onnx`
- **Models**: 38 pre-exported ONNX models (WeSpeaker, 3D-Speaker, NeMo)
- **CAM++ model**: 0.73% EER, ~25MB, 50-200ms on CPU

#### Resemblyzer (Simplest for prototyping)

```python
from resemblyzer import VoiceEncoder, preprocess_wav
encoder = VoiceEncoder()
wav = preprocess_wav(Path("audio.wav"))
embedding = encoder.embed_utterance(wav)  # shape: (256,)
```

- **EER**: ~4.5% (lower accuracy, but sufficient for basic ID)
- **Model**: 17MB, no PyTorch needed
- **Status**: Inactive maintenance -- good for prototyping only

---

## 4. Node.js Integration Options

### Strategy A: Python HTTP Microservice (Recommended)

```
Node.js (OpenClaw) --HTTP POST--> FastAPI (localhost:8200) --JSON--> Node.js
                                   (SpeechBrain model loaded in memory)
```

| Aspect | Details |
|--------|---------|
| **Latency** | ~100-300ms (model stays loaded) |
| **Setup** | FastAPI + SpeechBrain + systemd service |
| **Accuracy** | 0.80% EER (ECAPA-TDNN) |
| **RAM** | ~300-500MB additional |

```python
# speaker_service.py
from fastapi import FastAPI, UploadFile
from speechbrain.inference.speaker import SpeakerRecognition
import torch

app = FastAPI()
verifier = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb")
voiceprints = {}  # name -> averaged embedding

@app.post("/identify")
async def identify(file: UploadFile, threshold: float = 0.25):
    embedding = verifier.encode_batch(waveform)
    best_match, best_score = None, -1
    for name, vp in voiceprints.items():
        score = torch.nn.functional.cosine_similarity(embedding, vp)
        if score > best_score:
            best_match, best_score = name, score.item()
    if best_score >= threshold:
        return {"speaker": best_match, "confidence": best_score}
    return {"speaker": "unknown", "confidence": best_score}
```

```bash
# Run as systemd user service on port 8200
uvicorn speaker_service:app --host 127.0.0.1 --port 8200
```

### Strategy B: sherpa-onnx Native Node.js (No Python)

```
Node.js (OpenClaw) --native addon--> sherpa-onnx C++ core --ONNX model--> result
```

| Aspect | Details |
|--------|---------|
| **Latency** | ~50-200ms |
| **Setup** | `npm install sherpa-onnx` + download ONNX model |
| **Accuracy** | 0.73% EER (CAM++) |
| **RAM** | ~200-300MB additional |
| **Advantage** | No Python dependency |

### Strategy C: ONNX Runtime Node.js (Direct inference)

- `onnxruntime-node` npm package with WeSpeaker ONNX models
- Challenge: must handle audio preprocessing (resampling, mel-spectrograms) in JS
- ~50-200ms latency

### Strategy Comparison

| Scenario | Best Strategy |
|----------|--------------|
| Quickest to deploy | A (FastAPI + SpeechBrain) |
| Best Node.js native | B (sherpa-onnx npm) |
| Lowest latency | B (sherpa-onnx) |
| Most accurate | A (SpeechBrain ECAPA-TDNN) |
| No Python at all | B (sherpa-onnx) |

---

## 5. Cost Analysis

### Monthly Cost Estimates (~75 voice messages/day, ~2,250/month)

| Solution | Monthly Cost | Notes |
|----------|-------------|-------|
| AWS Voice ID | ~$56.25 | $0.025 x 2,250 -- retiring May 2026 |
| Picovoice Eagle (cloud) | ~$22.50 | $0.01 x 2,250 |
| Resemble AI Identity | ~$1.13 | $0.0005 x 2,250 |
| Google Cloud (diarization only) | ~$2.70-$5.40 | Bundled with STT |
| **Local (SpeechBrain/sherpa)** | **< $0.01** | **Electricity only** |

### Local Cost Breakdown

| Component | Value |
|-----------|-------|
| CPU inference power delta | ~3-10W per inference |
| Inference time per message | 100-300ms |
| Daily inference time (75 msgs) | ~7.5-22.5 seconds |
| Monthly inference time | ~4-11 minutes |
| Monthly energy | ~0.001-0.004 kWh |
| Monthly cost (EU avg $0.30/kWh) | **< $0.01** |
| One-time setup time | 2-4 hours |

---

## 6. Accuracy Comparison

### Benchmark EER (VoxCeleb1-O Clean)

| Model | EER | Type |
|-------|-----|------|
| NVIDIA TitaNet-Large | **0.66%** | Open-source (NeMo) |
| WeSpeaker ResNet34-LM | **0.72%** | Open-source |
| 3D-Speaker CAM++ | **0.73%** | Open-source |
| SpeechBrain ECAPA-TDNN | **0.80%** | Open-source |
| Azure Speaker Recognition | ~1-2% (est.) | Cloud (retired) |
| pyannote embedding | 2.8% | Open-source |
| Resemblyzer | ~4.5% | Open-source |

### Real-World Degradation (Telegram Audio)

| Factor | Impact on EER |
|--------|--------------|
| Noisy environment | 2-10x worse (SNR 0-10 dB) |
| Opus codec compression | 1.5-3x worse |
| Short utterances (<3s) | 2-5x worse |
| Different languages | 1.5-2x worse |
| Channel mismatch | 2-4x worse |

**CommonBench** (realistic benchmark, 10x more speakers): ECAPA-TDNN at **3.09% EER** -- better estimate of real-world.

**Expected with Telegram Opus, moderate noise, 5-10s**: **2-4% EER**

### FAR vs FRR Threshold Tuning

| Setting | FAR | FRR | Use Case |
|---------|-----|-----|----------|
| High security | <0.1% | 5-10% | Banking |
| Balanced (at EER) | ~1-3% | ~1-3% | General auth |
| **High convenience** | **3-5%** | **<0.5%** | **Personal assistant (recommended)** |

For personal use: lenient threshold (0.25 cosine similarity start) -- almost never reject real user.

---

## 7. Privacy & Legal Considerations

### GDPR (EU)

| Aspect | Details |
|--------|---------|
| Classification | Voiceprints = **biometric data** (GDPR Article 9, special category) |
| General rule | Biometric processing for identification prohibited by default |
| **Personal exemption** | Art. 2(2)(c): GDPR does not apply to **purely personal/household activity** |
| Assessment | Personal AI assistant identifying owner likely qualifies for exemption |
| If identifying others | Explicit consent + DPIA required for family/guests |

### US State Laws

| State | Law | Personal Use |
|-------|-----|-------------|
| Illinois | BIPA | Exempt |
| Texas | CUBI | Exempt |
| Washington | HB 1493 | Exempt |
| California | CCPA/CPRA | Applies to businesses only |

### Voiceprint Reverse Engineering

- **Vendor claim**: "Cannot be reverse-engineered"
- **Reality**: **Voxstructor** research demonstrated voice reconstruction from voiceprint templates
- **Implication**: Leaked voiceprints could enable voice cloning
- **Unlike passwords**: You cannot change your voice
- **Mitigation**: Local-only storage + encryption eliminates cloud breach risk

### Cloud vs Self-Hosted

| Factor | Cloud | Self-Hosted |
|--------|-------|-------------|
| Data location | Provider's servers | Your machine |
| Third-party access | Provider + law enforcement | Only you |
| Data breach risk | Provider-side breach exposes all | Only your data |
| Transmission | Audio over internet | No network transmission |
| **Winner** | | **Self-hosted** |

---

## 8. Pipeline Integration

### Current Pipeline

```
Telegram voice note (.ogg/opus)
    → OpenClaw receives
    → gpt-4o-mini-transcribe STT (~3.2s)
    → Text response
```

### Proposed Pipeline (Zero Additional Latency)

```
Telegram voice note (.ogg/opus)
    → Extract audio
    → [PARALLEL]
        → Speaker ID embedding (~100-300ms local)  ← DONE first
        → STT transcription (~3.2s via OpenAI)     ← bottleneck
    → Attach speaker label to transcript
    → Route/respond based on identity
```

Speaker ID completes in 100-300ms while STT takes 3,200ms. Running in parallel = **zero additional wall-clock time**.

### Resource Requirements

| Resource | ECAPA-TDNN (SpeechBrain) | CAM++ (sherpa-onnx) | Resemblyzer |
|----------|-------------------------|---------------------|-------------|
| Model size | ~83MB | ~25MB | ~17MB |
| RAM (loaded) | ~300-500MB | ~200-300MB | ~100-200MB |
| CPU inference | 100-300ms | 50-200ms | 50-200ms |
| Accuracy (EER) | 0.80% | 0.73% | ~4.5% |

---

## 9. Anti-Spoofing

### Threat Landscape

| Metric | Value |
|--------|-------|
| AI voice cloning attack increase (2025) | **442%** |
| Time to clone a voice | **3-5 seconds** of audio |
| Cost of cloning tools | Free-$50/month |
| Best anti-spoofing EER (ASVspoof 5) | 7.6% (misses 7.6% of spoofs) |

### Risk Assessment for Personal Assistant

**Low concern**, because:

1. **Telegram is already authenticated** -- attacker needs account access first
2. **Attack chain is long**: compromise Telegram + obtain voice sample + generate clone + send as voice note
3. **Low-value target**: worst case is attacker chatting with your AI assistant through your already-compromised Telegram
4. **Voice ID is for identification, not security** -- Telegram 2FA is the real security layer

### Recommended Anti-Spoofing

1. Use voice ID for **identification/personalization only**, not security-critical auth
2. Rely on **Telegram 2FA** as primary security
3. Optional: alert if speaker confidence is unusually low
4. Optional: require text confirmation for sensitive actions (smart home, etc.)

---

## 10. Recommendations

### Primary: SpeechBrain ECAPA-TDNN via FastAPI

| Criterion | Value |
|-----------|-------|
| **Model** | `speechbrain/spkrec-ecapa-voxceleb` |
| **Deployment** | FastAPI on localhost:8200, systemd user service |
| **Integration** | HTTP POST from OpenClaw, parallel with STT |
| **EER** | 0.80% benchmark, ~2-4% real-world |
| **Latency** | 0ms additional (absorbed by 3.2s STT) |
| **Cost** | $0/month |
| **RAM** | ~300-500MB additional |
| **Privacy** | Full -- no audio leaves machine |

### Alternative: sherpa-onnx Node.js Native

| Criterion | Value |
|-----------|-------|
| **Package** | `sherpa-onnx` npm |
| **Model** | `3dspeaker_speech_campplus_sv_en_voxceleb_16k` (CAM++) |
| **EER** | 0.73% benchmark |
| **Advantage** | No Python dependency, native Node.js |
| **Tradeoff** | Newer ecosystem, native addon compilation |

### Why Not Cloud?

- Azure: **Dead** (retired Sep 2025)
- AWS: **Dying** (retiring May 2026)
- Google: **Doesn't exist** (diarization only)
- Specialized providers: Enterprise pricing, opaque, lock-in risk
- **Local is free, private, fast, and future-proof**

### Enrollment Strategy

1. Collect **5-10 voice notes** of natural speech (different days, moods, noise levels)
2. Extract embeddings from each sample
3. **L2-normalize** each embedding
4. **Average** the normalized embeddings → robust voiceprint
5. Store averaged voiceprint locally (encrypted)
6. Threshold: start at **0.25** cosine similarity (lenient) and tune

### Quick Prototype Path

Start with **Resemblyzer** (17MB, 5 lines of code, pip install) to validate the concept, then upgrade to SpeechBrain ECAPA-TDNN or sherpa-onnx for production accuracy.

---

## Sources

### Cloud Services
- [Azure Speaker Recognition Retirement](https://azure.microsoft.com/en-us/updates?id=azure-ai-speaker-recognition-retirement)
- [AWS Voice ID End of Support](https://docs.aws.amazon.com/connect/latest/adminguide/amazonconnect-voiceid-end-of-support.html)
- [Google Cloud Speaker Diarization](https://docs.google.com/speech-to-text/docs/multiple-voices)
- [Picovoice Eagle](https://picovoice.ai/docs/eagle/)
- [Resemble AI Pricing](https://www.resemble.ai/pricing/)
- [ID R&D IDVoice](https://docs.idrnd.net/voice/)
- [Pindrop Passport](https://www.pindrop.com/product/pindrop-passport/)
- [Veridas das-Peak](https://docs.veridas.com/das-peak/cloud/v2.11/)

### Open-Source Solutions
- [SpeechBrain ECAPA-TDNN](https://huggingface.co/speechbrain/spkrec-ecapa-voxceleb)
- [sherpa-onnx GitHub](https://github.com/k2-fsa/sherpa-onnx)
- [sherpa-onnx npm](https://www.npmjs.com/package/sherpa-onnx)
- [pyannote-audio GitHub](https://github.com/pyannote/pyannote-audio)
- [WeSpeaker GitHub](https://github.com/wenet-e2e/wespeaker)
- [NVIDIA TitaNet-Large](https://huggingface.co/nvidia/speakerverification_en_titanet_large)
- [3D-Speaker / CAM++](https://github.com/modelscope/3D-Speaker)
- [Resemblyzer GitHub](https://github.com/resemble-ai/Resemblyzer)
- [Kaldi GitHub](https://github.com/kaldi-asr/kaldi)

### Research & Benchmarks
- [ECAPA-TDNN Paper (Interspeech 2020)](https://arxiv.org/abs/2005.07143)
- [CAM++ Paper (Interspeech 2023)](https://www.isca-archive.org/interspeech_2023/wang23ha_interspeech.pdf)
- [Comparison of Modern Deep Learning Models for Speaker Verification (MDPI)](https://www.mdpi.com/2076-3417/14/4/1329)
- [ASVspoof 5 Challenge](https://www.asvspoof.org/)
- [Voxstructor: Voice Reconstruction from Voiceprint](https://link.springer.com/chapter/10.1007/978-3-030-91356-4_20)
- [CommonBench Speaker Verification](https://arxiv.org/html/2509.17091v1)

### Privacy & Legal
- [GDPR Article 9 - Biometric Data](https://gdpr-info.eu/art-9-gdpr/)
- [Illinois BIPA](http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=3004&ChapterID=57)
- [US State Biometric Privacy Laws (Husch Blackwell)](https://www.huschblackwell.com/2025-state-biometric-privacy-law-tracker)
