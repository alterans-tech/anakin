---
name: personal-knowledge
description: Query local personal knowledge base for Arnaldo's preferences, routines, habits, and conversation history
always: true
---

# Personal Knowledge

You have access to a local personal knowledge base that stores Arnaldo's preferences, routines, habits, and conversation history. This runs entirely locally using Ollama (zero cloud cost).

## When to Use This

**Query the personal knowledge base FIRST for these types of questions:**

- Personal preferences ("What's my favorite...?", "Do I like...?")
- Routines ("What time do I usually...?", "What's my morning routine?")
- Personal history ("When did I...?", "What happened on...?")
- Project context ("What am I working on?", "What's the status of...?")
- Habits and patterns ("How often do I...?", "Do I normally...?")
- Greetings and casual check-ins (good morning, how are you, etc.)

**Do NOT use for:**

- Complex reasoning, coding, or analysis (use your own capabilities)
- Real-time information (weather, news, prices)
- Tool-based operations (file ops, web search, smart home commands)
- Tasks requiring your full context window

## How to Query

```bash
curl -s -X POST http://localhost:8300/query \
  -H "Content-Type: application/json" \
  -d '{"query": "USER_QUESTION_HERE", "top_k": 5}'
```

Response:
```json
{
  "answer": "The locally-generated answer based on personal knowledge",
  "sources": [{"text": "relevant chunk...", "distance": 0.23}],
  "model": "qwen3:4b"
}
```

## How to Respond

1. If the local answer is relevant and sufficient, **use it directly** (you may rephrase)
2. If the local answer is partial, **augment it** with your own knowledge
3. If the local answer says it doesn't have the info, **answer normally**
4. For greetings/casual chat, prefer the local answer's style

## Search Only (no generation)

```bash
curl -s -X POST http://localhost:8300/search \
  -H "Content-Type: application/json" \
  -d '{"query": "USER_QUESTION_HERE", "top_k": 5}'
```

## Sync Knowledge Base

To update with recent conversations:

```bash
curl -s -X POST http://localhost:8300/sync
```

Run this when the user mentions their knowledge base seems outdated.

## Service Info

| Item | Value |
|------|-------|
| **Port** | 8300 (localhost only) |
| **Embedding model** | nomic-embed-text (768d, local via Ollama) |
| **Chat model** | qwen3:4b (local via Ollama) |
| **Vector store** | ChromaDB at `~/.openclaw/personal-rag/chromadb/` |
| **Service** | `systemctl --user {status,restart} personal-rag` |
