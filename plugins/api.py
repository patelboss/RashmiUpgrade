"""
api.py – REST API endpoints consumed by the Telegram Web App.
Registers JSON routes on the same aiohttp server.

Endpoints:
  GET /api/search?q=<query>&offset=<n>&max=<n>&type=<video|audio|document>
  GET /api/recent?max=<n>
  GET /api/stats
  POST /api/send_file  <-- Proxy passing mock structures into native components
"""

from __future__ import annotations

import asyncio
import datetime
import logging
import re
import sys
import ujson
from urllib.parse import parse_qsl
from aiohttp import web
from plugins.subs_cmd import get_channel_subscriber_count
from info import AUTH_CHANNEL, ADMINS
from database.ia_filterdb import Media, get_search_results
from database.users_chats_db import db as users_db
from utils import get_size, temp
from plugins.pm_filter import *

# ── 🛠️ UNIFIED SYSTEM LOGGING MATRIX CONFIGURATION ───────────────────
logger = logging.getLogger("api_hub")
logger.setLevel(logging.INFO)
logger.propagate = False

if logger.hasHandlers():
    logger.handlers.clear()

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)

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
        logger.info("ℹ️ [_verify_and_extract_user] No init_data string provided to parse.")
        return None
    try:
        params = dict(parse_qsl(init_data))
        logger.info(f"📊 [_verify_and_extract_user] Raw parsed params keys: {list(params.keys())}")
        
        if "user" in params:
            user_data = ujson.loads(params["user"])
            logger.info(f"👤 [_verify_and_extract_user] Successfully found user dict object: {user_data}")
            return int(user_data.get("id"))
            
        logger.warning("⚠️ [_verify_and_extract_user] 'user' key missing from init_data parameters.")
    except Exception as e:
        logger.warning("❌ Failed to parse init_data validation fields: %s", e)
    return None


# ── 🚀 UNIFIED WEB SEARCH THROUGH REAL CHAT AUTOFILTERS ───────────────────
@api_routes.get("/api/search")
async def api_search(request: web.Request) -> web.Response:
    from pyrogram.enums import ChatType
    from plugins.pm_filter import auto_filter

    raw_q = request.rel_url.query.get("q", "").strip()
    offset = int(request.rel_url.query.get("offset", 0))
    max_res = min(int(request.rel_url.query.get("max", 15)), 50)
    file_type = request.rel_url.query.get("type", "") or None
    
    # 1. Capture BOTH potential identification parameters from the URL query string
    url_user_id = request.rel_url.query.get("user_id", "").strip()
    raw_init_data = request.rel_url.query.get("init_data", "")

    # 2. Process and clean the search text formatting
    flattened = raw_q.replace("\n", " ").replace("\r", " ")
    alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
    q = " ".join(alphanumeric_only.split()).strip()

    # 3. Dynamic multi-tier identity evaluation matching
    active_user_id = None
    
    if url_user_id.isdigit():
        active_user_id = int(url_user_id)
        logger.info(f"🎯 [SEARCH] Found direct numeric user_id parameter in URL: {active_user_id}")
    else:
        extracted_id = _verify_and_extract_user(raw_init_data)
        if extracted_id:
            active_user_id = extracted_id
            logger.info(f"🔑 [SEARCH] Extracted user_id from init_data token: {active_user_id}")

    # Fallback to structural database configuration list rules if both layers failed
    if not active_user_id:
        active_user_id = int(ADMINS[0]) if ADMINS else 1169128654
        logger.info(f"🛡️ [SEARCH] No user session found. Applying safe database cache fallback ID: {active_user_id}")

    # ✅ THE BULLETPROOF GUARD: Drop the request immediately if it's too short or contains only symbols
    if not q or len(q) < 3:
        logger.warning(f"⚠️ WebApp Search Rejected Early. Raw: '{raw_q}' dropped because Cleaned: '{q}' is too short.")
        return web.json_response({"files": [], "total_results": 0, "next_offset": ""})

    bot_client = request.app.get("bot_client")
    if not bot_client:
        return web.json_response({"error": "Core framework offline"}, status=503)

    try:
        DUMMY_CHAT_ID = -1001860020592
        mock_chat = type("MockChat", (object,), {"id": DUMMY_CHAT_ID, "type": ChatType.SUPERGROUP})()
        
        async def dummy_reply(*args, **kwargs):
            return type("DummySentMessage", (object,), {"id": 1})()

        mock_msg = type(
            "MockMessage",
            (object,),
            {
                "id": 1,
                "chat": mock_chat,
                "text": q,
                "from_user": type("MockUser", (object,), {"id": active_user_id})(), # ✅ Correctly mapped!
                "reply_text": dummy_reply,
                "reply_photo": dummy_reply,
                "reply": dummy_reply
            }
        )()

        # 2. Execute your core chat filtering
        await auto_filter(bot_client, mock_msg)

        # 3. Pull from cache layer
        key = f"{DUMMY_CHAT_ID}-1"
        cached_results = temp.GETALL.get(key, [])

        if cached_results:
            files = cached_results[offset : offset + max_res]
            total = len(cached_results)
            next_offset = offset + len(files) if total > offset + max_res else ""
            logger.info(f"✨ Search serving from cache matrix framework memory! Found {total} items.")
        else:
            files, next_offset, total = await get_search_results(
                query=q.lower(),
                file_type=file_type,
                max_results=max_res,
                offset=offset,
            )
            logger.info(f"📁 Cache expired. Dispatched lookup straight to MongoDB. Results: {total}")

        return web.json_response(
            {
                "files": [_serialize_file(f) for f in files],
                "total_results": total,
                "next_offset": next_offset,
            }
        )
    except Exception as exc:
        logger.exception("Unified Filter Search API error for query '%s': %s", q, exc)
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


async def _fetch_and_cache_stats(bot_client) -> None:
    """Fetch fresh data from DB and store it in RAM until midnight."""
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    total_files = await Media.count_documents({})
    total_users = await users_db.total_users_count()
    total_chats = await users_db.total_chat_count()

    subscriber_count = await get_channel_subscriber_count(bot_client, AUTH_CHANNEL)
    logger.info("AUTH_CHANNEL=%s | subscriber_count=%s", AUTH_CHANNEL, subscriber_count)
    latest_promo_text = "Comming Soon 🔜"

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


@api_routes.get("/api/stats")
async def api_stats(request: web.Request) -> web.Response:
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    force_refresh = request.rel_url.query.get("refresh", "").lower() == "true"
    now = datetime.datetime.now()

    bot_client = request.app.get("bot_client")
    if not bot_client:
        return web.json_response({"error": "Core framework offline"}, status=503)

    try:
        async with _STATS_LOCK:
            if force_refresh or not _STATS_CACHE or not _CACHE_EXPIRE_TIME or now >= _CACHE_EXPIRE_TIME:
                await _fetch_and_cache_stats(bot_client)
        return web.json_response(_STATS_CACHE)
    except Exception as exc:
        logger.exception("Cached Stats API error: %s", exc)
        return web.json_response({"error": "Stats unavailable"}, status=500)


@api_routes.post("/api/send_file")
async def api_send_file(request: web.Request) -> web.Response:
    try:
        from pyrogram.enums import ChatType
        from plugins.pm_filter import cb_handler

        payload = await request.json()
        raw_file_id = payload.get("file_id")
        user_id = payload.get("user_id")
        init_data = payload.get("init_data")
        
        is_protected = bool(payload.get("protect", False))

        if not user_id:
            user_id = _verify_and_extract_user(init_data)

        if not user_id:
            return web.json_response({"status": "redirect_required"}, status=200)

        user_id = int(user_id)
        
        # 🔍 DYNAMIC LOGGING TRACE FOR DISPATCH IDENTITIES
        logger.info(f"📥 [SEND_FILE] Requested File ID: '{raw_file_id}' | Final Destination User ID: {user_id}")

        bot_client = request.app.get("bot_client")

        DUMMY_CHAT_ID = -1001860020592
        mock_chat = type("MockChat", (object,), {"id": DUMMY_CHAT_ID, "type": ChatType.SUPERGROUP})()
        
        async def mock_reply_func(*args, **kwargs):
            text_content = args if args else "Action processed."
            return await bot_client.send_message(chat_id=user_id, text=text_content)

        mock_msg = type(
            "MockMessage", 
            (object,), 
            {
                "id": 1,
                "chat": mock_chat,
                "delete": lambda *args, **kwargs: asyncio.sleep(0), 
                "reply": mock_reply_func
            }
        )()

        mock_user = type("MockUser", (object,), {"id": user_id, "first_name": "User"})()
        prefix = "filep" if is_protected else "file"

        mock_query = type(
            "MockCallbackQuery",
            (object,),
            {
                "id": "0",
                "client": bot_client,
                "from_user": mock_user,
                "message": mock_msg,
                "data": f"{prefix}#{raw_file_id}",
                "answer": lambda *args, **kwargs: asyncio.sleep(0), 
                "edit_message_reply_markup": lambda *args, **kwargs: asyncio.sleep(0)
            }
        )()

        logger.info("Forwarding mock WebApp event payload straight to pm_filter.cb_handler -> User: %s", user_id)
        asyncio.create_task(cb_handler(bot_client, mock_query))

        return web.json_response({"status": "direct_sent"}, status=200)

    except Exception as global_exc:
        logger.exception("Global pipeline exception caught inside forwarding proxy route layout: %s", global_exc)
        return web.json_response({"status": "redirect_required"}, status=200)
