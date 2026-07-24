"""
plugins/commands.py — /settings, /donate, and /set_template.

This file used to be 931 lines covering /start's entire deep-link flow and
all the admin maintenance commands too. It has been split into:

    plugins/commands.py        (this file) — /settings, /donate, /set_template
    plugins/commands_start.py  — /start and its deep-link sub-handlers
    plugins/commands_admin.py  — /restart, /channel, /logs, /delete,
                                  /deleteall, /scrub and their callbacks

Pyrogram auto-discovers handlers from every .py file under the `plugins/`
package root, so this split needs no change to how the bot loads plugins.
No logic changed during this split — only the file boundaries moved.

All user-facing strings are served from langs/i18n.py via get() / get_btn().
"""

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.users_chats_db import db
from database.connections_mdb import active_connection

from info import ADMINS, OWNER_USERNAME, PAYMENT_QR, PAYMENT_TEXT
from utils import get_settings, save_group_settings
from langs.i18n import get, get_btn

# Importing these registers their handlers with Pyrogram (decorators run on
# import).
from plugins.commands_start import start  # noqa: F401
from plugins.commands_admin import (  # noqa: F401
    restart_bot, channel_info, log_file, delete_file, delete_all_index,
    delete_all_index_confirm, scrub_database, handle_purge_confirmation,
)


# ─────────────────────────────────────────────────────────────────────────────
# /settings  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("settings") & filters.user(ADMINS))
async def settings(client, message: Message):
    lang    = await db.get_user_lang(message.from_user.id)
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply(get(lang, "ANON_ADMIN_MSG", chat_id=message.chat.id))

    if message.chat.type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(user_id))
        if grpid:
            try:
                chat  = await client.get_chat(grpid)
                title = chat.title
                grp_id = grpid
            except Exception:
                return await message.reply_text(get(lang, "NOT_IN_GROUP"), quote=True)
        else:
            return await message.reply_text(get(lang, "NOT_CONNECTED"), quote=True)
    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title  = message.chat.title
    else:
        return

    st = await client.get_chat_member(grp_id, user_id)
    if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] \
            and str(user_id) not in ADMINS:
        return

    s = await get_settings(grp_id)
    if s:
        mk = lambda key, val, label_on, label_off: [
            InlineKeyboardButton(get_btn(lang, f"BTN_SET_{key.upper()}"),
                                 callback_data=f"setgs#{key}#{val}#{grp_id}"),
            InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if val else get_btn(lang, "BTN_SET_NO"),
                                 callback_data=f"setgs#{key}#{val}#{grp_id}"),
        ]
        buttons = [
            [
                InlineKeyboardButton(get_btn(lang, "BTN_SET_FILTER_BTN"),
                                     callback_data=f"setgs#button#{s['button']}#{grp_id}"),
                InlineKeyboardButton(
                    get_btn(lang, "BTN_SET_SINGLE") if s["button"] else get_btn(lang, "BTN_SET_DOUBLE"),
                    callback_data=f"setgs#button#{s['button']}#{grp_id}"),
            ],
            mk("botpm",       s["botpm"],       None, None),
            mk("file_secure", s["file_secure"], None, None),
            mk("imdb",        s["imdb"],        None, None),
            mk("spell_check", s["spell_check"], None, None),
            mk("welcome",     s["welcome"],     None, None),
        ]
        await message.reply_text(
            get(lang, "SETTINGS_TITLE", title=title),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )


# ─────────────────────────────────────────────────────────────────────────────
# /donate
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("donate"))
async def plans_cmd_handler(client, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    btn  = [
        [InlineKeyboardButton(get_btn(lang, "BTN_SEND_RECEIPT"), url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton(get_btn(lang, "BTN_CLOSE"),        callback_data="close_data")],
    ]
    await message.reply_photo(photo=PAYMENT_QR, caption=PAYMENT_TEXT,
                              reply_markup=InlineKeyboardMarkup(btn))


@Client.on_callback_query(filters.regex("donation"))
async def donation_callback(client, query):
    lang = await db.get_user_lang(query.from_user.id)
    await query.answer()
    btn  = [
        [InlineKeyboardButton(get_btn(lang, "BTN_SEND_RECEIPT"), url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton(get_btn(lang, "BTN_CLOSE"),        callback_data="close_data")],
    ]
    await query.message.reply_photo(photo=PAYMENT_QR, caption=PAYMENT_TEXT,
                                    reply_markup=InlineKeyboardMarkup(btn))


# ─────────────────────────────────────────────────────────────────────────────
# /set_template
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("set_template"))
async def save_template(client, message: Message):
    lang    = await db.get_user_lang(message.from_user.id)
    sts     = await message.reply(get(lang, "PROCESSING"))
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        return await message.reply(get(lang, "ANON_ADMIN_MSG", chat_id=message.chat.id))

    if message.chat.type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(user_id))
        if grpid:
            try:
                chat  = await client.get_chat(grpid)
                title = chat.title
                grp_id = grpid
            except Exception:
                return await message.reply_text(get(lang, "NOT_IN_GROUP"), quote=True)
        else:
            return await message.reply_text(get(lang, "NOT_CONNECTED"), quote=True)
    elif message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title  = message.chat.title
    else:
        return

    st = await client.get_chat_member(grp_id, user_id)
    if st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER] \
            and str(user_id) not in ADMINS:
        return

    if len(message.command) < 2:
        return await sts.edit(get(lang, "NO_INPUT"))

    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, "template", template)
    await sts.edit(get(lang, "TEMPLATE_SAVED", title=title, template=template))
