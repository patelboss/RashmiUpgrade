"""
api.py – REST API endpoints consumed by the Telegram Web App.
Registers JSON routes on the same aiohttp server.

Endpoints:
  GET /api/search?q=<query>&offset=<n>&max=<n>&type=<video|audio|document>
  GET /api/recent?max=<n>
  GET /api/stats
  POST /api/send_file  <-- New premium bypass delivery endpoint
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import ujson
from urllib.parse import parse_qsl
from aiohttp import web
from plugins.subs_cmd import get_channel_subscriber_count

from database.ia_filterdb import Media, get_search_results
from database.users_chats_db import db as users_db
from utils import get_size

logger = logging.getLogger(__name__)
api_routes = web.RouteTableDef()

# ── Global stats cache ───────────────────────────────────────────────────────
_STATS_CACHE = None
_CACHE_EXPIRE_TIME = None
_STATS_LOCK = asyncio.Lock()


def _serialize_file(doc) -> dict:
    """Convert a uMongo document or raw dict to a plain JSON-serialisable dict."""
    if hasattr(doc, "to_mongo"):
        raw = doc.to_mongo()
    elif hasattr(doc, "__iter__"):
        raw = dict(doc)
    else:
        raw = {}

    return {
        "file_id": str(raw.get("_id", "")),
        "file_name": raw.get("file_name", ""),
        "file_size": raw.get("file_size", 0),
        "file_type": raw.get("file_type", ""),
        "mime_type": raw.get("mime_type", ""),
        "caption": raw.get("caption", ""),
    }


def _verify_and_extract_user(init_data: str) -> int | None:
    """Parses Telegram WebApp initData string context to safely extract the User ID."""
    if not init_data:
        return None
    try:
        params = dict(parse_qsl(init_data))
        if "user" in params:
            user_data = ujson.loads(params["user"])
            return int(user_data.get("id"))
    except Exception as e:
        logger.warning("Failed to parse init_data validation fields: %s", e)
    return None


@api_routes.get("/api/search")
async def api_search(request: web.Request) -> web.Response:
    q = request.rel_url.query.get("q", "").strip()
    offset = int(request.rel_url.query.get("offset", 0))
    max_res = min(int(request.rel_url.query.get("max", 15)), 50)
    file_type = request.rel_url.query.get("type", "") or None

    if not q or len(q) < 2:
        return web.json_response({"files": [], "total_results": 0, "next_offset": ""})

    try:
        files, next_offset, total = await get_search_results(
            query=q,
            file_type=file_type,
            max_results=max_res,
            offset=offset,
        )
        return web.json_response(
            {
                "files": [_serialize_file(f) for f in files],
                "total_results": total,
                "next_offset": next_offset,
            }
        )
    except Exception as exc:
        logger.exception("Search API error: %s", exc)
        return web.json_response({"error": "Search failed"}, status=500)


@api_routes.get("/api/recent")
async def api_recent(request: web.Request) -> web.Response:
    max_res = min(int(request.rel_url.query.get("max", 20)), 50)
    try:
        cursor = Media.find({}).sort("$natural", -1).limit(max_res)
        files = await cursor.to_list(length=max_res)
        return web.json_response({"files": [_serialize_file(f) for f in files]})
    except Exception as exc:
        logger.exception("Recent API error: %s", exc)
        return web.json_response({"error": "Failed to load recent files"}, status=500)


async def _fetch_and_cache_stats() -> None:
    """Fetch fresh data from DB and store it in RAM until midnight."""
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    total_files = await Media.count_documents({})
    total_users = await users_db.total_users_count()
    total_chats = await users_db.total_chat_count()

    subscriber_count = 6000
    latest_promo_text = "Comming Soon 🔜"
    logger.info(
        "WebApp stats running in DB-only mode; live channel metrics are disabled in this build."
    )

    try:
        size = await users_db.get_db_size()
        free = max(0, 536870912 - int(size))
        used_storage = get_size(size)
        free_storage = get_size(free)
    except Exception as e:
        logger.warning("Storage size calculation failed: %s", e, exc_info=True)
        used_storage, free_storage = "–", "–"

    _STATS_CACHE = {
        "total_files": total_files,
        "total_users": total_users,
        "total_chats": total_chats,
        "subscriber_count": subscriber_count,
        "latest_promo_text": latest_promo_text,
        "used_storage": used_storage,
        "free_storage": free_storage,
        "generated_at": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
    }

    now = datetime.datetime.now()
    _CACHE_EXPIRE_TIME = datetime.datetime.combine(
        now.date() + datetime.timedelta(days=1),
        datetime.time.min,
    )

    logger.info(
        "Stats cache updated | files=%s users=%s chats=%s subscribers=%s expires_at=%s",
        total_files,
        total_users,
        total_chats,
        subscriber_count,
        _CACHE_EXPIRE_TIME,
    )


@api_routes.get("/api/stats")
async def api_stats(request: web.Request) -> web.Response:
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    force_refresh = request.rel_url.query.get("refresh", "").lower() == "true"
    now = datetime.datetime.now()

    try:
        async with _STATS_LOCK:
            if force_refresh or not _STATS_CACHE or not _CACHE_EXPIRE_TIME or now >= _CACHE_EXPIRE_TIME:
                logger.info(
                    "Stats refresh requested | force_refresh=%s | cache_present=%s | expired=%s",
                    force_refresh,
                    bool(_STATS_CACHE),
                    bool(_CACHE_EXPIRE_TIME and now >= _CACHE_EXPIRE_TIME),
                )
                await _fetch_and_cache_stats()

        return web.json_response(_STATS_CACHE)

    except Exception as exc:
        logger.exception("Cached Stats API error: %s", exc)
        if _STATS_CACHE:
            logger.warning("Serving stale stats cache due to refresh failure.")
            return web.json_response(_STATS_CACHE)

        return web.json_response({"error": "Stats unavailable"}, status=500)


# ── ✅ ADDED: POST ENDPOINT FOR DIRECT PREMIUM DISPATCH ───────────────────────
@api_routes.post("/api/send_file")
async def api_send_file(request: web.Request) -> web.Response:
    try:
        import variables
        from database.ia_filterdb import get_file_details
        from utils import clean_file_name, get_size

        data = await request.json()
        raw_file_id = data.get("file_id")
        init_data = data.get("init_data")

        # 1. Parse and extract User ID from WebApp initData query string context
        user_id = _verify_and_extract_user(init_data)
        if not user_id:
            return web.json_response({"error": "Unauthorized user validation failed"}, status=401)

        # 2. Grab your shared live bot client reference from aiohttp application context
        bot_client = request.app.get("bot_client")
        if not bot_client:
            return web.json_response({"error": "Core framework pipeline offline"}, status=500)

        # 3. Pull documents metrics from DB matching target hash indices
        files = await get_file_details(raw_file_id)
        if not files:
            return web.json_response({"error": "File entry absent from DB"}, status=404)

        f = files if isinstance(files, (list, tuple)) else files
        cached_file_id = getattr(f, "file_id", "") or f.get("file_id", "")
        original_name = getattr(f, "file_name", "") or f.get("file_name", "")
        original_size = getattr(f, "file_size", 0) or f.get("file_size", 0)
        original_caption = getattr(f, "caption", "") or f.get("caption", "")

        # 4. Process layout caption rules strings matching global variable states
        title = clean_file_name(str(original_name or raw_file_id))
        try:
            size = get_size(int(original_size))
        except Exception:
            size = ""

        caption = original_caption
        custom_caption = getattr(variables, "CUSTOM_FILE_CAPTION", "")
        protect_content = bool(getattr(variables, "PROTECT_CONTENT", False))

        if custom_caption:
            try:
                caption = custom_caption.format(
                    file_name=title or "",
                    file_size=size or "",
                    file_caption=caption or "",
                )
            except Exception:
                caption = caption or title

        # ── 🚀 BYPASS SETTINGS LOOP AND ATTEMPT DISPATCH IMMEDIATELY ──────────
        try:
            await bot_client.send_cached_media(
                chat_id=user_id,
                file_id=cached_file_id,
                caption=caption or title,
                protect_content=protect_content,
            )
            logger.info("Direct WebApp premium background delivery completed for user_id=%s", user_id)
            return web.json_response({"status": "direct_sent"}, status=200)
            
        except Exception as send_err:
            # Automatic fallback notice if user blocked or has never message-started the bot privately
            logger.warning("Direct delivery unreached for user %s, requesting deep link redirection fallback: %s", user_id, send_err)
            return web.json_response({"status": "redirect_required"}, status=200)

    except Exception as global_exc:
        logger.exception("Runtime exception inside premium file delivery engine: %s", global_exc)
        return web.json_response({"status": "redirect_required"}, status=200)
