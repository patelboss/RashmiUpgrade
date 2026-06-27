"""
api.py – REST API endpoints consumed by the Telegram Web App.
Registers JSON routes on the same aiohttp server.

Endpoints:
  GET /api/search?q=<query>&offset=<n>&max=<n>&type=<video|audio|document>
  GET /api/recent?max=<n>
  GET /api/stats
"""

from __future__ import annotations

import asyncio
import datetime
import logging

from aiohttp import web

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

    # This build intentionally avoids importing bot.py or any runtime client state.
    # Channel-level metrics like subscriber count and latest promo text are left as
    # safe placeholders so the API stays stable without a live Pyrogram reference.
    subscriber_count = 0
    latest_promo_text = ""
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
