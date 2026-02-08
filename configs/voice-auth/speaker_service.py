"""
Voice Authentication Microservice

FastAPI service wrapping SpeechBrain ECAPA-TDNN for speaker verification.
Stores voiceprints as .npz files in ~/.openclaw/voice-auth/voiceprints/.

Endpoints:
    POST /enroll   - Enroll a voice sample for a speaker
    POST /verify   - Verify a voice sample against enrolled speakers
    GET  /speakers - List enrolled speakers with sample counts
    GET  /health   - Health check
    DELETE /speakers/{name} - Remove a speaker's voiceprint
"""

import logging
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np
import torch
import torchaudio
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from speechbrain.inference.speaker import SpeakerRecognition

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-auth")

# --- Configuration ---
VOICEPRINT_DIR = Path.home() / ".openclaw" / "voice-auth" / "voiceprints"
SAMPLES_DIR = Path.home() / ".openclaw" / "voice-auth" / "samples"
DEFAULT_THRESHOLD = float(os.environ.get("VOICE_AUTH_THRESHOLD", "0.25"))
MODEL_SOURCE = "speechbrain/spkrec-ecapa-voxceleb"
MODEL_SAVEDIR = Path(__file__).parent / "pretrained_models" / "spkrec-ecapa-voxceleb"

# --- Startup ---
VOICEPRINT_DIR.mkdir(parents=True, exist_ok=True)
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Voice Auth", version="1.0.0")

logger.info("Loading SpeechBrain ECAPA-TDNN model...")
verifier = SpeakerRecognition.from_hparams(
    source=MODEL_SOURCE,
    savedir=str(MODEL_SAVEDIR),
)
logger.info("Model loaded.")

# In-memory cache of voiceprints: name -> numpy array (192,)
voiceprints: dict[str, np.ndarray] = {}


def _load_voiceprints():
    """Load all stored voiceprints from disk into memory."""
    voiceprints.clear()
    for npz_path in VOICEPRINT_DIR.glob("*.npz"):
        data = np.load(npz_path)
        voiceprints[npz_path.stem] = data["embedding"]
    logger.info("Loaded %d voiceprint(s) from disk.", len(voiceprints))


_load_voiceprints()


def _convert_to_wav(input_path: str) -> str:
    """Convert OGG/Opus or any audio to 16kHz mono WAV via ffmpeg."""
    wav_path = input_path.rsplit(".", 1)[0] + ".wav"
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-f", "wav", wav_path,
        ],
        capture_output=True,
        check=True,
    )
    return wav_path


def _extract_embedding(audio_path: str) -> np.ndarray:
    """Extract a 192-dim L2-normalized embedding from an audio file."""
    waveform, sr = torchaudio.load(audio_path)
    if sr != 16000:
        waveform = torchaudio.functional.resample(waveform, sr, 16000)
    # SpeechBrain expects (batch, time)
    if waveform.dim() == 2 and waveform.shape[0] > 1:
        waveform = waveform.mean(dim=0, keepdim=True)
    embedding = verifier.encode_batch(waveform)  # (1, 1, 192)
    emb_np = embedding.squeeze().cpu().numpy()
    # L2-normalize
    norm = np.linalg.norm(emb_np)
    if norm > 0:
        emb_np = emb_np / norm
    return emb_np


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two L2-normalized vectors."""
    return float(np.dot(a, b))


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model": MODEL_SOURCE,
        "speakers_enrolled": len(voiceprints),
        "threshold": DEFAULT_THRESHOLD,
    }


@app.get("/speakers")
async def list_speakers():
    speakers = []
    for name in sorted(voiceprints.keys()):
        sample_dir = SAMPLES_DIR / name
        sample_count = len(list(sample_dir.glob("*.npz"))) if sample_dir.exists() else 0
        speakers.append({"name": name, "samples": sample_count})
    return {"speakers": speakers}


@app.post("/enroll")
async def enroll(
    file: UploadFile = File(...),
    name: str = Form("arnaldo"),
):
    """Enroll a voice sample. Stores the individual sample embedding and
    recomputes the averaged voiceprint for the speaker."""
    if not file.filename:
        raise HTTPException(400, "No file provided")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Save uploaded file
        ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "ogg"
        input_path = os.path.join(tmpdir, f"input.{ext}")
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Convert to WAV
        try:
            wav_path = _convert_to_wav(input_path)
        except subprocess.CalledProcessError as e:
            raise HTTPException(400, f"ffmpeg conversion failed: {e.stderr.decode()}")

        # Extract embedding
        embedding = _extract_embedding(wav_path)

    # Store individual sample
    sample_dir = SAMPLES_DIR / name
    sample_dir.mkdir(parents=True, exist_ok=True)
    sample_idx = len(list(sample_dir.glob("*.npz")))
    np.savez(sample_dir / f"sample_{sample_idx:03d}.npz", embedding=embedding)

    # Recompute averaged voiceprint from all samples
    all_embeddings = []
    for npz_path in sorted(sample_dir.glob("*.npz")):
        data = np.load(npz_path)
        all_embeddings.append(data["embedding"])

    averaged = np.mean(all_embeddings, axis=0)
    norm = np.linalg.norm(averaged)
    if norm > 0:
        averaged = averaged / norm

    # Store averaged voiceprint
    np.savez(VOICEPRINT_DIR / f"{name}.npz", embedding=averaged)
    voiceprints[name] = averaged

    return {
        "status": "enrolled",
        "speaker": name,
        "total_samples": len(all_embeddings),
        "embedding_dim": int(embedding.shape[0]),
    }


@app.post("/verify")
async def verify(
    file: UploadFile = File(...),
    threshold: float = Form(DEFAULT_THRESHOLD),
):
    """Verify a voice sample against all enrolled speakers."""
    if not voiceprints:
        raise HTTPException(
            400,
            "No speakers enrolled. Use /enroll first.",
        )

    if not file.filename:
        raise HTTPException(400, "No file provided")

    with tempfile.TemporaryDirectory() as tmpdir:
        ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else "ogg"
        input_path = os.path.join(tmpdir, f"input.{ext}")
        with open(input_path, "wb") as f:
            content = await file.read()
            f.write(content)

        try:
            wav_path = _convert_to_wav(input_path)
        except subprocess.CalledProcessError as e:
            raise HTTPException(400, f"ffmpeg conversion failed: {e.stderr.decode()}")

        embedding = _extract_embedding(wav_path)

    # Compare against all enrolled speakers
    best_name = None
    best_score = -1.0
    scores = {}
    for name, vp in voiceprints.items():
        score = _cosine_similarity(embedding, vp)
        scores[name] = round(score, 4)
        if score > best_score:
            best_name = name
            best_score = score

    verified = best_score >= threshold
    return {
        "verified": verified,
        "speaker": best_name if verified else "unknown",
        "confidence": round(best_score, 4),
        "threshold": threshold,
        "scores": scores,
    }


@app.delete("/speakers/{name}")
async def delete_speaker(name: str):
    """Remove a speaker's voiceprint and all samples."""
    vp_path = VOICEPRINT_DIR / f"{name}.npz"
    sample_dir = SAMPLES_DIR / name

    if not vp_path.exists() and not sample_dir.exists():
        raise HTTPException(404, f"Speaker '{name}' not found")

    if vp_path.exists():
        vp_path.unlink()
    if sample_dir.exists():
        shutil.rmtree(sample_dir)
    voiceprints.pop(name, None)

    return {"status": "deleted", "speaker": name}
