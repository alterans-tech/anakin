"""
Personal Knowledge RAG Service

FastAPI microservice that indexes OpenClaw conversations and memory into
ChromaDB, embeds queries using Ollama nomic-embed-text (768d, fully local),
and generates answers using qwen3:4b. Zero cloud cost.

Endpoints:
    POST /query     - RAG query (search + generate with local model)
    POST /search    - Search only (return relevant chunks)
    POST /ingest    - Ingest new documents manually
    POST /sync      - Re-sync from OpenClaw memory/sessions
    POST /classify  - Classify if message needs cloud or can go local
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
http_client = httpx.Client(timeout=300.0)  # 5 min — qwen3:4b on CPU can be slow on cold start


def get_collection():
    """Get or create the personal knowledge collection."""
    return chroma_client.get_or_create_collection(
        name="personal_knowledge",
        metadata={"hnsw:space": "cosine"},
    )


def ollama_embed(texts: list[str]) -> list[list[float]]:
    """Get embeddings from Ollama nomic-embed-text."""
    embeddings = []
    for text in texts:
        resp = http_client.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": EMBED_MODEL, "prompt": text},
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
                "num_ctx": 4096,
            },
        },
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def extract_text_from_content(content) -> str:
    """Extract plain text from OpenClaw message content."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        texts = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                texts.append(block["text"])
        return "\n".join(texts).strip()
    return ""


def strip_telegram_envelope(text: str) -> str:
    """Remove Telegram metadata wrapper from user messages."""
    text = re.sub(
        r"\[Telegram\s+.*?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*",
        "",
        text,
    )
    text = re.sub(r"\n?\[message_id:\s*\d+\]$", "", text)
    return text.strip()


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


class ClassifyRequest(BaseModel):
    message: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[dict]
    model: str


class SearchResponse(BaseModel):
    results: list[dict]
    count: int


class ClassifyResponse(BaseModel):
    category: str
    confidence: str


# --- Endpoints ---


@app.get("/health")
def health():
    try:
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
        formatted.append(
            {
                "id": results["ids"][0][i],
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else None,
            }
        )

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
            if dist < 0.8:
                context_chunks.append(
                    {
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": dist,
                    }
                )

    # Step 2: Build prompt with context
    system = req.system_prompt or (
        "You are Anakin, a personal AI assistant for Arnaldo. "
        "Answer based on the personal knowledge context provided. "
        "If the context doesn't contain the answer, say so honestly. "
        "Be concise and direct."
    )

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
    if MEMORY_DIR.exists():
        for md_file in MEMORY_DIR.glob("*.md"):
            content = md_file.read_text()
            sections = re.split(r"\n(?=## )", content)
            for j, section in enumerate(sections):
                section = section.strip()
                if len(section) < 50:
                    continue
                # Chunk large sections (~400 tokens ~ 1600 chars)
                if len(section) > 1600:
                    chunks = [section[i : i + 1600] for i in range(0, len(section), 1200)]
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
    if SESSION_DIR.exists():
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
                if messages[i + 1].get("message", {}).get("role") != "assistant":
                    continue

                user_text = extract_text_from_content(messages[i]["message"].get("content", ""))
                asst_text = extract_text_from_content(messages[i + 1]["message"].get("content", ""))

                if len(user_text) < 5 or len(asst_text) < 10:
                    continue

                clean_user = strip_telegram_envelope(user_text)
                if not clean_user:
                    continue

                combined = f"User: {clean_user}\nAssistant: {asst_text[:500]}"
                doc_id = f"session_{sf.stem}_{i}"
                embedding = ollama_embed([combined])[0]
                collection.upsert(
                    ids=[doc_id],
                    documents=[combined],
                    embeddings=[embedding],
                    metadatas=[
                        {
                            "source": f"session/{sf.name}",
                            "type": "conversation",
                            "timestamp": messages[i].get("timestamp", ""),
                        }
                    ],
                )
                ingested += 1

    return {"synced": ingested, "total": collection.count()}


CLASSIFIER_SYSTEM = """You are a message classifier. Classify the user's message into one of these categories:
- PERSONAL: questions about preferences, routines, habits, personal info, greetings, casual chat
- COMPLEX: requires reasoning, coding, analysis, tool use, web search, or real-time information

Respond with ONLY the category name, nothing else. Do not use thinking tags."""


@app.post("/classify", response_model=ClassifyResponse)
def classify(req: ClassifyRequest):
    """Classify whether a message needs cloud or can be handled locally."""
    messages = [
        {"role": "system", "content": CLASSIFIER_SYSTEM},
        {"role": "user", "content": req.message},
    ]

    result = ollama_chat(messages, temperature=0.1)
    category = "PERSONAL" if "PERSONAL" in result.upper() else "COMPLEX"

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
