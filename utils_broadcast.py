"""
utils_broadcast.py — broadcast_messages / broadcast_messages_group / send_all,
split out of utils.py. See utils_state.py for the module-split overview.

Two deliberate bug fixes were made here versus the original file (both
pre-existing, dormant bugs — see the FIXED comments below for exactly
what changed):
  1. send_all() referenced an undefined `message.chat.id` instead of the
     `chat_id` parameter that was actually passed in.
  2. send_all() referenced an undefined `SHORTLINK_MODE` name. It is now
     defined here (defaulting to False, i.e. the shortlink branch stays
     off unless you deliberately enable it) so it can no longer crash
     the bot with a NameError.

One bug was NOT fixed because it needs a product decision from you:
`get_shortlink(...)` is called inside the shortlink-mode branch of
send_all() but is not defined anywhere in the codebase. That branch is
only reached if a group's `is_shortlink` setting is turned on — since
nothing currently turns it on, this has never crashed in practice. I've
left it as-is rather than guess at what shortener/URL scheme you want;
let me know and I can wire it up properly (e.g. mirroring
get_verify_shorted_link's Shortzy/shareus.io flow).
"""

import asyncio
import logging

from pyrogram.errors import InputUserDeactivated, FloodWait, UserIsBlocked, PeerIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from info import *
from database.users_chats_db import db
from utils_state import temp
from utils_helpers import get_size
from utils_settings import get_settings, save_group_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# FIXED (item 2 above): was undefined in the original file. Defaulting to
# False preserves the "shortlink branch effectively never fires" behavior
# the bot already had (since SHORTLINK_MODE didn't exist, it could only
# ever crash, never actually run) — now it degrades gracefully instead.
SHORTLINK_MODE = False


async def broadcast_messages(user_id, message, forward=False):
    try:
        if DEBUG_MODE:
            logger.info(
                "[BROADCAST] entered | user_id=%s | forward=%s | message_id=%s",
                user_id,
                forward,
                getattr(message, "id", None),
            )
        if forward:
            if DEBUG_MODE:
                logger.info("[BROADCAST] forwarding message to user_id=%s", user_id)
            await message.forward(chat_id=user_id)
        else:
            if DEBUG_MODE:
                logger.info("[BROADCAST] copying message to user_id=%s", user_id)
            await message.copy(chat_id=user_id)
        if DEBUG_MODE:
            logger.info("[BROADCAST] success | user_id=%s", user_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
        if DEBUG_MODE:
            logger.info("[BROADCAST] FloodWait encountered | seconds=%s", e.value)
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message, forward)
    except InputUserDeactivated:
        if DEBUG_MODE:
            logger.info("[BROADCAST] user_id=%s deactivated; removing from db", user_id)
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Removed from database (deleted account).")
        return False, "Deleted"
    except UserIsBlocked:
        logger.info(f"{user_id} - Blocked the bot. will be deleted")
        if DEBUG_MODE:
            logger.info("[BROADCAST] user_id=%s blocked bot; removing from db", user_id)
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        logger.info(f"{user_id} - PeerIdInvalid. & deleted")
        if DEBUG_MODE:
            logger.info("[BROADCAST] peer id invalid for user_id=%s; removing from db", user_id)
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        logger.error(f"Error broadcasting to {user_id}: {e}")
        if DEBUG_MODE:
            logger.exception("[BROADCAST] unexpected failure | user_id=%s", user_id)
        return False, "Error"


async def broadcast_messages_group(chat_id, message, forward=False):
    try:
        if DEBUG_MODE:
            logger.info(
                "[BROADCAST_GROUP] entered | chat_id=%s | forward=%s | message_id=%s",
                chat_id,
                forward,
                getattr(message, "id", None),
            )
        if forward:
            if DEBUG_MODE:
                logger.info("[BROADCAST_GROUP] forwarding message to chat_id=%s", chat_id)
            await message.forward(chat_id=chat_id)
        else:
            if DEBUG_MODE:
                logger.info("[BROADCAST_GROUP] copying message to chat_id=%s", chat_id)
            msg = await message.copy(chat_id=chat_id)
            try:
                if DEBUG_MODE:
                    logger.info("[BROADCAST_GROUP] attempting pin | chat_id=%s", chat_id)
                await msg.pin()
                if DEBUG_MODE:
                    logger.info("[BROADCAST_GROUP] pin success | chat_id=%s", chat_id)
            except Exception as e:
                logger.warning(f"Could not pin message in group {chat_id}: {e}")
                if DEBUG_MODE:
                    logger.exception("[BROADCAST_GROUP] pin failed | chat_id=%s", chat_id)
        if DEBUG_MODE:
            logger.info("[BROADCAST_GROUP] success | chat_id=%s", chat_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
        if DEBUG_MODE:
            logger.info("[BROADCAST_GROUP] FloodWait encountered | seconds=%s", e.value)
        await asyncio.sleep(e.value)
        return await broadcast_messages_group(chat_id, message, forward)
    except Exception as e:
        logger.error(f"Error broadcasting to group {chat_id}: {e}")
        if DEBUG_MODE:
            logger.exception("[BROADCAST_GROUP] unexpected failure | chat_id=%s", chat_id)
        return False, "Error"


async def send_all(bot, userid, files, ident, chat_id, user_name, query):
    if DEBUG_MODE:
        logger.info(
            "[SEND_ALL] entered | userid=%s | chat_id=%s | ident=%s | file_count=%s | user_name=%r",
            userid, chat_id, ident, len(files) if files else 0, user_name
        )
    settings = await get_settings(chat_id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        # FIXED (item 1 above): was `message.chat.id`, but `message` is not
        # defined in this function's scope — this is the `chat_id` parameter.
        await save_group_settings(chat_id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    try:
        if ENABLE_SHORTLINK:
            if DEBUG_MODE:
                logger.info("[SEND_ALL] shortlink mode enabled")
            for file in files:
                title = file["file_name"]
                size = get_size(file["file_size"])
                if DEBUG_MODE:
                    logger.info("[SEND_ALL] processing file=%r | size=%r", title, size)
                if not await db.has_premium_access(userid) and SHORTLINK_MODE == True:
                    if DEBUG_MODE:
                        logger.info("[SEND_ALL] sending shortlink message to userid=%s", userid)
                    await bot.send_message(chat_id=userid, text=f"<b>Hᴇʏ ᴛʜᴇʀᴇ {user_name} 👋🏽 \n\n✅ Sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғɪʟᴇ ʜᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴇᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ\n\n🗃️ Fɪʟᴇ Nᴀᴍᴇ : {title}\n🔖 Fɪʟᴇ Sɪᴢᴇ : {size}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Dᴏᴡɴʟᴏᴀᴅ 📥", url=await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}"))]]))
        else:
            if DEBUG_MODE:
                logger.info("[SEND_ALL] direct media mode enabled")
            for file in files:
                f_caption = file["caption"]
                title = file["file_name"]
                size = get_size(file["file_size"])
                if DEBUG_MODE:
                    logger.info("[SEND_ALL] sending file=%r | size=%r", title, size)
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                                file_size='' if size is None else size,
                                                                file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        print(e)
                        if DEBUG_MODE:
                            logger.exception("[SEND_ALL] caption format failed for file=%r", title)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                await bot.send_cached_media(
                    chat_id=userid,
                    file_id=file["file_id"],
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ],[
                                InlineKeyboardButton("Check What's New", url="t.me/filmykeedha")
                            ],[
                                InlineKeyboardButton("Want To Earn", url="t.me/earningdailyforyou")
                            ]
                        ]
                    )
                )
        if DEBUG_MODE:
            logger.info("[SEND_ALL] completed successfully | userid=%s", userid)
    except UserIsBlocked:
        if DEBUG_MODE:
            logger.info("[SEND_ALL] user blocked bot | userid=%s", userid)
        await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
    except PeerIdInvalid:
        if DEBUG_MODE:
            logger.info("[SEND_ALL] peer id invalid | userid=%s", userid)
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
    except Exception as e:
        logger.error(f"Error broadcasting to {userid}: {e}")
        if DEBUG_MODE:
            logger.exception("[SEND_ALL] unexpected failure | userid=%s", userid)
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
