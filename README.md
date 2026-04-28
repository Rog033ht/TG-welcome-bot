# Telegram Ecosystem Bot (aiogram 3.x)

Taglish-first Telegram bot scaffold for PH market.

## Quickstart (local)

1. Create venv + install deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Create `.env` from `.env.example` and set `BOT_TOKEN`.

3. Run:

```bash
python -m app
```

## Structure

- `app/handlers/`: routers (start, content, spin)
- `app/keyboards/`: inline/reply keyboards
- `app/db/`: DB abstraction + SQLite implementation
- `app/middlewares/`: request/user tracking middleware
- `app/localization/strings.py`: Taglish user-facing strings
