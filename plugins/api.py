"""
api.py – REST API endpoints consumed by the Telegram Web App.
Registers JSON routes on the same aiohttp server.

Endpoints:
  GET /api/search?q=<query>&offset=<n>&max=<n>&type=<video|audio|document>
  GET /api/recent?max=<n>
  GET /api/stats
"""
import logging

from aiohttp import web

from database.ia_filterdb import get_search_results, Media
from database.users_chats_db import db as users_db
from database.filters_mdb import filter_stats

logger = logging.getLogger(__name__)
api_routes = web.RouteTableDef()


def _serialize_file(doc) -> dict:
    """Convert a uMongo document or raw dict to a plain JSON-serialisable dict."""
    if hasattr(doc, "to_mongo"):
        raw = doc.to_mongo()
    elif hasattr(doc, "__iter__"):
        raw = dict(doc)
    else:
        raw = {}

    return {
        "file_id":   str(raw.get("_id", "")),
        "file_name": raw.get("file_name", ""),
        "file_size": raw.get("file_size", 0),
        "file_type": raw.get("file_type", ""),
        "mime_type": raw.get("mime_type", ""),
        "caption":   raw.get("caption", ""),
    }


@api_routes.get("/api/search")
async def api_search(request: web.Request) -> web.Response:
    q         = request.rel_url.query.get("q", "").strip()
    offset    = int(request.rel_url.query.get("offset", 0))
    max_res   = min(int(request.rel_url.query.get("max", 15)), 50)
    file_type = request.rel_url.query.get("type", "") or None

    if not q or len(q) < 2:
        return web.json_response({"files": [], "total_results": 0, "next_offset": ""})

    try:
        files, next_offset, total = await get_search_results(
            query       = q,
            file_type   = file_type,
            max_results = max_res,
            offset      = offset,
        )
        return web.json_response({
            "files":         [_serialize_file(f) for f in files],
            "total_results": total,
            "next_offset":   next_offset,
        })
    except Exception as exc:
        logger.exception("Search API error: %s", exc)
        return web.json_response({"error": "Search failed"}, status=500)


@api_routes.get("/api/recent")
async def api_recent(request: web.Request) -> web.Response:
    max_res = min(int(request.rel_url.query.get("max", 20)), 50)
    try:
        cursor = Media.find({}).sort("$natural", -1).limit(max_res)
        files  = await cursor.to_list(length=max_res)
        return web.json_response({"files": [_serialize_file(f) for f in files]})
    except Exception as exc:
        logger.exception("Recent API error: %s", exc)
        return web.json_response({"error": "Failed to load recent files"}, status=500)


@api_routes.get("/api/stats")
async def api_stats(request: web.Request) -> web.Response:
    try:
        from info import AUTH_CHANNEL
        from bot import app as pyrogram_client
        # Import your existing database helper instance
        from database.users_chats_db import db as users_db 

        # ── Using your existing class functions ───────────────────────────
        total_files = await Media.count_documents({})
        total_users = await users_db.total_users_count()   # 🧩 Your function
        totl_chats  = await users_db.total_chat_count()    # 🧩 Your function
        
        # ── Using your existing storage size layout logic ──────────────────
        try:
            size = await users_db.get_db_size()            # 🧩 Your function
            free = 536870912 - size
            
            # Using your global utility formatter to get '265.57 MB MiB' strings
            from utils import get_size
            used_storage = get_size(size)
            free_storage = get_size(free)
        except Exception as e:
            logger.warning("Could not calculate DB storage sizes: %s", e)
            used_storage, free_storage = "–", "–"

        # ── Subscriber count via Pyrogram client cache ────────────────────
        subscriber_count = 0
        if AUTH_CHANNEL:
            try:
                chat = await pyrogram_client.get_chat(AUTH_CHANNEL)
                subscriber_count = getattr(chat, "members_count", 0) or 0
            except Exception as e:
                logger.warning("Could not fetch subscriber count: %s", e)

        # ── Latest promo post text from AUTH_CHANNEL ──────────────────────
        latest_promo_text = ""
        if AUTH_CHANNEL:
            try:
                async for msg in pyrogram_client.get_chat_history(AUTH_CHANNEL, limit=1):
                    latest_promo_text = msg.text or msg.caption or ""
                    break
            except Exception as e:
                logger.warning("Could not fetch latest promo post: %s", e)

        return web.json_response({
            "total_files":        total_files,
            "total_users":        total_users,
            "total_chats":        totl_chats,
            "subscriber_count":   subscriber_count,
            "latest_promo_text":  latest_promo_text,
            "used_storage":       used_storage,   
            "free_storage":       free_storage,   
        })
    except Exception as exc:
        logger.exception("Stats API error: %s", exc)
        return web.json_response({"error": "Stats unavailable"}, status=500)
