"""
webapp_cmd.py – Registers /webapp command that sends the Telegram Web App button.
Also handles inline deep-linking queries when data is passed from the Web App interface.
"""
import logging
import json
import os

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
import variables
from database.ia_filterdb import get_file_details
from utils import get_size, clean_file_name

# Configure structured runtime logger
logger = logging.getLogger("Rashmibot.webapp")
logger.setLevel(logging.INFO)


def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").rstrip("/")
    logger.info("Resolving WebApp Base URL config. Found string: '%s'", base)
    if base:
        return f"{base}/webapp"
    return ""


@Client.on_message(filters.command("webapp") & filters.incoming)
async def webapp_cmd(client: Client, message: Message) -> None:
    """Send an inline button that opens the Telegram Web App."""
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /webapp triggered by user ID: %s", user_id)
    
    url = _webapp_url()
    if not url:
        logger.warning("Aborting /webapp command dispatch: BASE_URL environment string empty or invalid.")
        await message.reply_text(
            "<b>Web App URL is not configured.</b>\n"
            "Set the <code>BASE_URL</code> environment variable to your server URL.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))],
    ])
    
    logger.info("Successfully dispatched markup containing WebApp Target: %s", url)
    await message.reply_text(
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.text & filters.incoming, group=100)
async def webapp_inline_handler(client: Client, message: Message) -> None:
    """
    Handles deep-linked extraction tokens passed back by the interface layout.
    """
    if not message.text or not message.text.startswith("get_"):
        return

    user_id = message.from_user.id if message.from_user else "Unknown"
    file_id = message.text.replace("get_", "").strip()
    logger.info("Token extraction pipeline hit! User: %s, Processing Key ID: %s", user_id, file_id)

    if not file_id:
        logger.warning("Extraction aborted: Extracted file token payload empty.")
        return

    try:
        logger.info("Querying MongoDB layer for target ID matching: %s", file_id)
        files = await get_file_details(file_id)
        
        if not files:
            logger.warning("Data fetch returned empty for token: %s", file_id)
            await message.reply_text("⚠️ File not found in database.")
            return

        f = files
        title = clean_file_name(f.file_name)
        size = get_size(f.file_size)
        caption = f.caption or ""
        
        logger.info("File resolving payload loaded. Original Name: %s | Size: %s", f.file_name, size)

        # Dynamic variable fallback extractions matching current database environment logs
        custom_caption = getattr(variables, "CUSTOM_FILE_CAPTION", "")
        protect_content = getattr(variables, "PROTECT_CONTENT", False)
        ofr_cnl = getattr(variables, "OFR_CNL", "https://t.me/Filmykeedha")

        if custom_caption:
            try:
                caption = custom_caption.format(
                    file_name=title or "",
                    file_size=size or "",
                    file_caption=caption or "",
                )
            except Exception as formatting_err:
                logger.error("Caption metadata string parsing failed: %s", formatting_err)
                caption = caption or title

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Offer Zone 🤑", url=ofr_cnl)],
        ])
        
        logger.info("Sending cached document media map payload stream to target chat index: %s", user_id)
        await client.send_cached_media(
            chat_id=user_id,
            file_id=f.file_id,
            caption=caption or title,
            protect_content=protect_content,
            reply_markup=btn,
        )
        logger.info("Cached media stream delivered successfully.")

    except Exception as exc:
        logger.error("Critical failure during handling of file dispatch loop: %s", exc, exc_info=True)
        await message.reply_text("⚠️ Could not process or send the requested file record.")
