#!/usr/bin/env bash
# Claude Code Task Runner — wraps `claude -p` for OpenClaw integration
# Uses Max subscription (OAuth), zero API cost.
#
# Usage:
#   ./scripts/claude-code-task.sh "Fix the bug in auth.py" /path/to/project
#   MODEL=opus ./scripts/claude-code-task.sh "Architecture review" ~/project
#   SESSION=abc-123 ./scripts/claude-code-task.sh "Continue work" ~/project
#   MAX_TURNS=50 ./scripts/claude-code-task.sh "Large refactor" ~/project

set -euo pipefail

TASK="${1:?Usage: claude-code-task.sh \"TASK\" [PROJECT_DIR]}"
PROJECT_DIR="${2:-$(pwd)}"
MODEL="${MODEL:-opus}"
MAX_TURNS="${MAX_TURNS:-20}"
SESSION="${SESSION:-}"
ALLOWED_TOOLS="${ALLOWED_TOOLS:-Read,Edit,Write,Bash,Glob,Grep}"

# CRITICAL: Unset API key so Claude Code uses Max subscription (OAuth)
unset ANTHROPIC_API_KEY 2>/dev/null || true

# Build command
CMD=(claude -p "$TASK"
  --output-format json
  --model "$MODEL"
  --allowedTools "$ALLOWED_TOOLS"
  --max-turns "$MAX_TURNS"
)

# Resume session if specified
if [ -n "$SESSION" ]; then
  CMD+=(--resume "$SESSION")
fi

# Change to project directory
cd "$PROJECT_DIR"

# Run and capture output
OUTPUT=$(mktemp /tmp/claude-code-XXXXXX.json)
"${CMD[@]}" > "$OUTPUT" 2>/dev/null

# Parse result
if command -v python3 &>/dev/null; then
  python3 -c "
import json, sys
with open('$OUTPUT') as f:
    d = json.load(f)
print(json.dumps({
    'result': d.get('result', ''),
    'session_id': d.get('session_id', ''),
    'num_turns': d.get('num_turns', 0),
    'cost_usd': d.get('total_cost_usd', 0),
    'model': list(d.get('modelUsage', {}).keys()),
    'is_error': d.get('is_error', False),
}, indent=2))
" 2>/dev/null || cat "$OUTPUT"
else
  cat "$OUTPUT"
fi

# Cleanup
rm -f "$OUTPUT"
