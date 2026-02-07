#!/usr/bin/env bash
# patch-openclaw-tts.sh — Fix TTS MEDIA: path validation in OpenClaw
#
# Problem: OpenClaw's isValidMedia() rejects absolute /tmp/ paths,
#          causing TTS audio to leak as literal "MEDIA:/tmp/..." text
#          instead of being delivered as voice notes.
#
# Run this after every `npm install -g openclaw@latest`.

set -euo pipefail

OPENCLAW_DIST="${OPENCLAW_DIST:-$HOME/.npm-global/lib/node_modules/openclaw/dist}"

if [[ ! -d "$OPENCLAW_DIST" ]]; then
  echo "ERROR: OpenClaw dist not found at $OPENCLAW_DIST"
  echo "Set OPENCLAW_DIST if installed elsewhere."
  exit 1
fi

PATCHED=0
SKIPPED=0

for f in "$OPENCLAW_DIST"/deliver-*.js; do
  [[ -f "$f" ]] || continue

  if ! grep -q 'function isValidMedia' "$f"; then
    echo "SKIP (no isValidMedia): $(basename "$f")"
    continue
  fi

  # Check if already patched (the literal string in the JS file is \/tmp\/)
  if python3 -c "
import sys
with open(sys.argv[1]) as f:
    sys.exit(0 if '\\\\/tmp\\\\/' in f.read() else 1)
" "$f"; then
    echo "SKIP (already patched): $(basename "$f")"
    SKIPPED=$((SKIPPED + 1))
    continue
  fi

  # Apply patch: insert /tmp/ path acceptance after the https check
  python3 -c "
import sys

with open(sys.argv[1], 'r') as f:
    content = f.read()

search = '\tif (/^https?:\\/\\//i.test(candidate)) return true;\n\treturn candidate.startsWith(\"./\") && !candidate.includes(\"..\");'
replace = '\tif (/^https?:\\/\\//i.test(candidate)) return true;\n\tif (/^\\\\/tmp\\\\//.test(candidate) && !candidate.includes(\"..\")) return true;\n\treturn candidate.startsWith(\"./\") && !candidate.includes(\"..\");'

if search not in content:
    print(f'WARN: search pattern not found in {sys.argv[1]}', file=sys.stderr)
    sys.exit(1)

content = content.replace(search, replace, 1)
with open(sys.argv[1], 'w') as f:
    f.write(content)
" "$f"

  echo "PATCHED: $(basename "$f")"
  PATCHED=$((PATCHED + 1))
done

if [[ $PATCHED -eq 0 && $SKIPPED -gt 0 ]]; then
  echo "All deliver files already patched. Nothing to do."
elif [[ $PATCHED -gt 0 ]]; then
  echo ""
  echo "Patched $PATCHED file(s). Restart the gateway:"
  echo "  systemctl --user restart openclaw-gateway.service"
fi
