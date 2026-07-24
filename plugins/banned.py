import logging

from pyrogram import Client, filters
from utils import temp
from pyrogram.types import Message
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import SUPPORT_CHAT, DEBUG_MODE
from langs.i18n import get, get_btn, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


async def banned_users(_, client, message: Message):
    return (
        message.from_user is not None or not message.sender_chat
    ) and message.from_user.id in temp.BANNED_USERS

banned_user = filters.create(banned_users)

async def disabled_chat(_, client, message: Message):
    return message.chat.id in temp.BANNED_CHATS

disabled_group=filters.create(disabled_chat)


@Client.on_message(filters.private & banned_user & filters.incoming)
async def ban_reply(bot, message):
    lang = await _user_lang(message.from_user)
    ban = await db.get_ban_status(message.from_user.id)
    if DEBUG_MODE:
        logger.info("[BANNED] banned user attempted access | user_id=%s", message.from_user.id)
    await message.reply(get(lang, "BANNED_USER_REPLY", ban_reason=ban["ban_reason"]))

@Client.on_message(filters.group & disabled_group & filters.incoming)
async def grp_bd(bot, message):
    lang = await _user_lang(message.from_user)
    buttons = [[
        InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_PLAIN"), url=f'https://t.me/{SUPPORT_CHAT}')
    ]]
    reply_markup=InlineKeyboardMarkup(buttons)
    vazha = await db.get_chat(message.chat.id)
    if DEBUG_MODE:
        logger.info("[BANNED] leaving disabled chat | chat_id=%s reason=%s", message.chat.id, vazha['reason'])
    k = await message.reply(
        text=get(lang, "GRP_DISABLED_NOTICE_BILINGUAL", reason=vazha['reason']),
        reply_markup=reply_markup)
    try:
        await k.pin()
    except:
        pass
    await bot.leave_chat(message.chat.id)
