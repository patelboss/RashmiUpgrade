"""
plugins/commands_admin.py — admin-only maintenance commands: /restart,
/channel, /logs, /delete, /deleteall, /scrub, and their callbacks.

Split out of plugins/commands.py (which was 931 lines) purely for
readability. No logic changed, only the file boundary moved. See
plugins/commands.py and plugins/commands_start.py for the other two pieces.

All user-facing strings are served from langs/i18n.py via get() / get_btn().
Debug events are emitted via debug.dlog() — only printed when DEBUG_MODE=true.
"""

import os
import sys
import re
import uuid
import asyncio
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.ia_filterdb import Media, unpack_new_file_id
from database.users_chats_db import db

from info import ADMINS, CHANNELS
from langs.i18n import get, get_btn
from utils import get_size
from debug import dlog

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Temporary RAM cache for scrub confirmations
PURGE_CACHE: dict = {}


# ─────────────────────────────────────────────────────────────────────────────
# /restart  (admin only)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    msg = await bot.send_message(message.chat.id, get(lang, "BOT_RESTARTING"))
    dlog("RESTART", user_id=message.from_user.id)
    await asyncio.sleep(3)
    await msg.edit(get(lang, "BOT_RESTARTED"))
    os.execl(sys.executable, sys.executable, *sys.argv)


# ─────────────────────────────────────────────────────────────────────────────
# /channel  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("channel") & filters.user(ADMINS))
async def channel_info(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    channels = [CHANNELS] if isinstance(CHANNELS, (int, str)) else CHANNELS
    text = "📑 <b>Indexed channels/groups</b>\n"
    for ch in channels:
        chat = await bot.get_chat(ch)
        text += "\n@" + chat.username if chat.username else "\n" + (chat.title or chat.first_name)
    text += f"\n\n<b>Total:</b> {len(CHANNELS)}"
    if len(text) < 4096:
        await message.reply(text, parse_mode=enums.ParseMode.HTML)
    else:
        fname = "indexed_channels.txt"
        with open(fname, "w") as f:
            f.write(text)
        await message.reply_document(fname)
        os.remove(fname)


# ─────────────────────────────────────────────────────────────────────────────
# /logs  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def log_file(bot, message: Message):
    try:
        await message.reply_document("TelegramBot.log")
    except Exception as exc:
        await message.reply(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# /delete  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete_file(bot, message: Message):
    lang  = await db.get_user_lang(message.from_user.id)
    reply = message.reply_to_message
    if not (reply and reply.media):
        return await message.reply(get(lang, "REPLY_TO_FILE"), quote=True)

    msg = await message.reply(get(lang, "PROCESSING"), quote=True)

    for ftype in ("document", "video", "audio"):
        media = getattr(reply, ftype, None)
        if media is not None:
            break
    else:
        return await msg.edit(get(lang, "UNSUPPORTED_FMT"))

    file_id, _ = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({"_id": file_id})
    if result.deleted_count:
        return await msg.edit(get(lang, "FILE_DEL_DB_OK"))

    file_name = re.sub(r"(_|\-|\.|\\+)", " ", str(media.file_name))
    result = await Media.collection.delete_many({
        "file_name": file_name, "file_size": media.file_size, "mime_type": media.mime_type
    })
    if result.deleted_count:
        return await msg.edit(get(lang, "FILE_DEL_DB_OK"))

    result = await Media.collection.delete_many({
        "file_name": media.file_name, "file_size": media.file_size, "mime_type": media.mime_type
    })
    await msg.edit(get(lang, "FILE_DEL_DB_OK") if result.deleted_count else get(lang, "FILE_NOT_IN_DB"))


# ─────────────────────────────────────────────────────────────────────────────
# /deleteall  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("deleteall") & filters.user(ADMINS))
async def delete_all_index(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.reply_text(
        get(lang, "DELETE_ALL_CONFIRM"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_btn(lang, "BTN_YES"),    callback_data="autofilter_delete")],
            [InlineKeyboardButton(get_btn(lang, "BTN_CANCEL"), callback_data="close_data")],
        ]),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r"^autofilter_delete"))
async def delete_all_index_confirm(bot, query):
    lang = await db.get_user_lang(query.from_user.id)
    await Media.collection.drop()
    await query.answer(get(lang, "DELETE_THANK"))
    await query.message.edit(get(lang, "DELETE_ALL_DONE"))


# ─────────────────────────────────────────────────────────────────────────────
# /scrub  — bulk DB purge with pattern matching (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("scrub") & filters.user(ADMINS))
async def scrub_database(client, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    if len(message.command) < 2:
        return await message.reply_text(get(lang, "SCRUB_USAGE"))

    raw_args = message.text.split(maxsplit=1)[1].strip()

    # 1. Parse 'name:' parameter
    pattern = None
    name_match = re.search(r"name:\s*(.*?)(?=\s*size:|$)", raw_args, re.IGNORECASE | re.DOTALL)
    if name_match:
        pattern = name_match.group(1).strip()

    # 2. Parse 'size:' parameter
    size_args = None
    size_match = re.search(r"size:\s*(.*)", raw_args, re.IGNORECASE | re.DOTALL)
    if size_match:
        size_args = size_match.group(1).strip()

    # Fallback if the user didn't use parameters explicitly, treat the whole string as the name
    if not name_match and not size_match:
        pattern = raw_args

    db_query = {}

    # 3. Build File Name Query
    if pattern:
        # Flatten special characters for matching if your database normalizes them,
        # or use directly with wildcards converted safely.
        clean_pattern = re.sub(r'[^a-zA-Z0-9\s\*]', ' ', pattern)
        safe_pat = re.escape(clean_pattern).replace(r"\*", ".*")
        # Removing strict ^ and $ anchors so it behaves like a flexible search string
        db_query["file_name"] = {"$regex": f"{safe_pat}", "$options": "i"}

    # 4. Build Size Filter Query (Handles ranges like >50MB <1GB)
    size_label = "None"
    if size_args:
        size_query = {}
        all_sizes = re.findall(r"([<>])\s*([\d\.]+)\s*([KMG]?B)", size_args.upper())

        labels = []
        for op, val, unit in all_sizes:
            val = float(val)
            mult = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}.get(unit, 1)
            size_bytes = int(val * mult)

            if op == ">":
                size_query["$gt"] = size_bytes
            elif op == "<":
                size_query["$lt"] = size_bytes
            labels.append(f"{op}{val}{unit}")

        if size_query:
            db_query["file_size"] = size_query
            size_label = " ".join(labels)

    if not db_query:
        return await message.reply_text(get(lang, "SCRUB_USAGE"))

    msg = await message.reply_text(get(lang, "SCRUB_SCANNING"))
    try:
        pipeline = [{"$match": db_query}, {"$group": {
            "_id": None, "total_count": {"$sum": 1},
            "max_size": {"$max": "$file_size"}, "min_size": {"$min": "$file_size"}
        }}]
        stats_cur = Media.collection.aggregate(pipeline)
        stats     = await stats_cur.to_list(length=1)
        if not stats:
            return await msg.edit_text(get(lang, "SCRUB_NOT_FOUND", pattern=pattern or "None"))

        stats       = stats[0]
        total_count = stats.get("total_count", 0)
        max_size    = get_size(stats.get("max_size", 0))
        min_size    = get_size(stats.get("min_size", 0))

        samples_cur  = Media.collection.find(db_query).limit(5)
        sample_docs  = await samples_cur.to_list(length=5)
        sample_names = "\n".join([f" ├ <code>{d['file_name']}</code>" for d in sample_docs])

        query_id           = str(uuid.uuid4())[:8]
        PURGE_CACHE[query_id] = db_query

        text = get(lang, "SCRUB_CONFIRM",
                   pattern=pattern or "None", size=size_label,
                   count=total_count, min_size=min_size, max_size=max_size,
                   samples=sample_names)
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_DELETE_ALL_DB"), callback_data=f"purge_yes_{query_id}"),
            InlineKeyboardButton(get_btn(lang, "BTN_CANCEL"),        callback_data=f"purge_no_{query_id}"),
        ]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons),
                            parse_mode=enums.ParseMode.HTML)
        dlog("SCRUB_SCAN", user_id=message.from_user.id,
             extra={"pattern": pattern or "None", "count": total_count})

    except Exception as exc:
        logger.exception("Scrub scan error")
        await msg.edit_text(get(lang, "SCRUB_ERROR", error=str(exc)))


@Client.on_callback_query(filters.regex(r"^purge_(yes|no)_"))
async def handle_purge_confirmation(client, query):
    lang     = await db.get_user_lang(query.from_user.id)
    parts    = query.data.split("_")
    action   = parts[1]           # "yes" or "no"
    query_id = parts[2]

    if str(query.from_user.id) not in [str(a) for a in ADMINS]:
        return await query.answer(get(lang, "SCRUB_ADMIN_ONLY"), show_alert=True)

    if action == "no":
        PURGE_CACHE.pop(query_id, None)
        return await query.message.edit_text(get(lang, "SCRUB_CANCELLED"))

    if action == "yes":
        db_query = PURGE_CACHE.pop(query_id, None)
        if not db_query:
            return await query.answer(get(lang, "SCRUB_EXPIRED"), show_alert=True)

        await query.answer("Deleting... please wait.", show_alert=True)
        try:
            result = await Media.collection.delete_many(db_query)
            await query.message.edit_text(get(lang, "SCRUB_DONE", count=result.deleted_count))
            dlog("SCRUB_DONE", user_id=query.from_user.id,
                 extra={"deleted": result.deleted_count})
        except Exception as exc:
            logger.exception("Scrub delete error")
            await query.message.edit_text(get(lang, "SCRUB_ERROR", error=str(exc)))
