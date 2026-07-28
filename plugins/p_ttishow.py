import logging
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, CHNL_LNK, GRP_LNK, DEBUG_MODE
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings
#from Script import script
from pyrogram.errors import ChatAdminRequired
from variables import WELCOME_VIDEO_ID
from langs.i18n import get, get_btn, DEFAULT_LANG
"""-----------------------------------------https://t.me/iAmRashmibot --------------------------------------"""
# WELCOME_VIDEO_ID = config.get("WELCOME_VIDEO_ID") if config.get("WELCOME_VIDEO_ID") else environ.get("MELCOW_VID", "BAACAgQAAxkBAAEWWw5nXJ_bgRy9MY3ZNxpLzbIaysGuswAC2hoAAuLv4VIyB40_JD42Hh4E")

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.new_chat_members & filters.group)
async def save_group(bot, message):
    lang = await _user_lang(message.from_user)
    r_j_check = [u.id for u in message.new_chat_members]
    if temp.ME in r_j_check:
        if DEBUG_MODE:
            logger.info("[GROUP] bot added to chat | chat_id=%s", message.chat.id)
        if not await db.get_chat(message.chat.id):
            total = await bot.get_chat_members_count(message.chat.id)
            r_j = message.from_user.mention if message.from_user else "Anonymous"
            await bot.send_message( LOG_CHANNEL, get(lang, "LOG_TEXT_G", title=message.chat.title, chat_id=message.chat.id, members=total, added_by=r_j ))
            await db.add_chat(message.chat.id, message.chat.title)
        if message.chat.id in temp.BANNED_CHATS:
            if DEBUG_MODE:
                logger.info("[GROUP] chat is banned, leaving | chat_id=%s", message.chat.id)
            # Handle banned chats
            buttons = [[
                InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_PLAIN"), url=f'https://t.me/{SUPPORT_CHAT}')
            ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            k = await message.reply(
                text=get(lang, "CHAT_NOT_ALLOWED"),
                reply_markup=reply_markup,
            )

            try:
                await k.pin()
            except:
                pass
            await bot.leave_chat(message.chat.id)
            return
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GROUP"), url=GRP_LNK),
            InlineKeyboardButton(get_btn(lang, "BTN_UPDATES_CHANNEL"), url=CHNL_LNK)
        ], [
            InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_PLAIN"), url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=get(lang, "THANKS_FOR_ADDING", title=message.chat.title),
            reply_markup=reply_markup
        )
    else:
        settings = await get_settings(message.chat.id)
        if settings["welcome"]:
            for u in message.new_chat_members:
                if (temp.MELCOW).get('welcome') is not None:
                    try:
                        await (temp.MELCOW['welcome']).delete()
                    except:
                        pass
                # Replace MELCOW_VID with the file ID stored in settings
                temp.MELCOW['welcome'] = await message.reply_video(
                    video=WELCOME_VIDEO_ID,  # Use file ID here
                    caption=get(lang, "MELCOW_ENG", uname=u.mention, group=message.chat.title),
                 
                    #caption=(script.MELCOW_ENG.format(u.mention, message.chat.title)),
                    reply_markup=InlineKeyboardMarkup(
                        [[
                            InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_GROUP"), url=GRP_LNK),
                            InlineKeyboardButton(get_btn(lang, "BTN_UPDATES_CHANNEL"), url=CHNL_LNK)
                        ], [
                            InlineKeyboardButton(get_btn(lang, "BTN_BOT_OWNER"), url="t.me/Pankaj_jii")
                        ]]
                    ),
                    parse_mode=enums.ParseMode.HTML
                )

        if settings["auto_delete"]:
            # NOTE: `asyncio` is not imported in this module — pre-existing bug,
            # documented in README "Known dormant issues", left as-is (not
            # currently reachable: nothing in this project sets auto_delete).
            await asyncio.sleep(600)
            await (temp.MELCOW['welcome']).delete()


@Client.on_message(filters.command('leave') & filters.user(ADMINS))
async def leave_a_chat(bot, message):
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_CHAT_ID"))
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        chat = chat
    try:
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_STYLE"), url=f'https://t.me/{SUPPORT_CHAT}')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat,
            text=get(lang, "LEAVE_NOTICE_BILINGUAL"),
            reply_markup=reply_markup,
        )

        if DEBUG_MODE:
            logger.info("[ADMIN] leaving chat | chat_id=%s | requested_by=%s", chat, message.from_user.id)
        await bot.leave_chat(chat)
        await message.reply(get(lang, "LEFT_CHAT_CONFIRM", chat=chat))
    except Exception as e:
        await message.reply(get(lang, "GENERIC_ERROR", error=e))


@Client.on_message(filters.command('disable') & filters.user(ADMINS))
async def disable_chat(bot, message):
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_CHAT_ID"))
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = get(lang, "NO_REASON_PROVIDED")
    try:
        chat_ = int(chat)
    except:
        return await message.reply(get(lang, "GIVE_VALID_CHAT_ID"))
    cha_t = await db.get_chat(int(chat_))
    if not cha_t:
        return await message.reply(get(lang, "CHAT_NOT_FOUND_DB"))
    if cha_t['is_disabled']:
        return await message.reply(get(lang, "CHAT_ALREADY_DISABLED", reason=cha_t['reason']))
    await db.disable_chat(int(chat_), reason)
    temp.BANNED_CHATS.append(int(chat_))
    if DEBUG_MODE:
        logger.info("[ADMIN] chat disabled | chat_id=%s | reason=%r | by=%s", chat_, reason, message.from_user.id)
    await message.reply(get(lang, "CHAT_DISABLED_OK"))
    try:
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_SUPPORT_STYLE"), url=f'https://t.me/iAmRashmibot')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            chat_id=chat_,
            text=get(lang, "LEAVE_NOTICE_WITH_REASON", reason=reason),
            reply_markup=reply_markup)
        await bot.leave_chat(chat_)
    except Exception as e:
        await message.reply(get(lang, "GENERIC_ERROR", error=e))


@Client.on_message(filters.command('enable') & filters.user(ADMINS))
async def re_enable_chat(bot, message):
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_CHAT_ID_HI"))
    chat = message.command[1]
    try:
        chat_ = int(chat)
    except:
        return await message.reply(get(lang, "GIVE_VALID_CHAT_ID_HI"))
    sts = await db.get_chat(int(chat))
    if not sts:
        return await message.reply(get(lang, "CHAT_NOT_FOUND_DB_HI"))
    if not sts.get('is_disabled'):
        return await message.reply(get(lang, "CHAT_NOT_DISABLED_YET"))
    await db.re_enable_chat(int(chat_))
    temp.BANNED_CHATS.remove(int(chat_))
    if DEBUG_MODE:
        logger.info("[ADMIN] chat re-enabled | chat_id=%s | by=%s", chat_, message.from_user.id)
    await message.reply(get(lang, "CHAT_RE_ENABLED_OK"))


@Client.on_message(filters.command('stats') & filters.incoming)
async def get_ststs(bot, message):
    lang = await _user_lang(message.from_user)
    rju = await message.reply(get(lang, "FETCHING_STATS"))
    total_users = await db.total_users_count()
    totl_chats = await db.total_chat_count()
    files = await Media.count_documents()
    size = await db.get_db_size()
    free = 536870912 - size
    size = get_size(size)
    free = get_size(free)
    if DEBUG_MODE:
        logger.info(
            "[STATS] files=%s users=%s chats=%s used=%s free=%s",
            files, total_users, totl_chats, size, free
        )
    await rju.edit( get( lang, "STATUS_TXT", files=files, users=total_users, chats=totl_chats, used=size, free=free ))

# a function for trespassing into others groups, Inspired by a Vazha
# Not to be used , But Just to showcase his vazhatharam.
@Client.on_message(filters.command('invite') & filters.user(ADMINS))
async def gen_invite(bot, message):
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_VALID_CHAT_ID_PLAIN"))
    chat = message.command[1]
    try:
        chat = int(chat)
    except:
        return await message.reply(get(lang, "GIVE_VALID_CHAT_ID_PLAIN2"))
    try:
        link = await bot.create_chat_invite_link(chat)
    except ChatAdminRequired:
        return await message.reply(get(lang, "INVITE_FAILED"))
    except Exception as e:
        return await message.reply(get(lang, "GENERIC_ERROR", error=e))
    if DEBUG_MODE:
        logger.info("[ADMIN] invite link generated | chat_id=%s | by=%s", chat, message.from_user.id)
    await message.reply(get(lang, "INVITE_LINK_RESULT", link=link.invite_link))


@Client.on_message(filters.command('ban') & filters.user(ADMINS))
async def ban_a_user(bot, message):
    # https://t.me/GetTGLink/4185
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_USER_ID"))
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = get(lang, "NO_REASON_PROVIDED")
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply(get(lang, "INVALID_USER_NOT_MET"))
    except IndexError:
        return await message.reply(get(lang, "INVALID_USER_MIGHT_BE_CHANNEL"))
    except Exception as e:
        return await message.reply(get(lang, "GENERIC_ERROR", error=e))
    else:
        jar = await db.get_ban_status(k.id)
        if jar['is_banned']:
            return await message.reply(get(lang, "USER_ALREADY_BANNED", mention=k.mention, reason=jar['ban_reason']))
        await db.ban_user(k.id, reason)
        temp.BANNED_USERS.append(k.id)
        if DEBUG_MODE:
            logger.info("[ADMIN] user banned | user_id=%s | reason=%r | by=%s", k.id, reason, message.from_user.id)
        await message.reply(get(lang, "USER_BANNED_OK", mention=k.mention))


@Client.on_message(filters.command('unban') & filters.user(ADMINS))
async def unban_a_user(bot, message):
    lang = await _user_lang(message.from_user)
    if len(message.command) == 1:
        return await message.reply(get(lang, "GIVE_USER_ID_PLAIN"))
    r = message.text.split(None)
    if len(r) > 2:
        reason = message.text.split(None, 2)[2]
        chat = message.text.split(None, 2)[1]
    else:
        chat = message.command[1]
        reason = get(lang, "NO_REASON_PROVIDED")
    try:
        chat = int(chat)
    except:
        pass
    try:
        k = await bot.get_users(chat)
    except PeerIdInvalid:
        return await message.reply(get(lang, "INVALID_USER_NOT_MET"))
    except IndexError:
        return await message.reply(get(lang, "INVALID_USER_MIGHT_BE_CHANNEL"))
    except Exception as e:
        return await message.reply(get(lang, "GENERIC_ERROR", error=e))
    else:
        jar = await db.get_ban_status(k.id)
        if not jar['is_banned']:
            return await message.reply(get(lang, "USER_NOT_BANNED_YET", mention=k.mention))
        await db.remove_ban(k.id)
        temp.BANNED_USERS.remove(k.id)
        if DEBUG_MODE:
            logger.info("[ADMIN] user unbanned | user_id=%s | by=%s", k.id, message.from_user.id)
        await message.reply(get(lang, "USER_UNBANNED_OK", mention=k.mention))


@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    lang = await _user_lang(message.from_user)
    raju = await message.reply(get(lang, "FETCHING_USERS_LIST"))
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        # Include user id in the output
        out += f"User ID: `{user['id']}`\n"
        out += f"Name: <a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += ' (Banned User)'
        out += '\n'

    # Save the output to a .txt file
    with open('users.txt', 'w+') as outfile:
        outfile.write(out)

    # Send the .txt file to the user
    await message.reply_document('users.txt', caption=get(lang, "USERS_LIST_CAPTION"))


@Client.on_message(filters.command('chats') & filters.user(ADMINS))
async def list_chats(bot, message):
    lang = await _user_lang(message.from_user)
    raju = await message.reply(get(lang, "FETCHING_CHATS_LIST"))
    chats = await db.get_all_chats()
    out = "Chats Saved In DB Are:\n\n"
    async for chat in chats:
        # Include chat id in the output
        out += f"Chat ID: `{chat['id']}`\n"
        out += f"**Title:** `{chat['title']}`\n"
        if chat['chat_status']['is_disabled']:
            out += ' (Disabled Chat)'
        out += '\n'

    # Save the output to a .txt file
    with open('chats.txt', 'w+') as outfile:
        outfile.write(out)

    # Send the .txt file to the user
    await message.reply_document('chats.txt', caption=get(lang, "CHATS_LIST_CAPTION"))


@Client.on_message(filters.command("getfileid") & (filters.reply))
async def get_file_id(bot, message):
    lang = await _user_lang(message.from_user)
    # Check if the message is a reply with media
    if message.reply_to_message:
        media = message.reply_to_message.video or \
                message.reply_to_message.photo or \
                message.reply_to_message.document or \
                message.reply_to_message.audio or \
                message.reply_to_message.voice

        if media:
            file_id = media.file_id
            file_type = type(media).__name__.capitalize()
            if DEBUG_MODE:
                logger.info("[GETFILEID] resolved from reply | file_id=%s | type=%s", file_id, file_type)
            await message.reply(
                get(lang, "FILE_ID_RESULT", file_id=file_id, file_type=file_type, file_size=media.file_size),
                quote=True
            )
        else:
            await message.reply(get(lang, "GETFILEID_NO_MEDIA_REPLY"), quote=True)

    # Handle direct media messages (e.g., channels without replies)
    elif message.video or message.photo or message.document or message.audio or message.voice:
        media = message.video or message.photo or message.document or message.audio or message.voice
        file_id = media.file_id
        file_type = type(media).__name__.capitalize()
        if DEBUG_MODE:
            logger.info("[GETFILEID] resolved from direct media | file_id=%s | type=%s", file_id, file_type)
        await message.reply(
            get(lang, "FILE_ID_RESULT", file_id=file_id, file_type=file_type, file_size=media.file_size),
            quote=True
        )
    else:
        await message.reply(get(lang, "GETFILEID_NO_MEDIA"), quote=True)
