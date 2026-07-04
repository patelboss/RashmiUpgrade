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
import traceback
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

_STATS_CACHE = None
_CACHE_EXPIRE_TIME = None
_STATS_LOCK = asyncio.Lock()


def _safe_format(message: str, *args) -> str:
    try:
        return message % args if args else message
    except Exception:
        return f"{message} | args={args}"


def _emit(level: int, message: str, *args, exc_info: bool = False) -> None:
    text = _safe_format(message, *args)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} - api_hub - {logging.getLevelName(level)} - {text}"
    print(line, flush=True)
    logger.log(level, text, exc_info=exc_info)


def _emit_exception(message: str, *args) -> None:
    text = _safe_format(message, *args)
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ts} - api_hub - ERROR - {text}", flush=True)
    traceback.print_exc()
    logger.exception(text)


_emit(logging.INFO, "=" * 72)
_emit(logging.INFO, "api.py imported successfully from: %s", __file__)
_emit(logging.INFO, "=" * 72)


def _serialize_file(doc) -> dict:
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
    if not init_data:
        _emit(logging.INFO, "[_verify_and_extract_user] No init_data string provided to parse.")
        return None
    try:
        params = dict(parse_qsl(init_data))
        _emit(logging.INFO, "[_verify_and_extract_user] Raw parsed params keys: %s", list(params.keys()))

        if "user" in params:
            user_data = ujson.loads(params["user"])
            _emit(logging.INFO, "[_verify_and_extract_user] Successfully found user dict object: %s", user_data)
            return int(user_data.get("id"))

        _emit(logging.WARNING, "[_verify_and_extract_user] 'user' key missing from init_data parameters.")
    except Exception as e:
        _emit(logging.WARNING, "Failed to parse init_data validation fields: %s", e)
    return None


def _clean_search_query(raw_q: str) -> str:
    flattened = (raw_q or "").replace("\n", " ").replace("\r", " ")
    alphanumeric_only = re.sub(r"[^a-zA-Z0-9\s]", " ", flattened)
    return " ".join(alphanumeric_only.split()).strip()


@api_routes.get("/api/search")
async def api_search(request: web.Request) -> web.Response:
    from pyrogram.enums import ChatType
    from plugins.pm_filter import auto_filter

    raw_q = request.rel_url.query.get("q", "").strip()

    try:
        offset = max(0, int(request.rel_url.query.get("offset", 0)))
    except Exception:
        offset = 0

    try:
        max_res = min(max(1, int(request.rel_url.query.get("max", 15))), 50)
    except Exception:
        max_res = 15

    file_type = request.rel_url.query.get("type", "") or None
    url_user_id = request.rel_url.query.get("user_id", "").strip()
    raw_init_data = request.rel_url.query.get("init_data", "")

    _emit(
        logging.INFO,
        "[SEARCH] incoming request -> path_qs=%s | raw_q=%r | offset=%s | max=%s | type=%r | user_id=%r | init_data_len=%s",
        request.path_qs,
        raw_q,
        offset,
        max_res,
        file_type,
        url_user_id,
        len(raw_init_data or ""),
    )

    q = _clean_search_query(raw_q)
    _emit(logging.INFO, "[SEARCH] cleaned query = %r | meaningful chars = %s", q, len(re.sub(r"[^a-zA-Z0-9]", "", q or "")))

    active_user_id = None

    if url_user_id.isdigit():
        active_user_id = int(url_user_id)
        _emit(logging.INFO, "[SEARCH] Found direct numeric user_id parameter in URL: %s", active_user_id)
    else:
        extracted_id = _verify_and_extract_user(raw_init_data)
        if extracted_id:
            active_user_id = extracted_id
            _emit(logging.INFO, "[SEARCH] Extracted user_id from init_data token: %s", active_user_id)

    if not active_user_id:
        active_user_id = int(ADMINS[0]) if ADMINS else 1169128654
        _emit(logging.WARNING, "[SEARCH] No user session found. Applying safe database cache fallback ID: %s", active_user_id)

    if not q or len(q) < 3:
        _emit(logging.WARNING, "[SEARCH] rejected early. Raw=%r Cleaned=%r is too short.", raw_q, q)
        return web.json_response({"files": [], "total_results": 0, "next_offset": ""})

    bot_client = request.app.get("bot_client")
    if not bot_client:
        _emit(logging.ERROR, "[SEARCH] Core framework offline (bot_client missing).")
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
                "from_user": type("MockUser", (object,), {"id": active_user_id})(),
                "reply_text": dummy_reply,
                "reply_photo": dummy_reply,
                "reply": dummy_reply,
            }
        )()

        _emit(logging.INFO, "[SEARCH] calling auto_filter with from_user.id=%s and text=%r", active_user_id, q)
        await auto_filter(bot_client, mock_msg)

        key = f"{DUMMY_CHAT_ID}-1"
        cached_results = temp.GETALL.get(key, [])

        _emit(logging.INFO, "[SEARCH] cache key=%s | cached_results_count=%s", key, len(cached_results) if cached_results else 0)

        if cached_results:
            files = cached_results[offset: offset + max_res]
            total = len(cached_results)
            next_offset = offset + len(files) if total > offset + max_res else ""
            _emit(logging.INFO, "[SEARCH] serving from cache. total=%s | returned=%s | next_offset=%r", total, len(files), next_offset)
        else:
            files, next_offset, total = await get_search_results(
                query=q.lower(),
                file_type=file_type,
                max_results=max_res,
                offset=offset,
            )
            _emit(logging.INFO, "[SEARCH] MongoDB fallback finished. total=%s | returned=%s | next_offset=%r", total, len(files), next_offset)

        return web.json_response(
            {
                "files": [_serialize_file(f) for f in files],
                "total_results": total,
                "next_offset": next_offset,
            }
        )
    except Exception as exc:
        _emit_exception("Unified Filter Search API error for query %r: %s", q, exc)
        return web.json_response({"error": "Search failed"}, status=500)


@api_routes.get("/api/recent")
async def api_recent(request: web.Request) -> web.Response:
    try:
        max_res = min(max(1, int(request.rel_url.query.get("max", 20))), 50)
    except Exception:
        max_res = 20

    _emit(logging.INFO, "[RECENT] request -> path_qs=%s | max=%s", request.path_qs, max_res)

    try:
        cursor = Media.find({}).sort("$natural", -1).limit(max_res)
        files = await cursor.to_list(length=max_res)
        _emit(logging.INFO, "[RECENT] returning %s files", len(files))
        return web.json_response({"files": [_serialize_file(f) for f in files]})
    except Exception as exc:
        _emit_exception("Recent API error: %s", exc)
        return web.json_response({"error": "Failed to load recent files"}, status=500)


async def _fetch_and_cache_stats(bot_client) -> None:
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    total_files = await Media.count_documents({})
    total_users = await users_db.total_users_count()
    total_chats = await users_db.total_chat_count()

    subscriber_count = await get_channel_subscriber_count(bot_client, AUTH_CHANNEL)
    _emit(logging.INFO, "AUTH_CHANNEL=%s | subscriber_count=%s", AUTH_CHANNEL, subscriber_count)
    latest_promo_text = "Comming Soon 🔜"

    try:
        size = await users_db.get_db_size()
        free = max(0, 536870912 - int(size))
        used_storage = get_size(size)
        free_storage = get_size(free)
    except Exception as e:
        _emit(logging.WARNING, "Storage size calculation failed: %s", e, exc_info=True)
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

    _emit(
        logging.INFO,
        "Stats cache refreshed. files=%s users=%s chats=%s expires_at=%s",
        total_files,
        total_users,
        total_chats,
        _CACHE_EXPIRE_TIME.isoformat(timespec="seconds"),
    )


@api_routes.get("/api/stats")
async def api_stats(request: web.Request) -> web.Response:
    global _STATS_CACHE, _CACHE_EXPIRE_TIME

    force_refresh = request.rel_url.query.get("refresh", "").lower() == "true"
    now = datetime.datetime.now()

    bot_client = request.app.get("bot_client")
    if not bot_client:
        _emit(logging.ERROR, "[STATS] Core framework offline (bot_client missing).")
        return web.json_response({"error": "Core framework offline"}, status=503)

    try:
        async with _STATS_LOCK:
            if force_refresh or not _STATS_CACHE or not _CACHE_EXPIRE_TIME or now >= _CACHE_EXPIRE_TIME:
                _emit(logging.INFO, "[STATS] cache miss/refresh requested. force_refresh=%s", force_refresh)
                await _fetch_and_cache_stats(bot_client)
            else:
                _emit(logging.INFO, "[STATS] cache hit. using cached payload.")
        return web.json_response(_STATS_CACHE)
    except Exception as exc:
        _emit_exception("Cached Stats API error: %s", exc)
        return web.json_response({"error": "Stats unavailable"}, status=500)


@api_routes.post("/api/send_file")
async def api_send_file(request: web.Request) -> web.Response:
    try:
        from pyrogram.enums import ChatType
        from plugins.pm_filter import cb_handler

        payload = await request.json()
        _emit(logging.INFO, "[SEND_FILE] incoming JSON keys: %s", list(payload.keys()))

        raw_file_id = payload.get("file_id")
        user_id = payload.get("user_id")
        init_data = payload.get("init_data")
        is_protected = bool(payload.get("protect", False))

        _emit(
            logging.INFO,
            "[SEND_FILE] payload snapshot -> file_id=%r | user_id=%r | init_data_len=%s | protect=%s | is_send_all=%s",
            raw_file_id,
            user_id,
            len(init_data or ""),
            is_protected,
            payload.get("is_send_all"),
        )

        if not user_id:
            user_id = _verify_and_extract_user(init_data)

        if not user_id:
            _emit(logging.WARNING, "[SEND_FILE] rejected: user_id missing and init_data could not be parsed.")
            return web.json_response({"status": "redirect_required"}, status=200)

        user_id = int(user_id)
        _emit(logging.INFO, "[SEND_FILE] Final destination user_id=%s", user_id)

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
                "reply": mock_reply_func,
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
                "edit_message_reply_markup": lambda *args, **kwargs: asyncio.sleep(0),
            }
        )()

        _emit(
            logging.INFO,
            "[SEND_FILE] forwarding to cb_handler -> user_id=%s | data=%r",
            user_id,
            f"{prefix}#{raw_file_id}",
        )
        asyncio.create_task(cb_handler(bot_client, mock_query))

        return web.json_response({"status": "direct_sent"}, status=200)

    except Exception as global_exc:
        _emit_exception("Global pipeline exception caught inside forwarding proxy route layout: %s", global_exc)
        return web.json_response({"status": "redirect_required"}, status=200)
