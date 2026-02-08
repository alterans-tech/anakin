#!/usr/bin/env python3
"""
Extract Q&A pairs from OpenClaw session logs for fine-tuning.

Usage:
    python3 scripts/extract-training-data.py
    python3 scripts/extract-training-data.py --filter-preferences
    python3 scripts/extract-training-data.py --include-memory
    python3 scripts/extract-training-data.py --stats-only
    python3 scripts/extract-training-data.py --output training_data.jsonl
"""

import argparse
import json
import re
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
    match = re.match(
        r"\[Telegram\s+.*?\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+GMT[+-]\d+\]\s*(.*)",
        text,
        re.DOTALL,
    )
    if match:
        msg = match.group(1).strip()
        msg = re.sub(r"\n?\[message_id:\s*\d+\]$", "", msg).strip()
        return msg
    if text.startswith("System:"):
        return ""
    return text.strip()


def is_preference_related(user_text, assistant_text):
    """Check if the exchange involves preferences, routines, or personal info."""
    combined = (user_text + " " + assistant_text).lower()
    keywords = [
        "i like", "i prefer", "i want", "i need", "i usually",
        "i always", "i never", "my favorite", "i enjoy", "i hate",
        "my routine", "every morning", "every day", "every night",
        "wake up", "go to bed", "schedule", "remind me",
        "my name", "i live", "i work", "i'm from",
        "call me", "don't call me", "i go by",
        "set temperature", "turn on", "turn off",
        "good morning", "good night", "bom dia", "boa noite",
    ]
    return any(kw in combined for kw in keywords)


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

        user_text = strip_telegram_envelope(extract_text_from_content(msg["message"]["content"]))
        assistant_text = "\n".join(assistant_text_parts)

        if user_text and assistant_text and len(user_text) > 2:
            if not user_text.startswith("System:"):
                pairs.append(
                    {
                        "user": user_text,
                        "assistant": assistant_text,
                        "timestamp": msg.get("timestamp", ""),
                    }
                )

        i = j if j > i else i + 1

    return pairs


def load_memory_as_context():
    """Load memory markdown files as additional training context."""
    context_pairs = []
    if not MEMORY_DIR.exists():
        return context_pairs
    for md_file in MEMORY_DIR.glob("*.md"):
        content = md_file.read_text()
        if "project-summary" in md_file.name:
            context_pairs.append(
                {
                    "user": "What's the current status of the Anakin project?",
                    "assistant": content[:2000],
                    "timestamp": "",
                }
            )
        elif re.match(r"\d{4}-\d{2}-\d{2}", md_file.stem):
            context_pairs.append(
                {
                    "user": f"What happened on {md_file.stem}?",
                    "assistant": content[:1500],
                    "timestamp": "",
                }
            )
    return context_pairs


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


def main():
    parser = argparse.ArgumentParser(description="Extract training data from OpenClaw logs")
    parser.add_argument("--output", "-o", default="training_data.jsonl", help="Output JSONL file")
    parser.add_argument("--filter-preferences", action="store_true", help="Only preference-related exchanges")
    parser.add_argument("--include-memory", action="store_true", help="Include memory files as training context")
    parser.add_argument("--min-assistant-length", type=int, default=10, help="Min assistant response length")
    parser.add_argument("--stats-only", action="store_true", help="Only print statistics")
    args = parser.parse_args()

    all_pairs = []
    session_files = list(SESSION_DIR.glob("*.jsonl")) + list(SESSION_DIR.glob("*.jsonl.old"))

    for sf in session_files:
        pairs = extract_pairs_from_session(sf)
        all_pairs.extend(pairs)

    if args.filter_preferences:
        all_pairs = [p for p in all_pairs if is_preference_related(p["user"], p["assistant"])]

    all_pairs = [p for p in all_pairs if len(p["assistant"]) >= args.min_assistant_length]

    if args.include_memory:
        all_pairs.extend(load_memory_as_context())

    print(f"Total Q&A pairs extracted: {len(all_pairs)}")
    pref_count = sum(1 for p in all_pairs if is_preference_related(p["user"], p["assistant"]))
    print(f"Preference-related: {pref_count}")
    if all_pairs:
        avg_user = sum(len(p["user"]) for p in all_pairs) / len(all_pairs)
        avg_asst = sum(len(p["assistant"]) for p in all_pairs) / len(all_pairs)
        print(f"Average user message length: {avg_user:.0f} chars")
        print(f"Average assistant response length: {avg_asst:.0f} chars")

    if args.stats_only:
        return

    training_data = format_for_training(all_pairs)
    output_path = Path(args.output)
    with open(output_path, "w") as f:
        for item in training_data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")

    print(f"Written {len(training_data)} training samples to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
