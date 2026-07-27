import logging

from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from database.users_chats_db import db
from info import ADMINS, DEBUG_MODE
from langs.i18n import get, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def addconnection(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[CONNECT] /connect blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                get(lang, "CONNECT_USAGE"),
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and userid not in ADMINS
        ):
            if DEBUG_MODE:
                logger.info("[CONNECT] /connect blocked: not admin/owner | user_id=%s group_id=%s", userid, group_id)
            await message.reply_text(get(lang, "CONNECT_NOT_ADMIN"), quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            get(lang, "CONNECT_INVALID_ID"),
            quote=True,
        )

        return
    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            addcon = await add_connection(str(group_id), str(userid))
            if addcon:
                if DEBUG_MODE:
                    logger.info("[CONNECT] connected | group_id=%s user_id=%s", group_id, userid)
                await message.reply_text(
                    get(lang, "CONNECT_SUCCESS_PM", title=title),
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        get(lang, "CONNECT_SUCCESS_GRP", title=title),
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    get(lang, "CONNECT_ALREADY"),
                    quote=True
                )
        else:
            await message.reply_text(get(lang, "CONNECT_ADD_ME_ADMIN"), quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text(get(lang, "CONNECT_ERROR"), quote=True)
        return


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def deleteconnection(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[CONNECT] /disconnect blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text(get(lang, "DISCONNECT_HINT_PM"), quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
                st.status != enums.ChatMemberStatus.ADMINISTRATOR
                and st.status != enums.ChatMemberStatus.OWNER
                and str(userid) not in ADMINS
        ):
            if DEBUG_MODE:
                logger.info("[CONNECT] /disconnect blocked: not admin/owner | user_id=%s group_id=%s", userid, group_id)
            return

        delcon = await delete_connection(str(userid), str(group_id))
        if DEBUG_MODE:
            logger.info("[CONNECT] /disconnect: %s | user_id=%s group_id=%s", "success" if delcon else "not connected", userid, group_id)
        if delcon:
            await message.reply_text(get(lang, "DISCONNECT_SUCCESS"), quote=True)
        else:
            await message.reply_text(get(lang, "DISCONNECT_NOT_FOUND"), quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id

    groupids = await all_connections(str(userid))
    if groupids is None:
        if DEBUG_MODE:
            logger.info("[CONNECT] /connections: none | user_id=%s", userid)
        await message.reply_text(
            get(lang, "CONNECTIONS_NONE"),
            quote=True
        )
        return
    buttons = []
    for groupid in groupids:
        try:
            ttl = await client.get_chat(int(groupid))
            title = ttl.title
            active = await if_active(str(userid), str(groupid))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                    )
                ]
            )
        except:
            pass
    if buttons:
        if DEBUG_MODE:
            logger.info("[CONNECT] /connections: listed | count=%s user_id=%s", len(buttons), userid)
        await message.reply_text(
            get(lang, "CONNECTIONS_LIST"),
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            get(lang, "CONNECTIONS_NONE"),
            quote=True
        )
