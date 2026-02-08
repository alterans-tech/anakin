# Google Calendar Setup — gog CLI + OpenClaw

Manage multiple calendars through Anakin via Telegram/WhatsApp. Uses the `gog` CLI (gogcli) which is already a bundled OpenClaw skill. Supports all Google Calendar operations: list events, create/update/delete, cross-calendar agenda, conflict detection, and proactive reminders via cron jobs.

---

## Prerequisites

- OpenClaw gateway running (`systemctl --user status openclaw-gateway`)
- A Google account (personal or Workspace)
- Internet access for OAuth flow

---

## Step 1: Install the gog Binary

Download the pre-built Linux binary (no Homebrew needed):

```bash
curl -sL https://github.com/steipete/gogcli/releases/download/v0.9.0/gogcli_0.9.0_linux_amd64.tar.gz | tar xz
sudo mv gog /usr/local/bin/gog
gog --version
```

Verify:

```bash
which gog
# /usr/local/bin/gog
```

---

## Step 2: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/projectcreate) and create a new project (e.g. `anakin-calendar`)

2. Enable the Calendar API:
   - Navigate to [Calendar API](https://console.cloud.google.com/apis/api/calendar-json.googleapis.com) and click **Enable**
   - Optionally enable Gmail, Drive, People (Contacts), Sheets if you want full Workspace access later:
     - [Gmail API](https://console.cloud.google.com/apis/api/gmail.googleapis.com)
     - [Drive API](https://console.cloud.google.com/apis/api/drive.googleapis.com)
     - [People API](https://console.cloud.google.com/apis/api/people.googleapis.com)
     - [Sheets API](https://console.cloud.google.com/apis/api/sheets.googleapis.com)

3. Configure the OAuth consent screen:
   - Go to [OAuth consent](https://console.cloud.google.com/auth/branding)
   - Select **External** user type
   - Fill in app name (e.g. `Anakin Calendar`), support email, and developer email
   - Add scopes: `Google Calendar API` (all calendar scopes)
   - Save

4. Add yourself as a test user:
   - Go to [Audience](https://console.cloud.google.com/auth/audience)
   - Under **Test users**, add your Gmail address
   - The app stays in "Testing" mode (no need for verification for personal use)

5. Create OAuth credentials:
   - Go to [Clients](https://console.cloud.google.com/auth/clients)
   - Click **Create Client** > **Desktop app**
   - Name it `anakin-desktop`
   - Download the JSON file (saves as `client_secret_XXXXX.apps.googleusercontent.com.json`)
   - Move it somewhere safe: `mv ~/Downloads/client_secret_*.json ~/.config/gogcli/credentials.json`

---

## Step 3: Authenticate gog

Register the credentials and add your account:

```bash
# Register OAuth credentials
gog auth credentials ~/.config/gogcli/credentials.json

# Add your Google account (calendar-only, or full access)
gog auth add you@gmail.com --services calendar

# For full Workspace access instead:
# gog auth add you@gmail.com --services gmail,calendar,drive,contacts,sheets
```

This opens a browser for Google OAuth consent. Approve the permissions.

### Headless auth (no browser on this machine)

If running on a headless server, use `--manual`:

```bash
gog auth add you@gmail.com --services calendar --manual
```

This prints a URL to visit on any device. Paste the auth code back.

### Verify authentication

```bash
gog auth list
gog auth list --check
```

---

## Step 4: Test Calendar Access

```bash
# Set default account (avoids --account on every command)
export GOG_ACCOUNT=you@gmail.com

# List all calendars
gog calendar calendars

# List today's events across all calendars
gog calendar events --all --from "$(date -I)" --to "$(date -I -d '+1 day')" --plain

# List events for a specific calendar
gog calendar events primary --from "$(date -I)" --to "$(date -I -d '+7 days')"

# Create a test event
gog calendar create primary --summary "Test from Anakin" --from "$(date -I)T18:00:00" --to "$(date -I)T18:30:00"
```

---

## Step 5: Configure OpenClaw Environment

Add `GOG_ACCOUNT` and optionally `GOG_KEYRING_PASSWORD` to the systemd service so the gateway can invoke `gog` non-interactively.

### 5a. Set the keyring password for headless use

gog stores tokens in an encrypted file. For systemd (no TTY), it needs the keyring password in an env var:

```bash
# Set a password for the gog keyring (first-time only)
export GOG_KEYRING_PASSWORD="your-secure-password-here"
gog auth list --check  # verify it works with this password
```

### 5b. Add to the systemd unit

Edit the service file:

```bash
systemctl --user edit openclaw-gateway.service --force
```

Add under `[Service]`:

```ini
Environment="GOG_ACCOUNT=you@gmail.com"
Environment="GOG_KEYRING_PASSWORD=your-secure-password-here"
```

Or edit the full file directly at `~/.config/systemd/user/openclaw-gateway.service` and add the two `Environment=` lines alongside the existing ones.

Make sure `/usr/local/bin` is in the `PATH` line so the gateway can find the `gog` binary.

### 5c. Reload and restart

```bash
systemctl --user daemon-reload
systemctl --user restart openclaw-gateway.service
systemctl --user status openclaw-gateway.service
```

---

## Step 6: Install the gog-calendar ClawHub Skill (Recommended)

The bundled `gog` skill covers all of Google Workspace. The `gog-calendar` ClawHub skill adds calendar-specific optimizations:

- Cross-calendar agenda queries with `--all --plain`
- Automatic filtering of noise calendars (holidays, birthdays)
- Token-efficient output formatting
- Enforces user confirmation before any writes

```bash
clawhub install gog-calendar
```

After installing, restart the gateway:

```bash
systemctl --user restart openclaw-gateway.service
```

### Verify skill status

```bash
openclaw skills list
```

Both `gog` (bundled) and `gog-calendar` (ClawHub) should show as active (not `missing`).

---

## Step 7: Sharing Multiple Agendas with Anakin

### Calendars you own

All calendars in your Google account are automatically accessible. Run `gog calendar calendars` to see them.

### Calendars shared by others

When someone shares a Google Calendar with your email (family, partner, work team), it appears automatically in `gog calendar calendars`. No extra setup needed.

### External calendars (ICS feeds)

For non-Google calendars (school, sports, public events):

1. Get the ICS/iCal URL from the calendar provider
2. In Google Calendar web UI: **Other calendars (+)** > **From URL** > paste the ICS URL
3. The subscribed calendar now appears through `gog` like any other calendar

This is the simplest way to aggregate Outlook, Apple, or any public calendar into Anakin's view.

### Multiple Google accounts

```bash
gog auth add personal@gmail.com --services calendar
gog auth add work@company.com --services calendar
gog auth alias set personal personal@gmail.com
gog auth alias set work work@company.com
```

Query each account:

```bash
gog --account personal calendar events --all ...
gog --account work calendar events --all ...
```

---

## Step 8: Set Up Proactive Reminders (Cron Jobs)

### Morning briefing (daily at 7:00 AM)

```bash
openclaw cron add \
  --name "Morning calendar briefing" \
  --cron "0 7 * * *" \
  --tz "America/Sao_Paulo" \
  --session isolated \
  --message "Check my calendar for today across all calendars. Give me a concise summary of today's events, grouped by calendar. Highlight any conflicts or back-to-back meetings. Send on Telegram." \
  --announce \
  --channel telegram
```

### Pre-meeting reminders (every 15 minutes)

```bash
openclaw cron add \
  --name "Meeting reminder" \
  --cron "*/15 7-22 * * *" \
  --tz "America/Sao_Paulo" \
  --session isolated \
  --message "Check my calendar for events starting in the next 20 minutes. If any are found, send me a brief reminder on Telegram with the event title, time, and location. If nothing is coming up, do nothing and reply with just 'no upcoming events'." \
  --announce \
  --channel telegram
```

### Weekly planning (Sunday 8 PM)

```bash
openclaw cron add \
  --name "Weekly calendar review" \
  --cron "0 20 * * 0" \
  --tz "America/Sao_Paulo" \
  --session isolated \
  --message "Review my calendar for the upcoming week (Monday to Friday). Summarize each day's events, flag any conflicts or empty days, and suggest time blocks for focused work. Send on Telegram." \
  --announce \
  --channel telegram
```

### Manage cron jobs

```bash
openclaw cron list
openclaw cron run <jobId>          # test a job immediately
openclaw cron runs --id <jobId>    # view run history
openclaw cron edit <jobId> --enabled false  # disable a job
```

---

## Usage Examples via Telegram

Once set up, you can message Anakin naturally:

| You say | Anakin does |
|---------|-------------|
| "What's on my calendar today?" | Lists events across all calendars |
| "Schedule a dentist appointment Friday at 10am" | Creates event on primary calendar |
| "Move my 3pm meeting to 4pm" | Finds the event, updates the time |
| "Am I free Thursday afternoon?" | Checks all calendars for conflicts |
| "What's my week looking like?" | Summarizes Monday-Friday |
| "Add 'Team standup' every weekday at 9am" | Creates recurring event |
| "Delete the test event I made" | Finds and removes it (with confirmation) |

---

## Troubleshooting

### `gog: command not found` in OpenClaw

Ensure `/usr/local/bin` is in the `PATH` of the systemd service. Check:

```bash
grep PATH ~/.config/systemd/user/openclaw-gateway.service
```

Add `/usr/local/bin:` to the PATH value if missing.

### Token expired / auth error

```bash
gog auth list --check
# If expired:
gog auth add you@gmail.com --services calendar
```

Tokens auto-refresh, but if credentials are revoked in Google Cloud, re-auth is needed.

### Skill shows as `missing`

```bash
openclaw skills list | grep gog
```

If `gog` shows `missing`, the binary isn't found in PATH. Verify `which gog` returns a path, and that path is in the service's `PATH`.

### `GOG_KEYRING_PASSWORD` issues

If gog hangs waiting for keyring input, ensure the env var is set in the systemd unit. Test:

```bash
GOG_KEYRING_PASSWORD="your-password" gog auth list --check
```

### Calendar not visible

- Check it's enabled in Google Calendar web UI
- Run `gog calendar calendars` to list all accessible calendars
- Shared calendars must be accepted (check Google Calendar notification)

---

## Reference

| Item | Value |
|------|-------|
| gog binary | `/usr/local/bin/gog` |
| gog config | `~/.config/gogcli/config.json` |
| gog credentials | `~/.config/gogcli/credentials.json` |
| gog version | v0.9.0 |
| Bundled skill | `~/.npm-global/lib/node_modules/openclaw/skills/gog/SKILL.md` |
| ClawHub skill | `gog-calendar` v1.0.0 |
| Calendar API | `calendar-json.googleapis.com` |
| Cron jobs | `~/.openclaw/cron/jobs.json` |
| Systemd service | `~/.config/systemd/user/openclaw-gateway.service` |

---

## Calendar Command Reference

```bash
# List all calendars
gog calendar calendars

# List events (single calendar)
gog calendar events <calendarId> --from <ISO> --to <ISO>

# List events (all calendars)
gog calendar events --all --from <ISO> --to <ISO> --plain

# Create event
gog calendar create <calendarId> --summary "Title" --from <ISO> --to <ISO>

# Update event
gog calendar update <calendarId> <eventId> --summary "New Title" --from <ISO> --to <ISO>

# Color-code event (IDs 1-11)
gog calendar update <calendarId> <eventId> --color <colorId>

# Available colors
gog calendar colors
```
