"""
plugins/filters.py — /addfilter (/addf), /viewfilters (/filters),
/delelefilter, and /deleteallf.

All user-facing strings now go through langs.i18n.get()/get_btn() instead
of hardcoded literals. DEBUG_MODE logging added at each significant step.
No logic changed during this sweep — only text sourcing and logging.
"""

import io
import logging

from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from database.filters_mdb import (
   add_filter,
   get_filters,
   delete_filter,
   count_filters
)
from database.connections_mdb import active_connection
from database.users_chats_db import db
from utils import get_file_id, parser, split_quotes
from info import ADMINS, DEBUG_MODE
from langs.i18n import get, get_btn, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.command(['addfilter', 'addf']) & filters.incoming)
async def addfilter(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[FILTER] addfilter blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    chat_type = message.chat.type
    args = message.text.html.split(None, 1)

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                if DEBUG_MODE:
                    logger.info("[FILTER] addfilter: bot not in connected group | grp_id=%s", grpid)
                await message.reply_text(get(lang, "NOT_IN_GROUP_PLAIN"), quote=True)
                return
        else:
            if DEBUG_MODE:
                logger.info("[FILTER] addfilter: user has no active connection | user_id=%s", userid)
            await message.reply_text(get(lang, "NOT_CONNECTED_PLAIN"), quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        if DEBUG_MODE:
            logger.info("[FILTER] addfilter blocked: not admin/owner | user_id=%s grp_id=%s", userid, grp_id)
        return

    if len(args) < 2:
        if DEBUG_MODE:
            logger.info("[FILTER] addfilter: incomplete command | user_id=%s grp_id=%s", userid, grp_id)
        await message.reply_text(get(lang, "FILTER_CMD_INCOMPLETE"), quote=True)
        return

    extracted = split_quotes(args[1])
    text = extracted[0].lower()

    if not message.reply_to_message and len(extracted) < 2:
        await message.reply_text(get(lang, "FILTER_ADDF_NO_CONTENT"), quote=True)
        return

    if (len(extracted) >= 2) and not message.reply_to_message:
        reply_text, btn, alert = parser(extracted[1], text)
        fileid = None
        if not reply_text:
            await message.reply_text(get(lang, "FILTER_ADDF_BTN_ALONE"), quote=True)
            return

    elif message.reply_to_message and message.reply_to_message.reply_markup:
        try:
            rm = message.reply_to_message.reply_markup
            btn = rm.inline_keyboard
            msg = get_file_id(message.reply_to_message)
            if msg:
                fileid = msg.file_id
                reply_text = message.reply_to_message.caption.html
            else:
                reply_text = message.reply_to_message.text.html
                fileid = None
            alert = None
        except:
            reply_text = ""
            btn = "[]"
            fileid = None
            alert = None

    elif message.reply_to_message and message.reply_to_message.media:
        try:
            msg = get_file_id(message.reply_to_message)
            fileid = msg.file_id if msg else None
            reply_text, btn, alert = parser(extracted[1], text) if message.reply_to_message.sticker else parser(message.reply_to_message.caption.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
    elif message.reply_to_message and message.reply_to_message.text:
        try:
            fileid = None
            reply_text, btn, alert = parser(message.reply_to_message.text.html, text)
        except:
            reply_text = ""
            btn = "[]"
            alert = None
    else:
        return

    await add_filter(grp_id, text, reply_text, btn, fileid, alert)

    if DEBUG_MODE:
        logger.info("[FILTER] filter added | grp_id=%s text=%s", grp_id, text)

    await message.reply_text(
        get(lang, "FILTER_ADDF_SUCCESS", text=text, title=title),
        quote=True,
        parse_mode=enums.ParseMode.MARKDOWN
    )


@Client.on_message(filters.command(['viewfilters', 'filters']) & filters.incoming)
async def get_all(client, message):
    lang = await _user_lang(message.from_user)
    chat_type = message.chat.type
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[FILTER] viewfilters blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                if DEBUG_MODE:
                    logger.info("[FILTER] viewfilters: bot not in connected group | grp_id=%s", grpid)
                await message.reply_text(get(lang, "NOT_IN_GROUP_PLAIN"), quote=True)
                return
        else:
            if DEBUG_MODE:
                logger.info("[FILTER] viewfilters: user has no active connection | user_id=%s", userid)
            await message.reply_text(get(lang, "NOT_CONNECTED_PLAIN"), quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        if DEBUG_MODE:
            logger.info("[FILTER] viewfilters blocked: not admin/owner | user_id=%s grp_id=%s", userid, grp_id)
        return

    texts = await get_filters(grp_id)
    count = await count_filters(grp_id)
    if DEBUG_MODE:
        logger.info("[FILTER] viewfilters: count=%s | grp_id=%s", count, grp_id)
    if count:
        filterlist = get(lang, "FILTER_LIST_HEADER", title=title, count=count)

        for text in texts:
            keywords = get(lang, "FILTER_LIST_ITEM", name=text)

            filterlist += keywords

        if len(filterlist) > 4096:
            with io.BytesIO(str.encode(filterlist.replace("`", ""))) as keyword_file:
                keyword_file.name = "keywords.txt"
                await message.reply_document(
                    document=keyword_file,
                    quote=True
                )
            return
    else:
        filterlist = get(lang, "FILTER_LIST_EMPTY", title=title)

    await message.reply_text(
        text=filterlist,
        quote=True,
        parse_mode=enums.ParseMode.MARKDOWN
    )

@Client.on_message(filters.command('delelefilter') & filters.incoming)
async def deletefilter(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[FILTER] delelefilter blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                if DEBUG_MODE:
                    logger.info("[FILTER] delelefilter: bot not in connected group | grp_id=%s", grpid)
                await message.reply_text(get(lang, "NOT_IN_GROUP_PLAIN"), quote=True)
                return
        else:
            if DEBUG_MODE:
                logger.info("[FILTER] delelefilter: user has no active connection | user_id=%s", userid)
            await message.reply_text(get(lang, "NOT_CONNECTED_PLAIN"), quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status != enums.ChatMemberStatus.ADMINISTRATOR
        and st.status != enums.ChatMemberStatus.OWNER
        and str(userid) not in ADMINS
    ):
        if DEBUG_MODE:
            logger.info("[FILTER] delelefilter blocked: not admin/owner | user_id=%s grp_id=%s", userid, grp_id)
        return

    try:
        cmd, text = message.text.split(" ", 1)
    except:
        await message.reply_text(
            get(lang, "FILTER_DEL_USAGE"),
            quote=True
        )
        return

    query = text.lower()

    if DEBUG_MODE:
        logger.info("[FILTER] delelefilter: deleting | grp_id=%s query=%s", grp_id, query)

    await delete_filter(message, query, grp_id, lang=lang)


@Client.on_message(filters.command('deleteallf') & filters.incoming)
async def delallconfirm(client, message):
    lang = await _user_lang(message.from_user)
    userid = message.from_user.id if message.from_user else None
    if not userid:
        if DEBUG_MODE:
            logger.info("[FILTER] deleteallf blocked: anonymous admin | chat_id=%s", message.chat.id)
        return await message.reply(get(lang, "ANON_ADMIN_CONNECT", chat_id=message.chat.id))
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                if DEBUG_MODE:
                    logger.info("[FILTER] deleteallf: bot not in connected group | grp_id=%s", grpid)
                await message.reply_text(get(lang, "NOT_IN_GROUP_PLAIN"), quote=True)
                return
        else:
            if DEBUG_MODE:
                logger.info("[FILTER] deleteallf: user has no active connection | user_id=%s", userid)
            await message.reply_text(get(lang, "NOT_CONNECTED_PLAIN"), quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title

    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
        if DEBUG_MODE:
            logger.info("[FILTER] deleteallf: confirmation prompt sent | grp_id=%s user_id=%s", grp_id, userid)
        await message.reply_text(
            get(lang, "FILTER_DELALL_CONFIRM", title=title),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(text=get_btn(lang, "BTN_YES_PLAIN"), callback_data="delallconfirm")],
                [InlineKeyboardButton(text=get_btn(lang, "BTN_CANCEL_PLAIN"), callback_data="delallcancel")]
            ]),
            quote=True
        )
