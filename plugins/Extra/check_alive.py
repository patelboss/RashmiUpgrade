
import time
import random
import logging

from pyrogram import Client, filters
from info import DEBUG_MODE
from database.users_chats_db import db
from langs.i18n import get, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

CMD = ["/", "."]


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.command("alive", CMD))
async def check_alive(_, message):
    lang = await _user_lang(message.from_user)
    if DEBUG_MODE:
        logger.info("[ALIVE] /alive requested | user_id=%s", message.from_user.id if message.from_user else None)
    await message.reply_text(get(lang, "ALIVE_MSG"))


@Client.on_message(filters.command("ping", CMD))
async def ping(_, message):
    lang = await _user_lang(message.from_user)
    start_t = time.time()
    rm = await message.reply_text(get(lang, "PING_PLACEHOLDER"))
    end_t = time.time()
    time_taken_s = (end_t - start_t) * 1000
    if DEBUG_MODE:
        logger.info("[ALIVE] /ping | time_taken_ms=%.3f user_id=%s", time_taken_s, message.from_user.id if message.from_user else None)
    await rm.edit(get(lang, "PING_RESULT", time_taken=f"{time_taken_s:.3f}"))
