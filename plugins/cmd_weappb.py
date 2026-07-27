"""
webapp_buttons.py – Independent command module for WebApp triggers.
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Optional

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from info import DEBUG_MODE
from database.users_chats_db import db
from langs.i18n import get, get_btn, DEFAULT_LANG

# ── Logging configuration ───────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Prevent duplicate handlers on reload/import.
if logger.handlers:
    logger.handlers.clear()

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)
logger.propagate = False

logger.info("=" * 72)
logger.info("Loading plugin module: %s", __file__)
logger.info("BASE_URL at import time: %s", os.environ.get("BASE_URL", "<not set>"))
logger.info("Client object at import time: %r", Client)
logger.info("filters.command at import time: %r", filters.command)
logger.info("=" * 72)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


# ── URL Builder ──────────────────────────────────────────────────────────────
def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").strip().rstrip("/")
    if DEBUG_MODE:
        logger.info("[WEBAPP] Resolving WebApp Base URL config. Found string: %r", base)

    if not base:
        logger.warning("BASE_URL is empty.")
        return ""

    if not base.startswith(("https://", "http://")):
        logger.warning("BASE_URL does not look like a valid URL: %r", base)
        return ""

    if base.startswith("http://") and not base.startswith("http://localhost"):
        logger.warning("BASE_URL is HTTP. Telegram Web Apps usually require HTTPS in production.")

    resolved = f"{base}/webapp"
    if DEBUG_MODE:
        logger.info("[WEBAPP] Resolved WebApp URL: %r", resolved)
    return resolved


def _build_webapp_markup(url: str, lang: str) -> InlineKeyboardMarkup:
    if DEBUG_MODE:
        logger.info("[WEBAPP] Building WebApp markup for URL: %r", url)
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(get_btn(lang, "BTN_OPEN_WEBAPP_SEARCH"), web_app=WebAppInfo(url=url))]]
    )


async def _reply_wtry(client: Client, message: Message, source: str) -> None:
    lang = await _user_lang(message.from_user)
    user_id = message.from_user.id if message.from_user else "Unknown"
    chat_id = getattr(message.chat, "id", "Unknown")

    if DEBUG_MODE:
        logger.info(
            "[WTRY] handler entered | source=%s | user_id=%s | chat_id=%s | text=%r",
            source,
            user_id,
            chat_id,
            message.text,
        )

    await message.reply_text(
        get(lang, "WTRY_ALIVE", source=source),
        parse_mode=enums.ParseMode.HTML,
    )


async def _reply_webapp(client: Client, message: Message, source: str) -> None:
    lang = await _user_lang(message.from_user)
    user_id = message.from_user.id if message.from_user else "Unknown"
    chat_id = getattr(message.chat, "id", "Unknown")

    if DEBUG_MODE:
        logger.info(
            "[WEBAPP] handler entered | source=%s | user_id=%s | chat_id=%s | text=%r",
            source,
            user_id,
            chat_id,
            message.text,
        )

    try:
        url = _webapp_url()
        if not url:
            logger.warning("Aborting /webapp dispatch: BASE_URL is empty or invalid.")
            await message.reply_text(
                get(lang, "WEBAPP_NOT_CONFIGURED"),
                parse_mode=enums.ParseMode.HTML,
            )
            return

        try:
            markup = _build_webapp_markup(url, lang)
        except Exception as markup_err:
            logger.exception("Failed to build WebApp markup for user %s.", user_id)
            await message.reply_text(
                get(lang, "WEBAPP_MARKUP_ERROR", error=markup_err),
                parse_mode=enums.ParseMode.HTML,
            )
            return

        try:
            await message.reply_text(
                get(lang, "WEBAPP_SUCCESS", source=source),
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML,
            )
            if DEBUG_MODE:
                logger.info("[WEBAPP] WebApp message sent successfully to user %s via %s", user_id, source)
        except Exception as send_err:
            logger.exception("Failed to send /webapp reply for user %s via %s.", user_id, source)
            await message.reply_text(
                get(lang, "WEBAPP_SEND_ERROR", error=send_err),
                parse_mode=enums.ParseMode.HTML,
            )

    except Exception as exc:
        logger.exception("Unexpected failure inside /webapp handler for user %s via %s.", user_id, source)
        try:
            await message.reply_text(
                get(lang, "WEBAPP_CRASH", error=exc),
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            logger.exception("Could not send /webapp crash message to user %s.", user_id)


# ─
# ── COMMAND: /wtry ───────────────────────────────────────────────────────────
@Client.on_message(filters.command("wtry") & filters.private)
async def wtry_cmd(client: Client, message: Message) -> None:
    await _reply_wtry(client, message, "command")


# ── COMMAND: /webapp ─────────────────────────────────────────────────────────
@Client.on_message(filters.command("webapp") & filters.private)
async def webapp_cmd(client: Client, message: Message) -> None:
    await _reply_webapp(client, message, "command")
