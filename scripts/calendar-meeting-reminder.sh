#!/usr/bin/env bash
# Meeting Reminder - Cron job that alerts 15 min before meetings
# Add to crontab: */15 * * * * /home/anakin/Workspace/alterans/anakin/scripts/calendar-meeting-reminder.sh
#
# Prerequisites: gog CLI installed and authenticated (see guides/gog-calendar-setup.md)

set -euo pipefail

GOG_BIN="${GOG_BIN:-/usr/local/bin/gog}"
OPENCLAW_BIN="${OPENCLAW_BIN:-openclaw}"
REMINDER_FILE="/tmp/.calendar-reminder-sent"

if ! command -v "$GOG_BIN" &>/dev/null; then
    exit 0  # Silently skip if gog not installed yet
fi

NOW=$(date +%Y-%m-%dT%H:%M:%S)
SOON=$(date -d "+20 minutes" +%Y-%m-%dT%H:%M:%S)

# Get events starting in the next 20 minutes
EVENTS=$("$GOG_BIN" calendar events --all --from "$NOW" --to "$SOON" --plain 2>/dev/null || echo "")

if [ -z "$EVENTS" ] || [ "$EVENTS" = "No events found." ]; then
    exit 0
fi

# Create a hash of current events to avoid duplicate reminders
EVENT_HASH=$(echo "$EVENTS" | md5sum | cut -d' ' -f1)

# Check if we already sent this reminder
if [ -f "$REMINDER_FILE" ] && grep -q "$EVENT_HASH" "$REMINDER_FILE" 2>/dev/null; then
    exit 0
fi

# Send reminder
MESSAGE="Upcoming in ~15 minutes:

${EVENTS}"

"$OPENCLAW_BIN" send --channel telegram --to "$TELEGRAM_CHAT_ID" --message "$MESSAGE" 2>/dev/null || \
    echo "$MESSAGE"

# Mark as sent (keep last 50 hashes)
echo "$EVENT_HASH" >> "$REMINDER_FILE"
tail -50 "$REMINDER_FILE" > "${REMINDER_FILE}.tmp" && mv "${REMINDER_FILE}.tmp" "$REMINDER_FILE"
