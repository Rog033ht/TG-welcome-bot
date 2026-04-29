# WelcomePx / TG Welcome Bot — Full Introduction

This document describes what the bot does for **end users**, what **operators** can do, how **languages** work, and how **data + infrastructure** fit together. It reflects the codebase as of this repository version.

---

## 1. What this bot is

A **Telegram bot** built on **aiogram 3.x** (Python) aimed at a **Philippines-oriented audience** (Taglish UX where relevant), with:

- A **high-conversion style** main menu (official links: groups, app, bot, support).
- **Multi-language UI** driven mainly by the user’s Telegram app language.
- **SQLite** persistence for users, optional CTA analytics, saved media assets, and broadcast jobs.
- **Operator tooling** (English command surface) to build **channel promo posts** (with optional **Gemini** translations) and to run **throttled DM broadcasts** to known users.
- **Long polling** by default (with webhook cleared on startup), suitable for **Railway** and similar hosts.

---

## 2. End-user features (anyone who talks to the bot)

These commands and flows are **not** restricted by admin ID (unless Telegram itself hides messages in groups due to privacy rules).

### 2.1 `/start` — Welcome + main menu

- Sends a **localized welcome** (`WELCOME_TITLE`, `WELCOME_SUB`) and an **inline keyboard** with four URL buttons:
  - Groups / community  
  - App download  
  - Official bot  
  - Support / help  

- Button labels and body copy follow the user’s resolved language (see **Section 5**).

- **Important behavior:** `/start` is matched with **relaxed bot-mention rules** (`ignore_mention=True`), so if someone pastes `/start@SomeOldBotUsername` while chatting with *your* bot, it still responds. That avoids “silent” `/start` after rebranding or token changes.

- **URLs** for the menu come from environment variables (`GROUPS_URL`, `APP_URL`, `OFFICIAL_BOT_URL`, `SUPPORT_URL` in `.env.example`). Operators should set real HTTPS links before going live.

### 2.2 `/spin` — Lucky spin placeholder

- Sends a short **localized** “Lucky Spin” message (title + “coming soon” style copy).
- Intended as a **conversion / retention hook** to be extended later (no game logic in the current skeleton).

### 2.3 `/post_demo` — Sample “post + CTA” vibe

- Sends a **sample post-style message** (HTML) with a **callback** button (“Leave a comment” style), using localized `POST_CTA` / button text where applicable.
- Demonstrates the **post + inline CTA** pattern used in PH-style funnels (comment / conversion paths).

### 2.4 Callback buttons (`cta:…`) — CTA + light analytics

- When users tap certain **callback** buttons (not URL buttons), the bot:
  - **Logs** a row in `button_clicks` (user id, button id, chat/message ids, timestamp) — best-effort; failures do not block the user.
  - **Answers** the callback (quick “noted” style feedback).
  - **Sends a follow-up message** with a **link** from settings:
    - For `leave_comment` → `COMMENT_URL`
    - For other configured CTAs → `CONVERSION_URL` (see `app/handlers/callbacks.py`).

So end users get **immediate utility** (the link) while you get **basic CTA performance** signals in the database.

### 2.5 Groups vs private

- In **private chat**, the bot normally sees all messages you send it.
- In **groups**, Telegram **privacy mode** may hide ordinary messages; users may need **`/command@YourBotUsername`** or to **disable privacy** in BotFather if you want the bot to see non-command group messages. Commands like `/start@bot` in groups are a common pattern.

---

## 3. Operator features (admins only)

Operators are users whose **numeric Telegram user ID** appears in `ADMIN_IDS` (comma-separated in the environment). If `ADMIN_IDS` is empty, **no one** is treated as admin for these commands.

All operator commands below are **message commands** in DM (or wherever the bot can read your messages).

### 3.1 Help and playbooks

| Command | Purpose |
|--------|---------|
| `/operator_help` | Short list of operator commands (campaign + asset save + cancel). |
| `/ops_flow` | Step-by-step **English** checklist for the campaign workflow, plus **multi-language CTA phrase suggestions** pulled from the internal **“Old Driver” term bank** (EN/PH/VI/TR/ES). |

### 3.2 Reusable media — `/asset_save`

**Usage:** reply to a **photo** or **video** message, then send:

```text
/asset_save my_asset_name
```

**Effect:**

- Stores Telegram `file_id` + type in SQLite table `media_assets` under `my_asset_name`.
- Those assets can be referenced by **broadcasts** and by **campaign publish** (photo/video posts).

**Limits (current implementation):** photo and video only; name is whatever string you pass after the command.

### 3.3 Channel / chat campaign builder — `/campaign_create`

A **guided finite-state flow** (FSM) to publish a promo-style post to a **target chat or channel** (often `@YourChannel` or a numeric supergroup id like `-100…`).

**High-level steps:**

1. **`/campaign_create`** — starts the flow.  
2. **Target** — send `@channel`, `@supergroup`, or `-100…` id.  
3. **Asset** — send a name previously saved with `/asset_save`, or send `skip` for **text-only** publish.  
4. **Caption** — send **English** draft (HTML allowed). The bot then calls **Gemini** (if `GEMINI_API_KEY` is set) to build **PH / VI / TR / ES** previews (plus EN). If the API key is missing, non-EN previews effectively fall back to the English text.  
5. **Buttons + language** — in one state you can:
   - Add buttons: each line `Button text | https://…` (URL must start with `http`/`https`).  
   - **`/use_lang en|ph|vi|tr|es`** — pick which **translated caption** becomes final.  
   - **`/row`** — start a new keyboard row.  
   - **`/done`** — build **preview** in the admin chat (photo/video + caption + keyboard, or text-only).  
6. **`/publish`** — sends the same content to the **target** chat/channel.

**Cancel:** `/campaign_cancel` clears FSM state anytime during the flow.

**Permissions:** the bot account must be allowed to **post** in the target channel (typically **admin** with “Post messages” / equivalent). If not, publish fails and you get an error summary in DM.

### 3.4 User DM broadcasts — `/broadcast_*`

Broadcasts send a saved **asset** (photo/video) **plus caption** to users **known to the bot** (rows in `users`, populated when people interact and middleware upserts them).

| Command | Purpose |
|--------|---------|
| `/broadcast_new asset_name \| caption text...` | Creates a broadcast job in the DB; replies with a **numeric broadcast id**. |
| `/broadcast_run <id>` | Starts or resumes the worker for that id (respects rate limit). |
| `/broadcast_pause <id>` | Requests pause; job status moves toward `paused` and can be resumed with `/broadcast_run`. |
| `/broadcast_status <id>` | Shows status, counters, last uid cursor. |

**Throttling:** `BROADCAST_RPS` (default **30** messages per second cap in settings) spaces sends with `asyncio.sleep` between targets.

**Resume model:** progress is persisted (`last_uid`, sent/fail counts). After restarts, `/broadcast_run` can continue from the saved cursor.

**Caption localization (narrow):** if the stored caption string is **exactly** one of the keys `WELCOME_TITLE`, `WELCOME_SUB`, or `POST_CTA`, the worker runs it through the same `t(key, user_lang)` helper used in the UI — so those three keys can be broadcast **per-user language**. Any other caption text is sent **as-is** to everyone.

**Anti-spam helper:** optional unique suffix / timestamp on captions (`BROADCAST_UNIQUE_SUFFIX`) to reduce identical-message friction when blasting similar promos.

**Failures:** blocked users, Telegram server errors, etc. increment **fail** count and the loop continues; `TelegramRetryAfter` is handled with a sleep and that send is treated as not successful for that pass.

### 3.5 What operators do *not* have in-app (today)

- No `/lang` override for normal users (language is Telegram-driven + DB for broadcasts as above).
- **Follow-up** tables and service code exist in the repo, but the **follow-up scheduler is not started** in `app/main.py` in the current wiring — do not expect scheduled follow-up DMs until that is hooked up again.

---

## 4. Data model (what gets stored)

| Area | Table / concept | Role |
|------|-------------------|------|
| Users | `users` | `uid`, `username`, `full_name`, `join_date`, `language_code` — updated on interactions. |
| CTA analytics | `button_clicks` | Per-click log for callback CTAs. |
| Media library | `media_assets` | Named `file_id` for photo/video reuse. |
| Broadcasts | `broadcasts` | Job definition + `status` + progress fields for resume. |
| Followups | `followups` | Schema + DB API present; scheduler not wired in main entrypoint (see above). |

SQLite file path is controlled by `DB_URL` (see `.env.example`). On Docker/Railway, ensure the process can write to that path (the included Dockerfile creates `/app/data` for the default-style URL).

---

## 5. Languages — how “all the language parts” trigger

### 5.1 Live UI (menu, `/start`, `/spin`, `/post_demo`, callback strings that use `t()`)

- **`LanguageMiddleware`** reads Telegram’s `user.language_code` and normalizes it to one of **`en` / `ph` / `vi` / `es` / `tr`** (with fallbacks).
- **`fil` (Telegram Filipino)** is mapped to **`ph`** (Taglish bucket) so Filipino-language Telegram clients see the PH copy.
- Anything unknown falls back to **English**.

**Practical test:** change **Telegram → Settings → Language**, open the bot again, send `/start` or `/spin`.

### 5.2 “Old Driver” term bank

- Large structured dictionary (`TERM_BANK`) for marketing phrases by dimension (core, sports, rebate, finance) and language.
- Surfaced to operators mainly via **`/ops_flow`** and related hints — not a separate end-user game.

### 5.3 Gemini in `/campaign_create`

- After you paste the **English** caption, the bot requests **Taglish / Vietnamese / Turkish / Spanish** style variants from **Gemini** (`GEMINI_API_KEY`, optional `GEMINI_MODEL`, default `gemini-2.0-flash`).
- You lock the final post language with **`/use_lang`**.

---

## 6. Configuration checklist (operators + devops)

| Variable | Role |
|----------|------|
| `BOT_TOKEN` | Telegram bot token. |
| `ADMIN_IDS` | Comma-separated Telegram user IDs allowed to use operator commands. |
| `DB_URL` | SQLite connection string. |
| `GROUPS_URL`, `APP_URL`, `OFFICIAL_BOT_URL`, `SUPPORT_URL` | Main menu URL buttons. |
| `COMMENT_URL`, `CONVERSION_URL` | Destinations for callback CTAs in `callbacks.py`. |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | Optional; enables real multi-language campaign drafts. |
| `BROADCAST_RPS`, `BROADCAST_UNIQUE_SUFFIX` | Broadcast throughput + uniqueness helper. |
| `LOG_LEVEL` | Logging verbosity. |

**Deployment hygiene:** run **only one** polling instance per token (single Railway replica, no second local poller). Rotate tokens if you see conflict errors. The app clears webhooks on startup so polling receives updates.

---

## 7. Quick role-based summary

| Audience | Can do |
|----------|--------|
| **End user** | `/start` (menu), `/spin`, `/post_demo`, tap callback CTAs and receive links; language follows Telegram (with `fil`→`ph`). |
| **Operator (ADMIN_IDS)** | `/operator_help`, `/ops_flow`, `/asset_save`, full `/campaign_create` … `/publish` pipeline, `/broadcast_new` / `_run` / `_pause` / `_status`, `/campaign_cancel`. |
| **Platform** | SQLite persistence, optional Gemini, throttled broadcasts, process lock against duplicate instances in one container, HTML parse mode by default. |

For day-to-day operator steps, `OPERATOR_QUICKSTART.md` is the short checklist; this file is the **full conceptual map** of behavior and capabilities.
