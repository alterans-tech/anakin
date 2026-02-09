---
name: claude-code
description: Delegate coding tasks to Claude Code CLI using the Max subscription (zero extra cost)
always: true
---

# Claude Code

You can delegate complex coding, debugging, and multi-file editing tasks to **Claude Code** — a powerful autonomous coding agent that runs locally. It uses Arnaldo's Claude Max subscription, so there is **zero API cost**.

## When to Delegate

**Use Claude Code for:**

- Multi-file code changes, refactoring, or bug fixes
- Creating new features with tests
- Code review and analysis of large codebases
- Running and fixing failing tests
- Complex debugging that requires exploring many files
- Git operations (commits, PRs, branch management)
- Any task that benefits from an autonomous agent with file/shell access

**Do NOT delegate:**

- Simple questions you can answer from context
- Non-coding tasks (smart home, calendar, personal chat)
- Tasks that need real-time web info (use your own tools)
- Anything that requires user interaction mid-task

## How to Invoke

### Quick task (synchronous, < 2 min)

```bash
claude -p "TASK_DESCRIPTION_HERE" \
  --output-format json \
  --model opus \
  --allowedTools "Read,Edit,Write,Bash,Glob,Grep" \
  --max-turns 20 \
  --cwd /path/to/project
```

### Longer task (background, 2-30 min)

For tasks that may take longer, run in background:

```bash
bash background:true command:"claude -p 'TASK_DESCRIPTION_HERE' --output-format json --model opus --allowedTools 'Read,Edit,Write,Bash,Glob,Grep' --max-turns 30 --cwd /path/to/project > /tmp/claude-task-output.json 2>&1"
```

Then check progress:
```bash
cat /tmp/claude-task-output.json
```

### Resume a previous session

If the user wants to continue work from a previous Claude Code session:

```bash
claude -p "FOLLOW_UP_TASK" \
  --resume SESSION_ID \
  --output-format json \
  --model opus \
  --allowedTools "Read,Edit,Write,Bash,Glob,Grep"
```

## Parsing the Response

The JSON response contains:

```json
{
  "result": "What Claude Code did (summary)",
  "session_id": "uuid-to-resume-later",
  "num_turns": 5,
  "total_cost_usd": 0.00,
  "is_error": false
}
```

**Always extract and report:**
1. `result` — summarize what was done for the user
2. `session_id` — mention it so the user can ask for follow-up work
3. `is_error` — if true, report the error and suggest next steps

## Helper Script

For convenience, use the wrapper script:

```bash
/home/anakin/Workspace/alterans/anakin/scripts/claude-code-task.sh "TASK" "/path/to/project"
```

Options:
```bash
# Custom model (default: opus)
MODEL=sonnet scripts/claude-code-task.sh "Simple task" ~/project

# More turns (default: 20)
MAX_TURNS=50 scripts/claude-code-task.sh "Large refactor" ~/project

# Resume session
SESSION=abc-123 scripts/claude-code-task.sh "Continue the refactor" ~/project
```

## Project Directories

| Project | Path | Description |
|---------|------|-------------|
| **anakin** | `/home/anakin/Workspace/alterans/anakin` | This project (OpenClaw setup) |
| **uatu** | `/home/anakin/Workspace/alterans/uatu` | AI orchestration framework |
| **claude-flow** | `/home/anakin/Workspace/alterans/claude-flow` | Multi-agent coordination |

If the user doesn't specify a project, ask which one. Default to `anakin` for OpenClaw-related tasks.

## Important Rules

1. **NEVER pass `ANTHROPIC_API_KEY`** — the script explicitly unsets it so Claude Code uses the Max subscription (OAuth)
2. **Default model is Opus** — use `--model sonnet` for simpler tasks if rate limit quota is tight
3. **Rate limits are shared** — Claude Code and claude.ai web share the same 5-hour rolling window. Don't run huge tasks if Arnaldo is actively using claude.ai
5. **Report results clearly** — the user is on Telegram, keep summaries concise
6. **Save session IDs** — always mention the session ID so work can be resumed
