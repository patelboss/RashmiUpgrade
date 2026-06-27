"""
webapp_buttons.py – Independent command module for WebApp triggers.
"""
import logging
import os
import sys

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

# Prevent log duplication issues if re-imported
if logger.hasHandlers():
    logger.handlers.clear()

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stdout_handler.setFormatter(formatter)
logger.addHandler(stdout_handler)


# ── URL Builder ──────────────────────────────────────────────────────────────
def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").rstrip("/")
    logger.info("Resolving WebApp Base URL config. Found string: '%s'", base)
    if base:
        return f"{base}/webapp"
    return ""


# ── COMMAND: /wtry ───────────────────────────────────────────────────────────
@Client.on_message(filters.command('wtry') & filters.incoming)
async def wtry_cmd(client: Client, message: Message) -> None:
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /wtry successfully fired by user ID: %s", user_id)
    await message.reply_text(
        "<b>Testing Phase 1 Active</b>\n\nHandler is responsive inside webappcmd file.",
        parse_mode=enums.ParseMode.HTML,
    )


# ── COMMAND: /webapp ─────────────────────────────────────────────────────────
@Client.on_message(filters.command("webapp") & filters.private)
async def webapp_cmd(client: Client, message: Message) -> None:
    """Send an inline button that opens the Telegram Web App."""
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /webapp triggered by user ID: %s", user_id)

    try:
        url = _webapp_url()
        logger.info("Resolved /webapp URL: %r", url)

        if not url:
            logger.warning("Aborting /webapp dispatch: BASE_URL is empty or invalid.")
            await message.reply_text(
                "<b>Web App URL is not configured.</b>\n"
                "Set the <code>BASE_URL</code> environment variable to your server URL.",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        try:
            markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))]]
            )
            logger.info("WebApp markup created successfully for user %s", user_id)
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
                "Tap the button below to open the media search app directly in Telegram.",
                reply_markup=markup,
                parse_mode=enums.ParseMode.HTML,
            )
            logger.info("WebApp message sent successfully to user %s", user_id)
        except Exception as send_err:
            logger.exception("Failed to send /webapp reply for user %s.", user_id)
            await message.reply_text(
                f"<b>❌ Failed to send WebApp message:</b>\n<code>{send_err}</code>",
                parse_mode=enums.ParseMode.HTML,
            )

    except Exception as exc:
        logger.exception("Unexpected failure inside /webapp handler for user %s.", user_id)
        try:
            await message.reply_text(
                f"<b>❌ /webapp crashed:</b>\n<code>{exc}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            logger.exception("Could not send /webapp crash message to user %s.", user_id)
