#!/usr/bin/env bash
# Calendar Morning Briefing - Cron job that sends today's agenda via Telegram
# Add to crontab: 0 7 * * * /home/anakin/Workspace/alterans/anakin/scripts/calendar-morning-briefing.sh
#
# Prerequisites: gog CLI installed and authenticated (see guides/gog-calendar-setup.md)

set -euo pipefail

GOG_BIN="${GOG_BIN:-/usr/local/bin/gog}"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"

# Check gog is available
if ! command -v "$GOG_BIN" &>/dev/null; then
    echo "gog CLI not found at $GOG_BIN" >&2
    exit 1
fi

TODAY=$(date +%Y-%m-%d)
TOMORROW=$(date -d "+1 day" +%Y-%m-%d)

# Fetch today's events across all calendars
EVENTS=$("$GOG_BIN" calendar events --all --from "${TODAY}T00:00:00" --to "${TODAY}T23:59:59" --plain 2>/dev/null || echo "")

if [ -z "$EVENTS" ] || [ "$EVENTS" = "No events found." ]; then
    MESSAGE="Good morning, Arnaldo! Your calendar is clear today. A good day to focus on deep work."
else
    MESSAGE="Good morning, Arnaldo! Here's your schedule for today:

${EVENTS}

Have a productive day!"
fi

# Send via OpenClaw Telegram channel
"$OPENCLAW_BIN" send --channel telegram --to "$TELEGRAM_CHAT_ID" --message "$MESSAGE" 2>/dev/null || \
    echo "$MESSAGE"
