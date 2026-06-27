"""
webapp_cmd.py – Registers /webapp command that sends the Telegram Web App button.
Also handles the webapp_data update (when the web app sends data back to the bot).
"""
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from info import ADMINS
from utils import temp

logger = logging.getLogger(__name__)


def _webapp_url() -> str:
    """Build the Web App URL served by this bot."""
    # BASE_URL is set in env; fallback to a generic path.
    import os
    base = os.environ.get("BASE_URL", "").rstrip("/")
    if base:
        return f"{base}/webapp"
    return ""


@Client.on_message(filters.command("webapp") & filters.incoming)
async def webapp_cmd(client: Client, message: Message) -> None:
    """Send an inline button that opens the Telegram Web App."""
    url = _webapp_url()
    if not url:
        await message.reply_text(
            "<b>Web App URL is not configured.</b>\n"
            "Set the <code>BASE_URL</code> environment variable to your server URL.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))],
    ])
    await message.reply_text(
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.via_bot & filters.incoming, group=100)
async def webapp_data_handler(client: Client, message: Message) -> None:
    """
    Handle data sent from the Web App via sendData().
    Pyrogram delivers this as a Message with web_app_data attribute.
    """
    if not (hasattr(message, "web_app_data") and message.web_app_data):
        return

    import json
    try:
        payload = json.loads(message.web_app_data.data)
    except (ValueError, AttributeError):
        return

    action  = payload.get("action")
    file_id = payload.get("file_id")

    if action == "get_file" and file_id:
        from database.ia_filterdb import get_file_details
        from utils import get_size, clean_file_name
        from variables import CUSTOM_FILE_CAPTION
        from info import PROTECT_CONTENT, OFR_CNL

        files = await get_file_details(file_id)
        if not files:
            await message.reply_text("⚠️ File not found in database.")
            return

        f = files[0]
        title     = clean_file_name(f.file_name)
        size      = get_size(f.file_size)
        caption   = f.caption or ""

        if CUSTOM_FILE_CAPTION:
            try:
                caption = CUSTOM_FILE_CAPTION.format(
                    file_name    = title or "",
                    file_size    = size  or "",
                    file_caption = caption or "",
                )
            except Exception:
                caption = caption or title

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Offer Zone 🤑", url=OFR_CNL)],
        ])
        try:
            await client.send_cached_media(
                chat_id         = message.from_user.id,
                file_id         = f.file_id,
                caption         = caption or title,
                protect_content = PROTECT_CONTENT,
                reply_markup    = btn,
            )
        except Exception as exc:
            logger.error("Failed to send file from Web App: %s", exc)
            await message.reply_text("⚠️ Could not send the file. Please try again.")
