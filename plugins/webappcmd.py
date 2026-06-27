"""
webapp_cmd.py – Registers /webapp command that sends the Telegram Web App button.
Also handles inline deep-linking queries when data is passed from the Web App interface.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

# ---------------------------------------------------------------------
# Bootstrap logger first so import failures are visible immediately.
# ---------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    _stdout_handler = logging.StreamHandler(sys.stdout)
    _stdout_handler.setLevel(logging.INFO)
    _stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(_stdout_handler)

logger.propagate = False

logger.info("=" * 72)
logger.info("Loading plugin module: %s", __file__)
logger.info("BASE_URL at import time: %s", os.environ.get("BASE_URL", "<not set>"))
logger.info("=" * 72)

try:
    from pyrogram import Client, filters, enums
    from pyrogram.types import (
        InlineKeyboardButton,
        InlineKeyboardMarkup,
        Message,
        WebAppInfo,
    )

    import variables
    from database.ia_filterdb import get_file_details
    from utils import clean_file_name, get_size

    logger.info("Top-level imports for webapp_cmd.py completed successfully.")

except Exception as import_error:
    print(f"CRITICAL COMPILATION ERROR IN WEBAPP PLUGIN: {import_error}", file=sys.stderr)
    logger.exception("Webapp plugin failed to initialize top-level imports:")
    raise


def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").strip().rstrip("/")
    logger.info("Resolving WebApp BASE_URL. Raw resolved string: %r", base)

    if not base:
        return ""

    if not base.startswith(("https://", "http://")):
        logger.warning("BASE_URL does not look like a valid URL: %r", base)
        return ""

    # Telegram Web Apps are expected to use HTTPS in production.
    if base.startswith("http://") and not base.startswith("http://localhost"):
        logger.warning("BASE_URL is HTTP. Telegram Web Apps usually require HTTPS in production.")

    return f"{base}/webapp"


def _field(obj: Any, key: str, default: Any = None) -> Any:
    """Read a field from either a dict-like object or an attribute-based object."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _extract_file_id(payload: str) -> str:
    """
    Accepts either:
    - get_<file_id>
    - JSON like {"file_id":"..."}
    - raw file_id
    """
    if not payload:
        return ""

    payload = payload.strip()

    if payload.startswith("get_"):
        return payload[4:].strip()

    if payload.startswith("{") and payload.endswith("}"):
        try:
            data = json.loads(payload)
            if isinstance(data, dict):
                for key in ("file_id", "id", "fileid", "token"):
                    value = data.get(key)
                    if value:
                        return str(value).strip()
        except Exception:
            logger.exception("Failed to parse JSON payload from web app data.")

    return payload.strip()


@Client.on_message(filters.command("wtry") & filters.private)
async def wtry_cmd(client: Client, message: Message) -> None:
    """Diagnostic command to verify whether WebApp URL and plugin bootstrapping work."""
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /wtry triggered by user ID: %s", user_id)

    url = _webapp_url()
    logger.info("wtry resolved URL: %r", url)

    if not url:
        await message.reply_text(
            "<b>Web App URL is not configured.</b>\n"
            "Set the <code>BASE_URL</code> environment variable to your server URL.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))]]
    )

    await message.reply_text(
        "<b>✅ Web App configuration looks OK.</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.command("webapp") & filters.private)
async def webapp_cmd(client: Client, message: Message) -> None:
    """Send an inline button that opens the Telegram Web App."""
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /webapp triggered by user ID: %s", user_id)

    url = _webapp_url()
    if not url:
        logger.warning("Aborting /webapp dispatch: BASE_URL is empty or invalid.")
        await message.reply_text(
            "<b>Web App URL is not configured.</b>\n"
            "Set the <code>BASE_URL</code> environment variable to your server URL.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))]]
    )

    logger.info("Dispatching WebApp button with URL: %s", url)
    await message.reply_text(
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.private & filters.incoming & filters.text, group=100)
async def webapp_inline_handler(client: Client, message: Message) -> None:
    """
    Handles deep-linked extraction tokens passed back by the interface layout.
    """
    text = (message.text or "").strip()
    if not text:
        return

    # Keep this handler narrow so it doesn't eat all incoming text.
    if not (text.startswith("get_") or text.startswith("{") or text):
        return

    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        logger.warning("Incoming message without from_user; skipping.")
        return

    file_id = _extract_file_id(text)
    logger.info("Token pipeline hit. User: %s | Raw payload: %r | Parsed file_id: %r", user_id, text, file_id)

    if not file_id:
        logger.warning("Extraction aborted: parsed file_id is empty.")
        await message.reply_text("⚠️ Invalid request payload.")
        return

    try:
        logger.info("Querying database for file details: %s", file_id)
        files = await get_file_details(file_id)

        if not files:
            logger.warning("Database returned no file for token: %s", file_id)
            await message.reply_text("⚠️ File not found in database.")
            return

        # get_file_details may return a record or a list/tuple depending on implementation.
        f = files[0] if isinstance(files, (list, tuple)) else files

        original_name = _field(f, "file_name", "") or ""
        original_size = _field(f, "file_size", 0) or 0
        original_caption = _field(f, "caption", "") or ""
        cached_file_id = _field(f, "file_id", "") or ""

        if not cached_file_id:
            logger.warning("File record found but file_id is missing for token: %s", file_id)
            await message.reply_text("⚠️ File record is incomplete.")
            return

        title = clean_file_name(str(original_name or file_id))
        try:
            size = get_size(int(original_size))
        except Exception:
            logger.exception("Failed to format file size for file_id=%s", file_id)
            size = ""

        caption = original_caption
        logger.info("Loaded file record. name=%r size=%r", original_name, size)

        custom_caption = getattr(variables, "CUSTOM_FILE_CAPTION", "")
        protect_content = bool(getattr(variables, "PROTECT_CONTENT", False))
        ofr_cnl = getattr(variables, "OFR_CNL", "https://t.me/Filmykeedha")

        if custom_caption:
            try:
                caption = custom_caption.format(
                    file_name=title or "",
                    file_size=size or "",
                    file_caption=caption or "",
                )
            except Exception as formatting_err:
                logger.exception("Caption formatting failed for file_id=%s", file_id)
                caption = caption or title
                logger.error("Caption metadata string parsing failed: %s", formatting_err)

        btn = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Join Offer Zone 🤑", url=ofr_cnl)]]
        )

        logger.info("Sending cached media to user %s using file_id=%s", user_id, cached_file_id)
        await client.send_cached_media(
            chat_id=user_id,
            file_id=cached_file_id,
            caption=caption or title,
            protect_content=protect_content,
            reply_markup=btn,
        )
        logger.info("Cached media delivered successfully to user %s", user_id)

    except Exception as exc:
        logger.error("Critical failure during file dispatch: %s", exc, exc_info=True)
        await message.reply_text("⚠️ Could not process or send the requested file record.")
