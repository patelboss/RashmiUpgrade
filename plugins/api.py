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


# ── ✅ FIXED: POST ENDPOINT FOR DIRECT PREMIUM DISPATCH WITH SAFE OBJECT MAPPING ──
@api_routes.post("/api/send_file")
async def api_send_file(request: web.Request) -> web.Response:
    try:
        import variables
        from database.ia_filterdb import get_file_details
        from utils import clean_file_name, get_size

        # 1. Unpack incoming JSON payload fields
        payload = await request.json()
        raw_file_id = payload.get("file_id")
        user_id = payload.get("user_id")
        init_data = payload.get("init_data")

        if not user_id:
            user_id = _verify_and_extract_user(init_data)

        if not user_id:
            logger.warning("Bypass Delivery aborted: No valid user_id resolved.")
            return web.json_response({"status": "redirect_required"}, status=200)

        user_id = int(user_id)

        bot_client = request.app.get("bot_client")
        if not bot_client:
            logger.error("Core engine instance context 'bot_client' missing from web app server stack.")
            return web.json_response({"status": "redirect_required"}, status=200)

        # ── Step 1: Fetch object list from database matching your model ──
        from database.ia_filterdb import get_file_details
        files_list = await get_file_details(raw_file_id)
        if not files_list:
            logger.warning("Target document hash %s returned empty from collections query.", raw_file_id)
            return web.json_response({"error": "File not found"}, status=404)

        # get_file_details returns a list from cursor.to_list(length=1)
        file_doc = files_list

        # ── Step 2: Extract attributes directly via the uMongo wrapper mapping layer ──
        if isinstance(file_doc, dict):
            cached_file_id   = file_doc.get("file_id") or file_doc.get("_id")
            original_name    = file_doc.get("file_name")
            original_size    = file_doc.get("file_size")
            original_caption = file_doc.get("caption")
        else:
            cached_file_id   = getattr(file_doc, "file_id", None)
            original_name    = getattr(file_doc, "file_name", None)
            original_size    = getattr(file_doc, "file_size", None)
            original_caption = getattr(file_doc, "caption", None)

        cached_file_id = str(cached_file_id or "").strip()

        # Final safety catch against internal ObjectId dictionary formatting fallbacks
        if not cached_file_id or cached_file_id.startswith("ObjectId"):
            cached_file_id = str(raw_file_id)

        logger.info("Successfully resolved structural file_id value from uMongo object context: %s", cached_file_id)

        # ── Step 3: Parse caption string values ──────────────────────────────
        title = clean_file_name(str(original_name or cached_file_id))
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
            except Exception as fe:
                logger.error("Caption metadata macro string compilation exception occurred: %s", fe)
                caption = caption or title

        # ── Step 4: Fire direct private chat delivery bypass ─────────────────
        try:
            logger.info("Executing direct background cached media delivery bypass channel for chat: %s", user_id)
            
            await bot_client.send_cached_media(
                chat_id=user_id,
                file_id=cached_file_id,
                caption=caption or title,
                protect_content=protect_content
            )
            
            return web.json_response({"status": "direct_sent"}, status=200)

        except Exception as send_err:
            logger.warning("Direct backdrop transmission unreached for profile %s. Flipping to link window: %s", user_id, send_err)
            return web.json_response({"status": "redirect_required"}, status=200)

    except Exception as global_exc:
        logger.exception("Global breakdown inside WebApp file dispatch backend handler: %s", global_exc)
        return web.json_response({"status": "redirect_required"}, status=200)
