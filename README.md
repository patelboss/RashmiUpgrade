# AutoFile Search Bot — Upgraded

A Telegram bot that indexes media files from channels and lets users search them via inline queries, private chat, and a **Telegram Web App**.

---

## What was changed in this upgrade

| Area | Change |
|---|---|
| `variables.py` | Fixed `NameError` on `AUTH_CHANNELS` (missing quotes). Removed debug `print()` calls; replaced with `logging`. |
| `database/ia_filterdb.py` | **Critical bug fix**: `get_search_results()` now uses `.skip(offset).limit(max_results)` before `to_list()` — previously always returned only 1 result regardless of offset/page. |
| `database/filters_mdb.py` | Replaced deprecated `.count()` with `.count_documents()` (PyMongo 4.x). Fixed bare `except:` blocks. |
| `bot.py` | Robust logging setup: `logging.conf` applied if present, falls back to `basicConfig`. Cleaner startup. |
| `plugins/route.py` | `/` now returns proper JSON status. Added `/health` endpoint. Serves `/webapp` directory. |
| `plugins/__init__.py` | Registers API routes alongside main routes. |
| `plugins/api.py` | **New**: REST endpoints (`/api/search`, `/api/recent`, `/api/stats`) for the Web App. |
| `plugins/webapp_cmd.py` | **New**: `/webapp` command sends a Web App button. Handles `sendData()` callbacks. |
| `webapp/` | **New**: Full Telegram Web App — search UI, recent files, bot stats. |
| `requirements.txt` | Removed `python-telegram-bot==12.0.0b1` (unused). Replaced `fuzzywuzzy` with `rapidfuzz`. Updated `motor` to 3.x. Added `aiohttp-cors`. |

---

## Setup

```bash
git clone <your-repo>
cd auto-file-search
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # fill in your values
python bot.py
```

## Environment variables

See `.env.example` — every variable is documented with a comment.

Key required vars:
- `API_ID`, `API_HASH`, `BOT_TOKEN`
- `DATABASE_URI`
- `ADMINS`
- `BASE_URL` — public URL of your server (required for Web App)

## Telegram Web App

The Web App is served at `<BASE_URL>/webapp`.

Users open it via `/webapp` command → button → in-app browser.

Features:
- 🔎 Real-time file search with type filter (video / audio / document)
- 📋 Recent files tab
- 📊 Live bot stats (total files, users, groups, filters)
- Tap any file → detail sheet → "Get File" sends it to bot which forwards to user

To enable: set `BASE_URL` env var to your server's public URL (e.g. `https://mybot.koyeb.app`).

## Endpoints

| Path | Description |
|---|---|
| `GET /` | JSON health ping |
| `GET /health` | JSON: bot name, uptime, username |
| `GET /webapp` | Telegram Web App HTML |
| `GET /api/search?q=<query>&offset=0&max=15&type=video` | File search |
| `GET /api/recent?max=20` | Most recently indexed files |
| `GET /api/stats` | Bot statistics |

## Dependency notes

- **`fuzzywuzzy` → `rapidfuzz`**: drop-in replacement, ~10× faster. Update imports if used directly.
- **`python-telegram-bot` removed**: was unused (bot uses Pyrogram only).
- **`motor>=3.3`**: stays as async MongoDB driver. Motor 2.x deprecated.
# RashmiUpgrade
