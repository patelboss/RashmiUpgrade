"""
plugins/pm_filter.py — Group-message entry point for the filter/search flow.

This file used to contain ~1500 lines covering everything from the group
message handler down to the callback dispatcher and the search/spell-check
engine. It has been split into three files for readability and easier
maintenance:

    plugins/pm_filter.py            (this file) — group message entry point
    plugins/pm_filter_search.py     — auto_filter / spell-check / manual_filters engine
    plugins/pm_filter_callbacks.py  — all callback_query handlers (pagination,
                                       spell suggestions, the main dispatcher)
    plugins/pm_filter_state.py      — shared in-memory caches used by all three

Pyrogram auto-discovers handlers from every .py file under the `plugins/`
package root (see bot.py -> Client(plugins={"root": "plugins"})), so this
split does not require any change to how the bot loads plugins.

No logic changed during this split — only the file boundaries moved.
All user-facing strings now go through langs.i18n.get()/get_btn() instead
of hardcoded literals. DEBUG_MODE logging added at each significant step.
"""

import asyncio
import logging

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import SUPPORT_CHAT_ID, DEBUG_MODE
from database.users_chats_db import db
from langs.i18n import get, get_btn, DEFAULT_LANG

# Importing these registers their handlers with Pyrogram (decorators run on
# import) and also makes the functions available to this module.
from plugins.pm_filter_search import auto_filter, manual_filters  # noqa: F401
from plugins.pm_filter_callbacks import (  # noqa: F401
    donation_callback, next_page, advantage_spoll_choker, cb_handler,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.group & filters.text & filters.incoming & ~filters.regex(r"^/"))
async def give_filter(client, message):
    chat_id = message.chat.id
    user = message.from_user  # Get the user object
    user_id = user.id if user else 0  # Fallback to 0 if no user ID is available
    lang = await _user_lang(user)

    # Check if the user is an anonymous admin
    if user_id == 0:
        if DEBUG_MODE:
            logger.info("[PMFILTER] anonymous admin blocked | chat_id=%s", chat_id)
        await message.reply_text(
            get(lang, "PMFILTER_ANON_ADMIN"),
            parse_mode=ParseMode.HTML
        )
        return

    try:
        # Check if this is the support chat
        if chat_id == SUPPORT_CHAT_ID:
            if DEBUG_MODE:
                logger.info("[PMFILTER] message in support chat redirected | user_id=%s", user_id)
            # Inline button to join the search group
            inline_button = InlineKeyboardButton(get_btn(lang, "BTN_JOIN_SEARCH_GROUP"), url="https://t.me/Filmykeedha/306")
            reply_markup = InlineKeyboardMarkup([[inline_button]])

            T = await message.reply_text(
                get(lang, "PMFILTER_NOT_SEARCH_GROUP"),
                reply_markup=reply_markup,  # Add the inline button
                disable_web_page_preview=True
            )
            await asyncio.sleep(300)
            await T.delete()
            return

        # If not in the support chat, execute manual and auto-filter logic
        if DEBUG_MODE:
            logger.info("[PMFILTER] dispatching manual_filters + auto_filter | chat_id=%s user_id=%s", chat_id, user_id)
        L = await message.reply_text(get(lang, "PMFILTER_GROUP_BAN_NOTICE"), disable_web_page_preview=True)
        await manual_filters(client, message)
        await auto_filter(client, message)
        await asyncio.sleep(60)
        await L.delete()
    except FloodWait as e:
        # Handle FloodWait exception
        logger.error(f"FloodWait exception: {e.value} seconds")
        await asyncio.sleep(e.value)
        await message.reply_text(
            get(lang, "PMFILTER_FLOODWAIT", seconds=e.value),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Handle generic exceptions
        logger.error(f"Unexpected exception: {str(e)}")
        await message.reply_text(
            get(lang, "PMFILTER_UNEXPECTED_ERROR", error=str(e)),
            parse_mode=ParseMode.HTML
            )


def get_butto1ns(lang=DEFAULT_LANG):
    buttons = [
        [
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GROUP_EMOJI"), url="https://t.me/Filmykeedha/306"),
            InlineKeyboardButton(get_btn(lang, "BTN_OFFER_CHANNEL"), url="https://t.me/+4dWp2gDjwC43YmJl"),
        ],
        [
            InlineKeyboardButton(get_btn(lang, "BTN_DONATE_MONEY"), callback_data="donation2"),
            InlineKeyboardButton(get_btn(lang, "BTN_MAIN_CHANNEL_EMOJI"), url="https://t.me/+zhtB8CYxfxFhOTM1"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


# NOTE: private_message_handler below was already commented out (disabled)
# in the original file — preserved as-is, still disabled.
"""
@Client.on_message(filters.private & filters.text & filters.incoming)
async def private_message_handler(client, message):
    if message.text.startswith("/"):  # Ignore commands
        return

    p = await message.reply_text(
        "<b>🚫 I am not working here; I only work in groups.</b>\n\n"
        "<b>👉 Explore the options below:</b>",
        reply_markup=get_butto1ns()
    )
    await asyncio.sleep(60)
    await p.delete()
"""
