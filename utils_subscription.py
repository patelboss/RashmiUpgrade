"""
utils_subscription.py — force-subscribe channel check (is_subscribed), split
out of utils.py. See utils_state.py for the module-split overview.
"""

import logging

from pyrogram import enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery

from info import *
from variables import AUTH_CHANNELS

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def is_subscribed(bot, query):
    missing_channels = []

    if DEBUG_MODE:
        logger.info(
            "[SUB] is_subscribed entered | user_id=%s | query_type=%s | total_channels=%s",
            getattr(getattr(query, "from_user", None), "id", None),
            type(query).__name__,
            len(AUTH_CHANNELS),
        )

    for channel_id in AUTH_CHANNELS:
        try:
            if DEBUG_MODE:
                logger.info(
                    "[SUB] checking channel_id=%s for user_id=%s",
                    channel_id,
                    query.from_user.id,
                )
            user = await bot.get_chat_member(int(channel_id), query.from_user.id)
            if DEBUG_MODE:
                logger.info(
                    "[SUB] channel_id=%s status=%s",
                    channel_id,
                    getattr(user, "status", None),
                )
            if user.status == enums.ChatMemberStatus.BANNED:
                if DEBUG_MODE:
                    logger.warning(
                        "[SUB] user_id=%s is banned in channel_id=%s",
                        query.from_user.id,
                        channel_id,
                    )
                return False
        except UserNotParticipant:
            if DEBUG_MODE:
                logger.info(
                    "[SUB] user_id=%s is not participant in channel_id=%s",
                    query.from_user.id,
                    channel_id,
                )
            missing_channels.append(channel_id)
            continue
        except Exception as e:
            logger.error(
                "Error while checking channel %s for user %s: %s",
                channel_id,
                query.from_user.id,
                e,
            )

    if missing_channels:
        if DEBUG_MODE:
            logger.info(
                "[SUB] missing channels for user_id=%s -> %s",
                query.from_user.id,
                missing_channels,
            )
        join_buttons = []
        for channel_id in missing_channels:
            if DEBUG_MODE:
                logger.info("[SUB] fetching chat info for missing channel_id=%s", channel_id)
            channel = await bot.get_chat(int(channel_id))
            join_buttons.append(
                InlineKeyboardButton(f"Join {channel.title}", url=channel.invite_link)
            )
        reply_markup = InlineKeyboardMarkup([join_buttons])

        if isinstance(query, CallbackQuery):
            if DEBUG_MODE:
                logger.info("[SUB] responding via CallbackQuery prompt")
            await query.answer(
                text="Please join all required channels & Unmute Them to use the bot.\nTap on Files Again",
                show_alert=True
            )
            await query.message.reply(
                "Join the channels using the buttons below.\nTap on Join Then Unmute\nTap On Files Again To Get Files",
                reply_markup=reply_markup
            )
        elif isinstance(query, InlineQuery):
            if DEBUG_MODE:
                logger.info("[SUB] responding via InlineQuery prompt")
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="Please subscribe to all required channels.",
                switch_pm_parameter="subscribe"
            )
        else:
            if DEBUG_MODE:
                logger.info("[SUB] responding via Message prompt")
            await query.reply(
                "You need to join all the required channels & Unmute Them to get the files.",
                reply_markup=reply_markup
            )
        return False

    if DEBUG_MODE:
        logger.info("[SUB] user_id=%s is subscribed to all required channels", query.from_user.id)
    return True
