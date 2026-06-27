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


# ── URL Builder ──────────────────────────────────────────────────────────────
def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").strip().rstrip("/")
    logger.info("Resolving WebApp Base URL config. Found string: %r", base)

    if not base:
        logger.warning("BASE_URL is empty.")
        return ""

    if not base.startswith(("https://", "http://")):
        logger.warning("BASE_URL does not look like a valid URL: %r", base)
        return ""

    if base.startswith("http://") and not base.startswith("http://localhost"):
        logger.warning("BASE_URL is HTTP. Telegram Web Apps usually require HTTPS in production.")

    resolved = f"{base}/webapp"
    logger.info("Resolved WebApp URL: %r", resolved)
    return resolved


def _build_webapp_markup(url: str) -> InlineKeyboardMarkup:
    logger.info("Building WebApp markup for URL: %r", url)
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))]]
    )


async def _reply_wtry(client: Client, message: Message, source: str) -> None:
    user_id = message.from_user.id if message.from_user else "Unknown"
    chat_id = getattr(message.chat, "id", "Unknown")

    logger.info(
        "wtry handler entered | source=%s | user_id=%s | chat_id=%s | text=%r",
        source,
        user_id,
        chat_id,
        message.text,
    )

    await message.reply_text(
        "✅ <b>wtry reached this file and the handler is alive.</b>\n\n"
        f"<b>Source:</b> <code>{source}</code>",
        parse_mode=enums.ParseMode.HTML,
    )


async def _reply_webapp(client: Client, message: Message, source: str) -> None:
    user_id = message.from_user.id if message.from_user else "Unknown"
    chat_id = getattr(message.chat, "id", "Unknown")

    logger.info(
        "webapp handler entered | source=%s | user_id=%s | chat_id=%s | text=%r",
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
                "<b>Web App URL is not configured.</b>\n"
                "Set the <code>BASE_URL</code> environment variable to your server URL.",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        try:
            markup = _build_webapp_markup(url)
        except Exception as markup_err:
            logger.exception("Failed to build WebApp markup for user %s.", user_id)
            await message.reply_text(
                f"<b>❌ Could not build Web App button:</b>\n<code>{markup_err}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        try:
            await message.reply_text(
                "<b>🎬 AutoFile Media Search</b>\n\n"
                "Tap the button below to open the media search app directly in Telegram.\n\n"
                f"<b>Path:</b> <code>{source}</code>",
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML,
            )
            logger.info("WebApp message sent successfully to user %s via %s", user_id, source)
        except Exception as send_err:
            logger.exception("Failed to send /webapp reply for user %s via %s.", user_id, source)
            await message.reply_text(
                f"<b>❌ Failed to send WebApp message:</b>\n<code>{send_err}</code>",
                parse_mode=enums.ParseMode.HTML,
            )

    except Exception as exc:
        logger.exception("Unexpected failure inside /webapp handler for user %s via %s.", user_id, source)
        try:
            await message.reply_text(
                f"<b>❌ /webapp crashed:</b>\n<code>{exc}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            logger.exception("Could not send /webapp crash message to user %s.", user_id)


# ── EARLY PROBE ─────────────────────────────────────────────────────────────
# This catches the commands even if a normal command filter is being weird
# or another plugin is swallowing /commands later.
"""
@Client.on_message(
    filters.private & filters.incoming & filters.text & filters.regex(r"^/(wtry|webapp)(?:\s|$)"),
    group=-999,
)
async def webapp_command_probe(client: Client, message: Message) -> None:
    text = (message.text or "").strip()
    logger.info("Probe handler saw command-like text: %r", text)

    if text.startswith("/wtry"):
        await _reply_wtry(client, message, "probe")
        return

    if text.startswith("/webapp"):
        await _reply_webapp(client, message, "probe")
        return

"""
# ── COMMAND: /wtry ───────────────────────────────────────────────────────────
@Client.on_message(filters.command("wtry") & filters.private)
async def wtry_cmd(client: Client, message: Message) -> None:
    await _reply_wtry(client, message, "command")


# ── COMMAND: /webapp ─────────────────────────────────────────────────────────
@Client.on_message(filters.command("webapp") & filters.private)
async def webapp_cmd(client: Client, message: Message) -> None:
    await _reply_webapp(client, message, "command")
