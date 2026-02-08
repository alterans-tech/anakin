# Local Learning Implementation Plan

> **Goal**: Make a local Ollama model (qwen3:4b) learn the user's personal preferences, routines, and habits so it can handle those interactions locally instead of going to cloud LLM APIs.
>
> Last updated: 2026-02-08

---

## Table of Contents

1. [System Inventory](#1-system-inventory)
2. [Extracting Training Data from OpenClaw](#2-extracting-training-data-from-openclaw)
3. [Local RAG with nomic-embed-text](#3-local-rag-with-nomic-embed-text)
4. [Fine-tuning qwen3:4b with Unsloth on Free Colab](#4-fine-tuning-qwen34b-with-unsloth-on-free-colab)
5. [Smart Routing Between Local and Cloud](#5-smart-routing-between-local-and-cloud)
6. [End-to-End Architecture](#6-end-to-end-architecture)
7. [Implementation Phases](#7-implementation-phases)

---

## 1. System Inventory

### Hardware
| Component | Value |
|-----------|-------|
| CPU | Intel i7-10510U (4C/8T, 1.8-4.9 GHz) |
| RAM | 16 GB |
| GPU | None (CPU inference only) |
| OS | Ubuntu 24.04 LTS |

### Software Stack
| Component | Location | Notes |
|-----------|----------|-------|
| OpenClaw | `/home/anakin/.npm-global/lib/node_modules/openclaw/` | v2026.2.6-3 |
| OpenClaw config | `~/.openclaw/openclaw.json` | Primary: claude-sonnet-4-5 |
| Ollama | System-installed | Serves qwen3:4b and nomic-embed-text |
| Session logs | `~/.openclaw/agents/main/sessions/*.jsonl` | JSONL format, ~154 user messages total |
| Memory DB | `~/.openclaw/memory/main.sqlite` | SQLite with text-embedding-3-small vectors (1536d) |
| Memory files | `~/.openclaw/workspace/memory/` | Daily markdown journals + project summary |
| Skills | `~/.openclaw/workspace/skills/` | ollama-local, voice-auth, etc. |
| Voice-auth service | `/home/anakin/Workspace/alterans/anakin/configs/voice-auth/` | FastAPI on :8200 (reference pattern) |

### Ollama Models Available
| Model | Purpose | Size |
|-------|---------|------|
| qwen3:4b | Chat/inference | ~2.5 GB |
| nomic-embed-text | Embeddings (768d) | ~274 MB |

---

## 2. Extracting Training Data from OpenClaw

### 2.1 Where Conversations Are Stored

OpenClaw stores conversation history in **JSONL session files**:

```
~/.openclaw/agents/main/sessions/
├── 8778d68e-....jsonl          # 1.8 MB, main active session (218 entries, 30 user / 92 assistant)
├── dd7de134-....jsonl          # 717 KB, older session
├── 70d34b28-....jsonl.old      # 1.1 MB, archived session
├── 70d34b28-....jsonl.bak-...  # 410 KB, backup
├── fd48a34f-....jsonl          # 7.5 KB, small session (sub-agent)
└── sessions.json               # Session metadata/routing
```

**Current data volume**: ~154 user messages, ~759 assistant messages across all sessions.

### 2.2 Session JSONL Format

Each line is a JSON object. The key types are:

```jsonl
{"type":"session","version":3,"id":"...","timestamp":"..."}
{"type":"model_change","provider":"anthropic","modelId":"claude-sonnet-4-5",...}
{"type":"message","id":"...","message":{"role":"user","content":[{"type":"text","text":"..."}]}}
{"type":"message","id":"...","message":{"role":"assistant","content":[{"type":"thinking","thinking":"..."},{"type":"text","text":"..."}],"model":"claude-sonnet-4-5","usage":{...}}}
```

User messages arrive in this format:
```
[Telegram Arnaldo Silva id:7656768218 2026-02-07 21:06 GMT-3] Ping
[message_id: 237]
```

Assistant messages contain an array of content blocks:
- `{"type":"thinking","thinking":"..."}` -- internal reasoning (strip for training)
- `{"type":"text","text":"..."}` -- actual response text
- `{"type":"toolCall","name":"...","arguments":{...}}` -- tool invocations
- `{"type":"toolResult","toolCallId":"...","output":"..."}` -- tool outputs

### 2.3 Memory Database (SQLite)

```
~/.openclaw/memory/main.sqlite
```

Tables:
| Table | Rows | Content |
|-------|------|---------|
| `files` | 4 | Memory file paths (daily journals, project-summary.md) |
| `chunks` | 10 | Text chunks with text-embedding-3-small embeddings (1536d) |
| `embedding_cache` | 10 | Cached embeddings by hash |
| `chunks_fts` | -- | Full-text search index |
| `chunks_vec` | -- | Vector search index |

The memory files (in `~/.openclaw/workspace/memory/`) contain:
- `2026-02-05.md` -- Day One journal
- `2026-02-07.md` -- First contact log
- `2026-02-08.md` -- Status check notes
- `project-summary.md` -- Comprehensive summary of the project

### 2.4 Extraction Script

Create `/home/anakin/Workspace/alterans/anakin/scripts/extract-training-data.py`:

```python
#!/usr/bin/env python3
"""
Extract Q&A pairs from OpenClaw session logs for fine-tuning.

Usage:
    python3 scripts/extract-training-data.py
    python3 scripts/extract-training-data.py --filter-preferences
    python3 scripts/extract-training-data.py --output training_data.jsonl
"""

import json
import glob
import re
import argparse
from pathlib import Path

SESSION_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"

def extract_text_from_content(content):
    """Extract plain text from message content (string or array)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block["text"])
        return "\n".join(texts).strip()
    return ""

def strip_telegram_envelope(text):
    """Remove Telegram metadata wrapper from user messages."""
    # Pattern: [Telegram Name id:123 timestamp] actual message\n[message_id: N]
    match = re.match(
        r'\[Telegram\s+.*?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*(.*)',
        text, re.DOTALL
    )
    if match:
        msg = match.group(1).strip()
        # Remove trailing [message_id: N]
        msg = re.sub(r'\n?\[message_id:\s*\d+\]$', '', msg).strip()
        return msg
    # Also strip System: prefixed messages
    if text.startswith("System:"):
        return ""
    return text.strip()

def is_preference_related(user_text, assistant_text):
    """Check if the exchange involves preferences, routines, or personal info."""
    combined = (user_text + " " + assistant_text).lower()
    preference_keywords = [
        "i like", "i prefer", "i want", "i need", "i usually",
        "i always", "i never", "my favorite", "i enjoy", "i hate",
        "my routine", "every morning", "every day", "every night",
        "wake up", "go to bed", "schedule", "remind me",
        "my name", "i live", "i work", "i'm from",
        "call me", "don't call me", "i go by",
        "set temperature", "turn on", "turn off",
        "good morning", "good night", "bom dia", "boa noite",
    ]
    return any(kw in combined for kw in preference_keywords)

def extract_pairs_from_session(session_file):
    """Extract user->assistant pairs from a session JSONL file."""
    messages = []
    with open(session_file) as f:
        for line in f:
            try:
                obj = json.loads(line)
                if obj.get("type") == "message":
                    messages.append(obj)
            except json.JSONDecodeError:
                continue

    pairs = []
    i = 0
    while i < len(messages) - 1:
        msg = messages[i]
        if msg.get("message", {}).get("role") != "user":
            i += 1
            continue

        # Find the next assistant message (may skip tool calls)
        j = i + 1
        assistant_text_parts = []
        while j < len(messages):
            next_msg = messages[j]
            role = next_msg.get("message", {}).get("role", "")
            if role == "assistant":
                text = extract_text_from_content(next_msg["message"]["content"])
                if text:
                    assistant_text_parts.append(text)
                j += 1
                # Keep collecting assistant messages until next user message
                while j < len(messages) and messages[j].get("message", {}).get("role") != "user":
                    if messages[j].get("message", {}).get("role") == "assistant":
                        t = extract_text_from_content(messages[j]["message"]["content"])
                        if t:
                            assistant_text_parts.append(t)
                    j += 1
                break
            elif role == "user":
                break
            j += 1

        user_text = strip_telegram_envelope(
            extract_text_from_content(msg["message"]["content"])
        )
        assistant_text = "\n".join(assistant_text_parts)

        if user_text and assistant_text and len(user_text) > 2:
            # Skip system/error messages
            if not user_text.startswith("System:"):
                pairs.append({
                    "user": user_text,
                    "assistant": assistant_text,
                    "timestamp": msg.get("timestamp", ""),
                    "model": messages[i+1].get("message", {}).get("model", "unknown")
                        if i+1 < len(messages) else "unknown"
                })

        i = j if j > i else i + 1

    return pairs

def format_for_training(pairs, system_prompt=None):
    """Convert pairs to Unsloth/ChatML training format."""
    if system_prompt is None:
        system_prompt = (
            "You are Anakin, a personal AI assistant for Arnaldo. "
            "You know his preferences, routines, and habits. "
            "Be concise, friendly, and helpful. Skip filler words."
        )

    training_data = []
    for pair in pairs:
        conversations = [
            {"from": "system", "value": system_prompt},
            {"from": "human", "value": pair["user"]},
            {"from": "gpt", "value": pair["assistant"]},
        ]
        training_data.append({"conversations": conversations})

    return training_data

def load_memory_as_context():
    """Load memory markdown files as additional training context."""
    context_pairs = []
    for md_file in MEMORY_DIR.glob("*.md"):
        content = md_file.read_text()
        # Create Q&A pairs from memory content
        if "project-summary" in md_file.name:
            context_pairs.append({
                "user": "What's the current status of the Anakin project?",
                "assistant": content[:2000],
                "timestamp": "",
                "model": "memory"
            })
        elif re.match(r'\d{4}-\d{2}-\d{2}', md_file.stem):
            context_pairs.append({
                "user": f"What happened on {md_file.stem}?",
                "assistant": content[:1500],
                "timestamp": "",
                "model": "memory"
            })
    return context_pairs

def main():
    parser = argparse.ArgumentParser(description="Extract training data from OpenClaw logs")
    parser.add_argument("--output", "-o", default="training_data.jsonl",
                        help="Output JSONL file")
    parser.add_argument("--filter-preferences", action="store_true",
                        help="Only include preference-related exchanges")
    parser.add_argument("--include-memory", action="store_true",
                        help="Include memory files as training context")
    parser.add_argument("--min-assistant-length", type=int, default=10,
                        help="Minimum assistant response length in chars")
    parser.add_argument("--stats-only", action="store_true",
                        help="Only print statistics, don't write file")
    args = parser.parse_args()

    all_pairs = []
    session_files = list(SESSION_DIR.glob("*.jsonl")) + list(SESSION_DIR.glob("*.jsonl.old"))

    for sf in session_files:
        pairs = extract_pairs_from_session(sf)
        all_pairs.extend(pairs)

    # Filter
    if args.filter_preferences:
        all_pairs = [p for p in all_pairs if is_preference_related(p["user"], p["assistant"])]

    # Filter short responses
    all_pairs = [p for p in all_pairs if len(p["assistant"]) >= args.min_assistant_length]

    # Add memory context
    if args.include_memory:
        memory_pairs = load_memory_as_context()
        all_pairs.extend(memory_pairs)

    # Stats
    print(f"Total Q&A pairs extracted: {len(all_pairs)}")
    print(f"Preference-related: {sum(1 for p in all_pairs if is_preference_related(p['user'], p['assistant']))}")
    print(f"Average user message length: {sum(len(p['user']) for p in all_pairs) / max(len(all_pairs), 1):.0f} chars")
    print(f"Average assistant response length: {sum(len(p['assistant']) for p in all_pairs) / max(len(all_pairs), 1):.0f} chars")

    if args.stats_only:
        return

    # Format for training
    training_data = format_for_training(all_pairs)

    # Write JSONL
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Written {len(training_data)} training samples to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")

if __name__ == "__main__":
    main()
```

### 2.5 Training Data Format

The Unsloth Qwen3 notebook expects data in the `conversations` format (ShareGPT-like):

```jsonl
{"conversations":[{"from":"system","value":"You are Anakin..."},{"from":"human","value":"What's the weather like?"},{"from":"gpt","value":"Currently in Curitiba..."}]}
{"conversations":[{"from":"system","value":"You are Anakin..."},{"from":"human","value":"Turn on the lights"},{"from":"gpt","value":"I've turned on the living room lights."}]}
```

### 2.6 Data Volume Assessment

**Current state**: ~154 user messages is well below the recommended minimum of 200-500 samples for effective QLoRA fine-tuning.

**Recommendation**: Use RAG (Section 3) as the primary approach NOW, and accumulate data over 2-4 weeks of usage before attempting fine-tuning. The extraction script should be run weekly to track data growth.

**Data augmentation strategies** to reach the 500+ sample threshold:
1. Include memory file content as synthetic Q&A pairs
2. Create manual preference pairs from known facts about Arnaldo
3. Paraphrase existing exchanges using Claude to generate variations
4. Log new conversations continuously with the extraction script

---

## 3. Local RAG with nomic-embed-text

### 3.1 Vector Store Choice: ChromaDB

**Decision**: ChromaDB over LanceDB or SQLite-VSS.

| Factor | ChromaDB | LanceDB | SQLite-VSS |
|--------|----------|---------|------------|
| Python API simplicity | Excellent | Good | Basic |
| pip install | `pip install chromadb` | `pip install lancedb` | Needs C ext |
| Persistent storage | Built-in | Built-in | Manual |
| Ollama embedding support | Native | Via custom fn | Manual |
| Active community | Large | Growing | Small |
| RAM at rest | ~50 MB | ~30 MB | ~20 MB |

ChromaDB wins on developer speed and community support. For a single-user system with <100K documents, performance differences are irrelevant.

### 3.2 Architecture: FastAPI RAG Microservice

Following the same pattern as the voice-auth service (`/home/anakin/Workspace/alterans/anakin/configs/voice-auth/speaker_service.py`), create a FastAPI service on port **8300**.

Service location: `/home/anakin/Workspace/alterans/anakin/configs/personal-rag/`

```
configs/personal-rag/
├── rag_service.py          # FastAPI application
├── ingest.py               # Data ingestion utilities
├── requirements.txt        # Dependencies
└── .venv/                  # Virtual environment
```

### 3.3 RAG Service Implementation

Create `/home/anakin/Workspace/alterans/anakin/configs/personal-rag/requirements.txt`:
```
fastapi>=0.115.0
uvicorn>=0.34.0
chromadb>=0.6.0
httpx>=0.28.0
```

Create `/home/anakin/Workspace/alterans/anakin/configs/personal-rag/rag_service.py`:

```python
#!/usr/bin/env python3
"""
Personal Knowledge RAG Service

FastAPI microservice that:
1. Indexes OpenClaw memory/conversations into ChromaDB
2. Embeds queries using Ollama nomic-embed-text (768d, fully local)
3. Retrieves relevant personal context
4. Queries qwen3:4b with augmented context
5. Returns answers grounded in personal knowledge

Endpoints:
    POST /query     - RAG query (search + generate)
    POST /search    - Search only (return relevant chunks)
    POST /ingest    - Ingest new documents
    POST /sync      - Re-sync from OpenClaw memory/sessions
    GET  /stats     - Collection statistics
    GET  /health    - Health check
"""

import json
import logging
import os
import re
from pathlib import Path
from typing import Optional

import chromadb
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("personal-rag")

# --- Configuration ---
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.environ.get("CHAT_MODEL", "qwen3:4b")
CHROMA_DIR = Path.home() / ".openclaw" / "personal-rag" / "chromadb"
MEMORY_DIR = Path.home() / ".openclaw" / "workspace" / "memory"
SESSION_DIR = Path.home() / ".openclaw" / "agents" / "main" / "sessions"
TOP_K = int(os.environ.get("RAG_TOP_K", "5"))

# --- Startup ---
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))

app = FastAPI(title="Personal RAG", version="1.0.0")
http_client = httpx.Client(timeout=120.0)


def get_collection():
    """Get or create the personal knowledge collection."""
    return chroma_client.get_or_create_collection(
        name="personal_knowledge",
        metadata={"hnsw:space": "cosine"}
    )


def ollama_embed(texts: list[str]) -> list[list[float]]:
    """Get embeddings from Ollama nomic-embed-text."""
    embeddings = []
    for text in texts:
        resp = http_client.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text}
        )
        resp.raise_for_status()
        embeddings.append(resp.json()["embedding"])
    return embeddings


def ollama_chat(messages: list[dict], temperature: float = 0.3) -> str:
    """Chat with local Ollama model."""
    resp = http_client.post(
        f"{OLLAMA_HOST}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": 4096,  # Keep context small for 4B model
            }
        }
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


# --- Request/Response Models ---

class QueryRequest(BaseModel):
    query: str
    top_k: int = TOP_K
    temperature: float = 0.3
    system_prompt: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    top_k: int = TOP_K

class IngestRequest(BaseModel):
    documents: list[str]
    metadatas: Optional[list[dict]] = None
    ids: Optional[list[str]] = None

class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    model: str

class SearchResponse(BaseModel):
    results: list[dict]
    count: int


# --- Endpoints ---

@app.get("/health")
def health():
    """Health check."""
    try:
        # Check Ollama
        resp = http_client.get(f"{OLLAMA_HOST}/api/tags")
        ollama_ok = resp.status_code == 200
    except Exception:
        ollama_ok = False

    collection = get_collection()
    return {
        "status": "ok" if ollama_ok else "degraded",
        "ollama": ollama_ok,
        "embed_model": EMBED_MODEL,
        "chat_model": CHAT_MODEL,
        "documents": collection.count(),
    }


@app.get("/stats")
def stats():
    """Collection statistics."""
    collection = get_collection()
    return {
        "total_documents": collection.count(),
        "collection_name": collection.name,
        "chroma_dir": str(CHROMA_DIR),
    }


@app.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    """Search for relevant personal knowledge chunks."""
    collection = get_collection()
    if collection.count() == 0:
        return SearchResponse(results=[], count=0)

    query_embedding = ollama_embed([req.query])[0]
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=min(req.top_k, collection.count()),
    )

    formatted = []
    for i in range(len(results["ids"][0])):
        formatted.append({
            "id": results["ids"][0][i],
            "text": results["documents"][0][i],
            "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
            "distance": results["distances"][0][i] if results["distances"] else None,
        })

    return SearchResponse(results=formatted, count=len(formatted))


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    """RAG query: search context + generate answer with local model."""
    collection = get_collection()

    # Step 1: Retrieve relevant context
    context_chunks = []
    if collection.count() > 0:
        query_embedding = ollama_embed([req.query])[0]
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(req.top_k, collection.count()),
        )
        for i in range(len(results["ids"][0])):
            dist = results["distances"][0][i] if results["distances"] else 1.0
            if dist < 0.8:  # Only include reasonably relevant chunks
                context_chunks.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": dist,
                })

    # Step 2: Build prompt with context
    system = req.system_prompt or (
        "You are Anakin, a personal AI assistant for Arnaldo. "
        "Answer based on the personal knowledge context provided. "
        "If the context doesn't contain the answer, say so honestly. "
        "Be concise and direct."
    )

    context_text = ""
    if context_chunks:
        context_text = "\n\n---\n\n".join(
            f"[Source: {c['metadata'].get('source', 'unknown')}]\n{c['text']}"
            for c in context_chunks
        )
        system += f"\n\n## Personal Knowledge Context\n\n{context_text}"

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": req.query},
    ]

    # Step 3: Generate answer
    answer = ollama_chat(messages, temperature=req.temperature)

    return QueryResponse(
        answer=answer,
        sources=[{"text": c["text"][:200], "distance": c["distance"]} for c in context_chunks],
        model=CHAT_MODEL,
    )


@app.post("/ingest")
def ingest(req: IngestRequest):
    """Ingest documents into the vector store."""
    if not req.documents:
        raise HTTPException(status_code=400, detail="No documents provided")

    collection = get_collection()
    ids = req.ids or [f"doc_{collection.count() + i}" for i in range(len(req.documents))]
    metadatas = req.metadatas or [{"source": "manual"} for _ in req.documents]

    embeddings = ollama_embed(req.documents)
    collection.add(
        ids=ids,
        documents=req.documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return {"ingested": len(req.documents), "total": collection.count()}


@app.post("/sync")
def sync():
    """Re-sync from OpenClaw memory files and session logs."""
    collection = get_collection()
    ingested = 0

    # 1. Ingest memory markdown files
    for md_file in MEMORY_DIR.glob("*.md"):
        content = md_file.read_text()
        # Chunk by sections (## headers)
        sections = re.split(r'\n(?=## )', content)
        for j, section in enumerate(sections):
            section = section.strip()
            if len(section) < 50:
                continue
            # Chunk large sections further (~400 tokens ~ 1600 chars)
            if len(section) > 1600:
                chunks = [section[i:i+1600] for i in range(0, len(section), 1200)]
            else:
                chunks = [section]

            for k, chunk in enumerate(chunks):
                doc_id = f"memory_{md_file.stem}_{j}_{k}"
                embedding = ollama_embed([chunk])[0]
                collection.upsert(
                    ids=[doc_id],
                    documents=[chunk],
                    embeddings=[embedding],
                    metadatas=[{"source": f"memory/{md_file.name}", "type": "memory"}],
                )
                ingested += 1

    # 2. Ingest session conversation pairs
    for sf in list(SESSION_DIR.glob("*.jsonl")) + list(SESSION_DIR.glob("*.jsonl.old")):
        messages = []
        with open(sf) as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    if obj.get("type") == "message":
                        messages.append(obj)
                except json.JSONDecodeError:
                    continue

        for i in range(len(messages) - 1):
            if messages[i].get("message", {}).get("role") != "user":
                continue
            if messages[i+1].get("message", {}).get("role") != "assistant":
                continue

            user_content = messages[i]["message"]["content"]
            asst_content = messages[i+1]["message"]["content"]

            # Extract text
            user_text = ""
            if isinstance(user_content, list):
                for c in user_content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        user_text = c["text"]
                        break
            elif isinstance(user_content, str):
                user_text = user_content

            asst_text = ""
            if isinstance(asst_content, list):
                for c in asst_content:
                    if isinstance(c, dict) and c.get("type") == "text":
                        asst_text = c["text"]
                        break
            elif isinstance(asst_content, str):
                asst_text = asst_content

            if len(user_text) < 5 or len(asst_text) < 10:
                continue

            # Strip Telegram envelope
            clean_user = re.sub(
                r'\[Telegram\s+.*?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*',
                '', user_text
            )
            clean_user = re.sub(r'\n?\[message_id:\s*\d+\]$', '', clean_user).strip()

            if not clean_user:
                continue

            combined = f"User: {clean_user}\nAssistant: {asst_text[:500]}"
            doc_id = f"session_{sf.stem}_{i}"
            embedding = ollama_embed([combined])[0]
            collection.upsert(
                ids=[doc_id],
                documents=[combined],
                embeddings=[embedding],
                metadatas=[{
                    "source": f"session/{sf.name}",
                    "type": "conversation",
                    "timestamp": messages[i].get("timestamp", ""),
                }],
            )
            ingested += 1

    return {"synced": ingested, "total": collection.count()}
```

### 3.4 Setup Commands

```bash
# Create directory
mkdir -p /home/anakin/Workspace/alterans/anakin/configs/personal-rag

# Create virtual environment
cd /home/anakin/Workspace/alterans/anakin/configs/personal-rag
python3 -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn chromadb httpx

# Test run
python3 -m uvicorn rag_service:app --host 127.0.0.1 --port 8300

# Initial sync
curl -s -X POST http://localhost:8300/sync | python3 -m json.tool

# Test query
curl -s -X POST http://localhost:8300/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is Arnaldo working on?"}' | python3 -m json.tool
```

### 3.5 Systemd Service

Create `~/.config/systemd/user/personal-rag.service`:

```ini
[Unit]
Description=Personal RAG Service (ChromaDB + Ollama nomic-embed-text + qwen3:4b)
After=network-online.target

[Service]
Type=simple
WorkingDirectory=/home/anakin/Workspace/alterans/anakin/configs/personal-rag
ExecStart=/home/anakin/Workspace/alterans/anakin/configs/personal-rag/.venv/bin/python -m uvicorn rag_service:app --host 127.0.0.1 --port 8300
Restart=on-failure
RestartSec=5
Environment=OLLAMA_HOST=http://localhost:11434
Environment=EMBED_MODEL=nomic-embed-text
Environment=CHAT_MODEL=qwen3:4b
Environment=RAG_TOP_K=5

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now personal-rag.service
```

### 3.6 Keeping RAG Updated

The `/sync` endpoint re-ingests everything (upsert prevents duplicates). Set up a cron job or OpenClaw cron to sync daily:

```bash
# Add to crontab (crontab -e)
0 4 * * * curl -s -X POST http://localhost:8300/sync > /dev/null 2>&1
```

Or have OpenClaw call it via its cron system (in `~/.openclaw/cron/`).

---

## 4. Fine-tuning qwen3:4b with Unsloth on Free Colab

### 4.1 Prerequisites

- Google account with Colab access (free tier gives T4 GPU)
- Training data in JSONL format (from Section 2)
- Minimum 200-500 Q&A pairs (recommended 500+)
- HuggingFace account (free, for model hosting)

### 4.2 Training Data Format

The Unsloth Qwen3 notebook expects the `conversations` format:

```jsonl
{"conversations":[{"from":"system","value":"You are Anakin, a personal AI assistant."},{"from":"human","value":"Good morning!"},{"from":"gpt","value":"Morning, Arnaldo! Ready when you are."}]}
```

The extraction script from Section 2.4 produces this format. Upload the resulting `training_data.jsonl` to Google Drive or HuggingFace.

### 4.3 Colab Notebook (Step-by-Step)

Use this notebook as the base:
**Qwen3 (4B) Instruct**: https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-Instruct.ipynb

Key modifications for personal fine-tuning:

**Cell 1 -- Install** (no changes needed):
```python
%%capture
import os, re
if "COLAB_" not in "".join(os.environ.keys()):
    !pip install unsloth
else:
    import torch; v = re.match(r'[\d]{1,}\.[\d]{1,}', str(torch.__version__)).group(0)
    xformers = 'xformers==' + {'2.10':'0.0.34','2.9':'0.0.33.post1','2.8':'0.0.32.post2'}.get(v, "0.0.34")
    !pip install sentencepiece protobuf "datasets==4.3.0" "huggingface_hub>=0.34.0" hf_transfer
    !pip install --no-deps unsloth_zoo bitsandbytes accelerate {xformers} peft trl triton unsloth
!pip install transformers==4.56.2
!pip install --no-deps trl==0.22.2
```

**Cell 2 -- Load model** (use 4B Instruct):
```python
from unsloth import FastLanguageModel
import torch

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name = "unsloth/Qwen3-4B-Instruct-2507",
    max_seq_length = 2048,
    load_in_4bit = True,
    load_in_8bit = False,
    full_finetuning = False,
)
```

**Cell 3 -- LoRA config** (rank 32, all linear layers):
```python
model = FastLanguageModel.get_peft_model(
    model,
    r = 32,
    target_modules = [
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
    ],
    lora_alpha = 32,
    lora_dropout = 0,
    bias = "none",
    use_gradient_checkpointing = "unsloth",
    random_state = 3407,
    use_rslora = False,
    loftq_config = None,
)
```

**Cell 4 -- Chat template**:
```python
from unsloth.chat_templates import get_chat_template
tokenizer = get_chat_template(
    tokenizer,
    chat_template = "qwen3-instruct",
)
```

**Cell 5 -- Load YOUR dataset** (upload training_data.jsonl first):
```python
from datasets import load_dataset

# Option A: From uploaded file
dataset = load_dataset("json", data_files="/content/training_data.jsonl", split="train")

# Option B: From HuggingFace (if you pushed it)
# dataset = load_dataset("YOUR_USERNAME/anakin-training-data", split="train")
```

**Cell 6 -- Standardize format**:
```python
from unsloth.chat_templates import standardize_data_formats
dataset = standardize_data_formats(dataset)
```

**Cell 7 -- Apply chat template**:
```python
def formatting_prompts_func(examples):
    convos = examples["conversations"]
    texts = [
        tokenizer.apply_chat_template(
            convo, tokenize=False, add_generation_prompt=False
        )
        for convo in convos
    ]
    return {"text": texts}

dataset = dataset.map(formatting_prompts_func, batched=True)
```

**Cell 8 -- Training config** (adjusted for small personal dataset):
```python
from trl import SFTTrainer, SFTConfig

trainer = SFTTrainer(
    model = model,
    tokenizer = tokenizer,
    train_dataset = dataset,
    eval_dataset = None,
    args = SFTConfig(
        dataset_text_field = "text",
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        # For small datasets (<500 samples), use num_train_epochs instead of max_steps
        num_train_epochs = 3,         # 3 epochs over your data
        # max_steps = 60,             # Use this for larger datasets
        learning_rate = 2e-4,
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.001,
        lr_scheduler_type = "linear",
        seed = 3407,
        report_to = "none",
    ),
)
```

**Cell 9 -- Response-only training** (critical: only train on assistant outputs):
```python
from unsloth.chat_templates import train_on_responses_only
trainer = train_on_responses_only(
    trainer,
    instruction_part = "<|im_start|>user\n",
    response_part = "<|im_start|>assistant\n",
)
```

**Cell 10 -- Train**:
```python
trainer_stats = trainer.train()
```

**Cell 11 -- Export to GGUF** (for Ollama deployment):
```python
# Save as Q8_0 quantization (good balance of quality/size)
model.save_pretrained_gguf(
    "anakin-qwen3-4b",
    tokenizer,
    quantization_method = "q8_0"
)

# Also save q4_k_m for a smaller option
model.save_pretrained_gguf(
    "anakin-qwen3-4b-q4",
    tokenizer,
    quantization_method = "q4_k_m"
)
```

**Cell 12 -- Download the GGUF + Modelfile**:
```python
# The GGUF file and Modelfile will be in the output directory
!ls -la anakin-qwen3-4b/
!cat anakin-qwen3-4b/Modelfile
```

Download `anakin-qwen3-4b/unsloth.Q8_0.gguf` and `anakin-qwen3-4b/Modelfile` from Colab.

### 4.4 Deploy to Ollama

```bash
# Copy files to local machine
mkdir -p ~/models/anakin-qwen3

# After downloading from Colab:
# mv ~/Downloads/unsloth.Q8_0.gguf ~/models/anakin-qwen3/
# mv ~/Downloads/Modelfile ~/models/anakin-qwen3/

# Create the Ollama model
cd ~/models/anakin-qwen3
ollama create anakin-qwen3:latest -f Modelfile

# Test it
ollama run anakin-qwen3:latest "Good morning! What should I do today?"

# Verify it's listed
ollama list
```

### 4.5 What Gets Baked In vs What Needs RAG

| Aspect | Fine-tuning bakes in | RAG provides dynamically |
|--------|---------------------|--------------------------|
| Response style/tone | Yes | No |
| Personality traits | Yes | No |
| Common greetings | Yes | No |
| User's name/identity | Yes | Also yes |
| Current preferences | Snapshot at training time | Always up-to-date |
| Today's schedule | No | Yes |
| Recent conversations | No | Yes |
| New routines | No (needs retrain) | Yes (auto-synced) |

**Recommendation**: Fine-tuning teaches the model HOW to respond (style, personality). RAG teaches it WHAT to respond about (current facts, preferences). Use both together.

### 4.6 Retraining Schedule

Re-fine-tune monthly or when you've accumulated 200+ new conversation pairs. The extraction script tracks this automatically.

---

## 5. Smart Routing Between Local and Cloud

### 5.1 OpenClaw Plugin Hook System (the key discovery)

OpenClaw has a full lifecycle hook system in its plugin SDK. The critical hooks for routing are:

```typescript
type PluginHookName =
    | "before_agent_start"    // Can modify system prompt, prepend context
    | "message_received"      // Fires when a message arrives
    | "message_sending"       // Can modify outgoing messages, or cancel
    | "before_tool_call"      // Can block tool calls
    | "after_tool_call"       // Post-processing
    // ... and more
```

The `before_agent_start` hook is especially powerful:
```typescript
type PluginHookBeforeAgentStartEvent = {
    prompt: string;           // The system prompt
    messages?: unknown[];     // Conversation messages
};

type PluginHookBeforeAgentStartResult = {
    systemPrompt?: string;    // Can REPLACE the system prompt
    prependContext?: string;  // Can PREPEND context to the prompt
};
```

And `message_received` gives access to inbound messages:
```typescript
type PluginHookMessageReceivedEvent = {
    from: string;
    content: string;
    timestamp?: number;
    metadata?: Record<string, unknown>;
};
```

### 5.2 Routing Strategy: Skill-Based Approach (Recommended)

Rather than trying to intercept and reroute at the plugin/hook level (which would require modifying OpenClaw's model selection internals), use the **existing skill + tool infrastructure**.

**How it works**:

1. Create an OpenClaw skill called `personal-knowledge` that is marked `always: true`
2. The skill instructs the cloud LLM: "For personal/routine questions, call the `personal_rag_query` tool instead of answering yourself"
3. The tool calls the local RAG service (port 8300), which uses local embeddings + local qwen3:4b
4. The cloud LLM relays the local model's answer (or augments it)

This is the **simplest, most reliable approach** because:
- No plugin code to write/compile/debug
- Works within OpenClaw's existing architecture
- The cloud LLM acts as an intelligent router naturally
- Falls back gracefully (cloud answers if local can't)

### 5.3 Implementation: Personal Knowledge Skill

Create `/home/anakin/.openclaw/workspace/skills/personal-knowledge/SKILL.md`:

```markdown
---
name: personal-knowledge
description: Query personal knowledge base for Arnaldo's preferences, routines, habits, and personal information. Use this before answering personal questions from memory.
always: true
---

# Personal Knowledge

You have access to a local personal knowledge base that stores Arnaldo's preferences, routines, habits, and conversation history. This runs entirely locally (no cloud API calls).

## When to Use This

**ALWAYS query the personal knowledge base FIRST for these types of questions:**

- Personal preferences ("What's my favorite...?", "Do I like...?")
- Routines ("What time do I usually...?", "What's my morning routine?")
- Personal history ("When did I...?", "What happened on...?")
- Project context ("What am I working on?", "What's the status of...?")
- Habits and patterns ("How often do I...?", "Do I normally...?")
- Greetings and casual check-ins (good morning, how are you, etc.)

**Do NOT use for:**

- Complex reasoning, coding, or analysis (use your own capabilities)
- Real-time information (weather, news, prices)
- Tool-based operations (file operations, web search, smart home)
- Tasks requiring your full context window

## How to Query

```bash
curl -s -X POST http://localhost:8300/query \
  -H "Content-Type: application/json" \
  -d '{"query": "USER_QUESTION_HERE", "top_k": 5}'
```

The response contains:
```json
{
  "answer": "The locally-generated answer based on personal knowledge",
  "sources": [{"text": "relevant chunk...", "distance": 0.23}],
  "model": "qwen3:4b"
}
```

## How to Respond

1. If the local answer is relevant and sufficient, **use it directly** (you may rephrase for better flow)
2. If the local answer is partial, **augment it** with your own knowledge
3. If the local answer says "I don't have information about that", **answer normally** using your capabilities
4. For greetings/casual chat, prefer the local answer's style (it's been trained on Arnaldo's conversational patterns)

## Search Only (without generation)

For just checking what personal knowledge exists:

```bash
curl -s -X POST http://localhost:8300/search \
  -H "Content-Type: application/json" \
  -d '{"query": "USER_QUESTION_HERE", "top_k": 5}'
```

## Sync Knowledge Base

To update the knowledge base with recent conversations:

```bash
curl -s -X POST http://localhost:8300/sync
```

Run this periodically or when the user mentions their knowledge base seems outdated.
```

Create `/home/anakin/.openclaw/workspace/skills/personal-knowledge/_meta.json`:

```json
{
  "name": "personal-knowledge",
  "version": "1.0.0",
  "description": "Local personal knowledge RAG system"
}
```

### 5.4 Advanced: OpenClaw Plugin for Automatic RAG Context Injection

For a more automated approach (no cloud LLM decision-making overhead), create a plugin that uses the `before_agent_start` hook to automatically prepend relevant personal context.

This runs as a plugin in `~/.openclaw/workspace/extensions/`:

Create `~/.openclaw/workspace/extensions/personal-context/index.ts`:

```typescript
import type { OpenClawPluginApi } from "openclaw/plugin-sdk";

/**
 * Personal Context Plugin
 *
 * Automatically searches the local RAG service for relevant personal
 * context and prepends it to the system prompt before every agent run.
 * This way, the LLM always has relevant personal knowledge available
 * without needing to make tool calls.
 */
const personalContextPlugin = {
  id: "personal-context",
  name: "Personal Context Injection",
  description: "Injects relevant personal knowledge into every conversation",

  register(api: OpenClawPluginApi) {
    api.on("before_agent_start", async (event, ctx) => {
      try {
        // Extract the latest user message from the event
        const messages = event.messages as Array<{ role: string; content: unknown }> | undefined;
        if (!messages || messages.length === 0) return;

        const lastUserMsg = [...messages]
          .reverse()
          .find((m) => m.role === "user");
        if (!lastUserMsg) return;

        let queryText = "";
        if (typeof lastUserMsg.content === "string") {
          queryText = lastUserMsg.content;
        } else if (Array.isArray(lastUserMsg.content)) {
          for (const block of lastUserMsg.content) {
            if (typeof block === "object" && block !== null && "type" in block) {
              const b = block as { type: string; text?: string };
              if (b.type === "text" && b.text) {
                queryText = b.text;
                break;
              }
            }
          }
        }

        if (queryText.length < 3) return;

        // Strip Telegram envelope
        const cleaned = queryText
          .replace(/\[Telegram\s+.*?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*/g, "")
          .replace(/\n?\[message_id:\s*\d+\]$/g, "")
          .trim();

        if (cleaned.length < 3) return;

        // Query the local RAG service
        const resp = await fetch("http://localhost:8300/search", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: cleaned, top_k: 3 }),
        });

        if (!resp.ok) return;

        const data = (await resp.json()) as {
          results: Array<{ text: string; distance: number }>;
          count: number;
        };

        if (data.count === 0) return;

        // Only include results with reasonable relevance (cosine distance < 0.6)
        const relevant = data.results.filter((r) => r.distance < 0.6);
        if (relevant.length === 0) return;

        const contextBlock = relevant
          .map((r) => r.text)
          .join("\n---\n");

        return {
          prependContext: `\n<personal_context>\n${contextBlock}\n</personal_context>\n`,
        };
      } catch (err) {
        api.logger.warn?.(`Personal context fetch failed: ${err}`);
        // Fail silently - don't break the main agent
      }
    });
  },
};

export default personalContextPlugin;
```

Create `~/.openclaw/workspace/extensions/personal-context/package.json`:

```json
{
  "name": "openclaw-personal-context",
  "version": "1.0.0",
  "type": "module",
  "openclaw.extensions": ["index.ts"]
}
```

**Important**: This plugin approach requires TypeScript compilation. If OpenClaw supports loading `.ts` extensions directly (via tsx), this works as-is. Otherwise, compile to JS first.

### 5.5 Intent Classification for Direct Local Routing

For the most aggressive cost-saving approach, use the local model itself as a classifier. Add a classification endpoint to the RAG service:

Add to `rag_service.py`:

```python
CLASSIFIER_SYSTEM = """You are a message classifier. Classify the user's message into one of these categories:
- PERSONAL: questions about preferences, routines, habits, personal info, greetings, casual chat
- COMPLEX: requires reasoning, coding, analysis, tool use, web search, or real-time information

Respond with ONLY the category name, nothing else."""

class ClassifyRequest(BaseModel):
    message: str

class ClassifyResponse(BaseModel):
    category: str  # "PERSONAL" or "COMPLEX"
    confidence: str  # "high" or "low"

@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    """Classify whether a message needs cloud or can be handled locally."""
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM},
        {"role": "user", "content": req.message},
    ]

    result = ollama_chat(messages, temperature=0.1)
    category = "PERSONAL" if "PERSONAL" in result.upper() else "COMPLEX"

    # Also check keyword heuristics for higher confidence
    personal_keywords = [
        "good morning", "good night", "bom dia", "boa noite",
        "how are you", "what's up", "hi ", "hello", "hey",
        "i like", "i prefer", "my favorite", "remind me",
        "what time", "my routine", "my schedule",
    ]
    msg_lower = req.message.lower()
    keyword_match = any(kw in msg_lower for kw in personal_keywords)

    if keyword_match and category == "PERSONAL":
        confidence = "high"
    elif not keyword_match and category == "COMPLEX":
        confidence = "high"
    else:
        confidence = "low"

    return ClassifyResponse(category=category, confidence=confidence)
```

### 5.6 Why NOT LiteLLM Proxy

LiteLLM's routing is designed for load-balancing between equivalent providers, not for intent-based routing to fundamentally different models. It lacks:
- Message content analysis
- Per-request model selection based on query semantics
- Integration with local RAG context

The skill-based approach (5.3) or plugin approach (5.4) integrates natively with OpenClaw and is simpler.

---

## 6. End-to-End Architecture

### 6.1 Architecture Diagram

```
                          +-----------------------+
                          |    User (Telegram)    |
                          +----------+------------+
                                     |
                                     v
                          +----------+------------+
                          |   OpenClaw Gateway    |
                          |   (port 18789)        |
                          |                       |
                          |  before_agent_start   |
                          |  hook fires:          |
                          |   |                   |
                          |   +-> Personal Context|
                          |       Plugin (5.4)    |
                          |       queries :8300   |
                          |       prepends context|
                          |                       |
                          +----------+------------+
                                     |
                    +----------------+----------------+
                    |                                 |
                    v                                 v
          +---------+---------+             +---------+---------+
          | Cloud LLM (Sonnet)|             | personal-knowledge|
          | (for complex/tool |             | skill triggers    |
          |  queries)         |             | curl :8300/query  |
          +-------------------+             +---------+---------+
                                                      |
                                                      v
                                            +---------+---------+
                                            | RAG Service :8300 |
                                            |                   |
                                            | 1. Embed query    |
                                            |    (nomic-embed)  |
                                            | 2. Search ChromaDB|
                                            | 3. Generate answer|
                                            |    (qwen3:4b)     |
                                            +---------+---------+
                                                      |
                                          +-----------+-----------+
                                          |                       |
                                          v                       v
                                   +------+------+        +------+------+
                                   | ChromaDB    |        | Ollama      |
                                   | (vectors)   |        | (localhost  |
                                   | ~/.openclaw/|        |  :11434)    |
                                   | personal-rag|        |             |
                                   +-------------+        +-------------+
```

### 6.2 Data Flow for a Personal Question

```
1. User sends: "Good morning! What should I work on today?"

2. OpenClaw Gateway receives message

3. [Plugin] before_agent_start hook fires:
   - Extracts user text: "Good morning! What should I work on today?"
   - Calls http://localhost:8300/search with query
   - Gets back relevant context chunks (project status, recent activity)
   - Prepends <personal_context>...</personal_context> to system prompt

4. Cloud LLM (Sonnet) receives prompt WITH personal context already injected:
   - Sees the personal context
   - Also reads the personal-knowledge skill (always: true)
   - Decides this is a personal/routine question
   - Calls curl http://localhost:8300/query for a full local answer

5. Local RAG Service:
   - Embeds "Good morning! What should I work on today?" via nomic-embed-text
   - Searches ChromaDB for relevant chunks
   - Finds: project summary, recent activity, today's memory entry
   - Sends context + query to qwen3:4b
   - qwen3:4b generates: "Morning Arnaldo! Based on your recent work..."

6. Cloud LLM receives local answer
   - Uses it as-is or augments with its own knowledge
   - Responds to user via Telegram
```

### 6.3 Data Flow for a Complex Question

```
1. User sends: "Write a Python script that parses XML and converts to JSON"

2. before_agent_start hook fires:
   - Searches RAG, finds no relevant personal context
   - Returns nothing (no context prepended)

3. Cloud LLM (Sonnet) handles directly:
   - personal-knowledge skill says "don't use for complex reasoning/coding"
   - Sonnet writes the Python script using its full capabilities
   - No local model invoked = no CPU overhead
```

### 6.4 Conversation Coherence

**Problem**: If local answers 3 messages, does cloud have context?

**Solution**: This is handled naturally because:
1. OpenClaw maintains the full conversation in its session JSONL
2. The cloud LLM sees all previous messages (including tool results from RAG queries)
3. The local model is only called per-query, not maintaining its own session
4. Context pruning (`cache-ttl` with 1h TTL) keeps the window manageable

### 6.5 System Prompt Size Concern

**Problem**: qwen3:4b with its 4K effective context window can't handle the 12K+ OpenClaw system prompt.

**Solution**: The local model NEVER receives the OpenClaw system prompt. The RAG service sends its own minimal system prompt (~200 tokens) plus retrieved context (~500-1000 tokens), leaving ~2800 tokens for the actual query and response. This is handled entirely within the RAG service.

### 6.6 Resource Budget

| Service | RAM (idle) | RAM (active) | CPU (active) |
|---------|-----------|-------------|-------------|
| Ollama (qwen3:4b loaded) | ~3 GB | ~4 GB | 100% 4 cores |
| Ollama (nomic-embed-text) | ~400 MB | ~500 MB | ~50% 1 core |
| ChromaDB (in-process) | ~80 MB | ~150 MB | Minimal |
| RAG FastAPI service | ~50 MB | ~80 MB | Minimal |
| **Total additional** | **~3.5 GB** | **~4.7 GB** | Variable |

With 16 GB RAM total and the OS + OpenClaw using ~4 GB, there is ~8 GB available. The qwen3:4b model fits comfortably.

**Note**: Ollama unloads models after idle timeout (default 5 minutes). The first RAG query after idle will take 5-10 seconds to load the model. Set `OLLAMA_KEEP_ALIVE=-1` in Ollama's systemd service to keep the model loaded permanently, or accept the cold-start latency.

---

## 7. Implementation Phases

### Phase 1: Local RAG Service (do this first, 1-2 hours)

**Why first**: Works immediately with existing data, no training needed, provides value on day one.

1. Create `/home/anakin/Workspace/alterans/anakin/configs/personal-rag/` directory
2. Write `rag_service.py` and `requirements.txt`
3. Create Python venv and install dependencies
4. Start the service and run initial `/sync`
5. Test with `/query` and `/search` endpoints
6. Create systemd service for persistence
7. Create the OpenClaw skill (`personal-knowledge`)

**Validation**: `curl http://localhost:8300/query -d '{"query":"What is Arnaldo working on?"}'` returns a relevant answer.

### Phase 2: OpenClaw Skill Integration (30 minutes)

1. Create the `personal-knowledge` skill in `~/.openclaw/workspace/skills/`
2. Restart OpenClaw gateway to pick up the new skill
3. Test via Telegram: ask Anakin a personal question and verify it queries the RAG service
4. Monitor logs to see tool calls to port 8300

**Validation**: Telegram conversation shows the bot using local knowledge for personal questions.

### Phase 3: Context Injection Plugin (1-2 hours, optional)

1. Create the `personal-context` plugin in `~/.openclaw/workspace/extensions/`
2. Test that `before_agent_start` hook fires and prepends context
3. Verify the cloud LLM receives and uses the injected personal context
4. Monitor for performance impact (should add <500ms latency from local embedding)

**Validation**: Even without the skill being invoked, the LLM's responses show awareness of personal context.

### Phase 4: Data Collection for Fine-tuning (ongoing, 2-4 weeks)

1. Run `scripts/extract-training-data.py --stats-only` weekly to track data growth
2. Keep accumulating conversations naturally
3. Target: 500+ Q&A pairs before attempting fine-tuning
4. Create manual preference pairs for known facts:

```jsonl
{"conversations":[{"from":"system","value":"You are Anakin, a personal AI assistant for Arnaldo."},{"from":"human","value":"What's my name?"},{"from":"gpt","value":"You're Arnaldo Silva, an entrepreneur and software developer based in Curitiba, Brazil."}]}
{"conversations":[{"from":"system","value":"You are Anakin, a personal AI assistant for Arnaldo."},{"from":"human","value":"What timezone am I in?"},{"from":"gpt","value":"You're in GMT-3 (Brasilia time), Curitiba, Brazil."}]}
```

### Phase 5: Fine-tuning on Colab (2-3 hours when data is ready)

1. Run `scripts/extract-training-data.py --include-memory -o training_data.jsonl`
2. Upload to Google Drive
3. Open the Unsloth Qwen3 4B Colab notebook
4. Modify cells as documented in Section 4.3
5. Train (takes ~15-30 minutes on free T4)
6. Download GGUF + Modelfile
7. Deploy to Ollama: `ollama create anakin-qwen3:latest -f Modelfile`
8. Update RAG service `CHAT_MODEL=anakin-qwen3:latest`

**Validation**: The fine-tuned model responds in Anakin's tone/style for personal questions.

### Phase 6: Monitoring and Iteration (ongoing)

1. Track which queries go to local vs cloud (add logging to RAG service)
2. Monitor response quality from the local model
3. Re-sync RAG weekly, re-fine-tune monthly
4. Gradually expand the categories handled locally

---

## Appendix A: Key File Locations

| File | Purpose |
|------|---------|
| `~/.openclaw/agents/main/sessions/*.jsonl` | Conversation logs (JSONL) |
| `~/.openclaw/memory/main.sqlite` | Memory vector DB (OpenAI embeddings) |
| `~/.openclaw/workspace/memory/*.md` | Memory markdown files |
| `~/.openclaw/openclaw.json` | OpenClaw configuration |
| `~/.openclaw/workspace/skills/personal-knowledge/SKILL.md` | RAG query skill |
| `/home/anakin/Workspace/alterans/anakin/configs/personal-rag/rag_service.py` | RAG FastAPI service |
| `/home/anakin/Workspace/alterans/anakin/scripts/extract-training-data.py` | Training data extractor |
| `~/.openclaw/personal-rag/chromadb/` | ChromaDB vector store |
| `~/.config/systemd/user/personal-rag.service` | RAG service systemd unit |

## Appendix B: Commands Quick Reference

```bash
# RAG Service
systemctl --user start personal-rag
systemctl --user status personal-rag
curl -s http://localhost:8300/health | python3 -m json.tool
curl -s -X POST http://localhost:8300/sync | python3 -m json.tool
curl -s -X POST http://localhost:8300/query -H "Content-Type: application/json" \
  -d '{"query": "test question"}' | python3 -m json.tool

# Training Data
python3 scripts/extract-training-data.py --stats-only
python3 scripts/extract-training-data.py --include-memory -o training_data.jsonl
python3 scripts/extract-training-data.py --filter-preferences --stats-only

# Ollama
ollama list
ollama run qwen3:4b "test"
ollama create anakin-qwen3:latest -f ~/models/anakin-qwen3/Modelfile

# OpenClaw
systemctl --user restart openclaw-gateway.service
openclaw memory status
```

## Appendix C: Sources and References

- [Unsloth Qwen3 Fine-tuning Guide](https://unsloth.ai/docs/models/qwen3-how-to-run-and-fine-tune)
- [Unsloth Qwen3 4B Colab Notebook](https://colab.research.google.com/github/unslothai/notebooks/blob/main/nb/Qwen3_(4B)-Instruct.ipynb)
- [Unsloth GGUF Export Docs](https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-gguf)
- [Unsloth Ollama Export Docs](https://unsloth.ai/docs/basics/inference-and-deployment/saving-to-ollama)
- [ChromaDB + Ollama RAG Tutorial](https://medium.com/@rahul.dusad/run-rag-pipeline-locally-with-ollama-embedding-model-nomic-embed-text-generate-model-llama3-e7a554a541b3)
- [Local RAG with FastAPI and Ollama](https://dev.to/nishant_prakash_780f5d541/no-openai-api-no-problem-build-rag-locally-with-ollama-and-fastapi-5g3c)
- [nomic-embed-text on Ollama](https://ollama.com/library/nomic-embed-text) (768 dimensions)
- [OpenClaw Plugin Docs](https://docs.openclaw.ai/plugin)
- [ChromaDB Ollama Embeddings Cookbook](https://cookbook.chromadb.dev/integrations/ollama/embeddings/)
- [LiteLLM Custom Routing](https://docs.litellm.ai/docs/routing)
- [Unsloth Fine-Tuning + Ollama Guide](https://medium.com/@yuxiaojian/fine-tuning-ollama-models-with-unsloth-a504ff9e8002)
