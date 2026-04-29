# Telegram Ecosystem Bot (aiogram 3.x)

Production-focused Telegram bot for:
- Taglish user-facing welcome flow
- English operator workflow for fast campaign posting to channels
- Reusable media assets via Telegram `file_id`

This document is the full operator and deployment guide.

---

## 1) Features (current build)

### End-user flow
- `/start` sends Taglish welcome message + menu buttons:
  - Groups / Community
  - App Download
  - Official Bot
  - Support / Help

### Operator flow (admin only)
- `/operator_help` - command cheat sheet
- `/asset_save NAME` - save replied photo/video as reusable asset
- `/campaign_create` - guided campaign composer:
  1. target channel/chat
  2. asset name or `skip`
  3. caption
  4. button rows
  5. preview + publish
- `/campaign_cancel` - cancel active campaign builder session

### Other
- CTA callback tracking demo (`/post_demo`)
- user tracking in SQLite (`uid`, `username`, `full_name`, `join_date`)
- process lock + webhook cleanup for stable long polling

---

## 2) Quickstart (local)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app
```

Minimum required in `.env`:
- `BOT_TOKEN`

---

## 3) Environment variables

See `.env.example` for full list.

### Required
- `BOT_TOKEN`

### AI localization (optional but recommended for `/campaign_create` previews)
- `GEMINI_API_KEY`
- `GEMINI_MODEL` (default in code: `gemini-2.0-flash`)

### Recommended
- `ADMIN_IDS=123456789,987654321`
- `GROUPS_URL=https://t.me/...`
- `APP_URL=https://...`
- `OFFICIAL_BOT_URL=https://t.me/...`
- `SUPPORT_URL=https://t.me/...`
- `COMMENT_URL=https://t.me/...`
- `CONVERSION_URL=https://...`
- `BROADCAST_RPS=30`
- `LOG_LEVEL=INFO`

### Notes
- `ADMIN_IDS` uses numeric Telegram user IDs only (not usernames, not phone numbers).
- URL fields should be full links (e.g. `https://t.me/your_channel`).

---

## 4) Operator usage guide

## 4.1 Save reusable media asset
1. Send or forward a **photo/video** to bot chat.
2. Reply to that message:
   - `/asset_save promo1`
3. Bot confirms asset saved.

Use cases:
- Reuse same creative across campaigns
- Faster sends using Telegram `file_id`

Important:
- Works with photo/video, not generic document files.

## 4.2 Create campaign post (guided)
1. Send `/campaign_create`
2. Step 1: enter target chat (`@channel` or `-100...`)
3. Step 2: enter asset name (e.g. `promo1`) or `skip`
4. Step 3: send caption text (HTML allowed)
5. Step 4: add buttons in format:
   - `Button Text | https://example.com`
   - `/row` for a new row
   - `/done` to finish buttons
6. Step 5: review preview, then send:
   - `/publish`

Cancel anytime:
- `/campaign_cancel`

---

## 5) Preview behavior

Preview is built in the flow:
- Send `/done` in step 4
- Bot renders a preview message in your admin chat
- Send `/publish` to post to target channel

---

## 6) Railway deployment guide

### 6.1 Connect repo
- Deploy from GitHub repo
- Dockerfile is included

### 6.2 Set variables in Railway
- Add at least `BOT_TOKEN`
- Add recommended variables listed above
- If you use AI previews: add `GEMINI_API_KEY` (+ optional `GEMINI_MODEL`)

### 6.3 Runtime settings
- Replicas: `1` (important for polling bots)
- Start command: can be empty (Dockerfile already runs `python -m app`)

### 6.4 Verify
- In Telegram: send `/start`
- In Railway logs: should show `Start polling`

### 6.5 Rotating bot token (most reliable MVP fix for conflicts)
If you generated a **new BotFather token**, do this in order:

1. **Stop old pollers**
   - Stop local `python -m app`
   - Remove/disable any second Railway service using the old token
2. **Railway Variables**
   - Update `BOT_TOKEN` to the new token
   - Click **Redeploy**
3. **Revoke old token** in BotFather (so nothing can accidentally poll with it)
4. **Confirm single poller**
   - Railway logs should NOT show `TelegramConflictError ... other getUpdates request`
5. **Test**
   - Open the bot’s correct `@username` and send `/start`

---

## 7) Troubleshooting

### `BOT_TOKEN Field required`
- `BOT_TOKEN` missing in Railway Variables

### `TelegramConflictError ... other getUpdates request`
- Same token running in another instance/service
- Keep only one active poller
- Most common MVP fix: rotate token + ensure Railway replicas = 1 + delete duplicate services

### Bot online but no replies
- Wrong bot username in chat
- Wrong token
- Missing bot permissions in channel
- Another service still using same token

### Asset not found in Step 2
- You must save an asset first via `/asset_save NAME`
- Step 2 expects that saved `NAME`, not random text

---

## 8) Project structure

- `app/main.py`: app bootstrap and polling
- `app/config.py`: env settings
- `app/handlers/start.py`: user `/start`
- `app/handlers/admin_campaign.py`: operator campaign workflow
- `app/handlers/callbacks.py`: CTA callback tracking sample
- `app/keyboards/`: button builders
- `app/middlewares/user_tracking.py`: user persistence middleware
- `app/db/`: SQLite adapter + abstractions
- `app/utils/`: logging and process lock

---

## 9) Suggested next improvements

1. Add `/asset_list` and `/asset_delete NAME`
2. Allow "upload media directly" during Step 2 (no pre-save needed)
3. Save/load campaign templates
4. Multi-channel publish in one action
5. Add PostgreSQL adapter for persistent production data
