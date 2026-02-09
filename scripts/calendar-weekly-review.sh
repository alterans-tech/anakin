#!/usr/bin/env bash
# Weekly Review - Cron job that sends next week's overview on Sunday evening
# Add to crontab: 0 20 * * 0 /home/anakin/Workspace/alterans/anakin/scripts/calendar-weekly-review.sh
#
# Prerequisites: gog CLI installed and authenticated (see guides/gog-calendar-setup.md)

set -euo pipefail

GOG_BIN="${GOG_BIN:-/usr/local/bin/gog}"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

if ! command -v "$GOG_BIN" &>/dev/null; then
    echo "gog CLI not found at $GOG_BIN" >&2
    exit 1
fi

MONDAY=$(date -d "next monday" +%Y-%m-%d)
SUNDAY=$(date -d "next sunday" +%Y-%m-%d)

# Fetch next week's events
EVENTS=$("$GOG_BIN" calendar events --all --from "${MONDAY}T00:00:00" --to "${SUNDAY}T23:59:59" --plain 2>/dev/null || echo "")

if [ -z "$EVENTS" ] || [ "$EVENTS" = "No events found." ]; then
    MESSAGE="Weekly outlook: Your calendar is clear next week (${MONDAY} to ${SUNDAY}). A great week for planning ahead!"
else
    MESSAGE="Weekly outlook for ${MONDAY} to ${SUNDAY}:

${EVENTS}

Plan your week accordingly. Good night, Arnaldo!"
fi

"$OPENCLAW_BIN" send --channel telegram --to "$TELEGRAM_CHAT_ID" --message "$MESSAGE" 2>/dev/null || \
    echo "$MESSAGE"
