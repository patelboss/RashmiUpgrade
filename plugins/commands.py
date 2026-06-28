"""
plugins/commands.py — Core bot command and callback handlers.

All user-facing strings are served from langs/i18n.py via get() / get_btn().
Debug events are emitted via debug.dlog() — only printed when DEBUG_MODE=true.
"""

import os
import sys
import logging
import random
import asyncio
import re
import uuid
import base64

import pytz
from datetime import datetime, date

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_file_details1
from database.users_chats_db import db
from database.connections_mdb import active_connection
from database.batch_filedb import (
    fetch_file_by_link, get_batch_by_id, save_batch_details,
    get_latest_batch_sequence, generate_batch_id
)

from info import (
    CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS,
    BATCH_FILE_CAPTION, PROTECT_CONTENT,
    GRP_LNK, CHNL_LNK, OFR_CNL, Share_msg, OWNER_USERNAME,
    PAYMENT_QR, PAYMENT_TEXT,
)
from variables import CUSTOM_FILE_CAPTION, VERIFY, VERIFY_TUTORIAL, DLTTM, AUTH_CHANNELS
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, clean_file_name
from utils import VERIFIED
from langs.i18n import get, get_btn
from debug import dlog

import builtins

# ── Logger ─────────────────────────────────────────────────────────────────────
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
_sh = logging.StreamHandler(sys.stdout)
_sh.setLevel(logging.INFO)
_sh.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
logger.addHandler(_sh)

# ── Sticker pool (random greeting) ────────────────────────────────────────────
_STICKER_IDS = [
    "CAACAgUAAxkBAAI15Wd8MrA2SLTI-Li_SmwkWxcxOoTVAALNBAACWe0YVlcLt2c9ppYFHgQ",
    "CAACAgIAAxkBAAI1z2d8MVKnvJ68w1OVqj6XCYTFCNS5AALUEQADwKBJeScB4o8r9AweBA",
    "CAACAgIAAxkBAAI102d8MVe_iLmKqD6BCfGvxxHmNUK4AAK8NwAC2VrBSCneSsfNGnZUHgQ",
    "CAACAgEAAxkBAAI112d8MV0hEjLP2-Re5U3DkgtF_0zsAALJAwACgtDpR9eFnD06DCjbHgQ",
    "CAACAgIAAxkBAAI122d8MWryfJiBYYFQnHswu2MUi0uIAAJiAANOXNIpTqLDGEjEK3EeBA",
]

# Temporary RAM cache for scrub confirmations
PURGE_CACHE: dict = {}


def _sticker() -> str:
    return random.choice(_STICKER_IDS)


# ─────────────────────────────────────────────────────────────────────────────
# /restart  (admin only)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def restart_bot(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    msg = await bot.send_message(message.chat.id, get(lang, "BOT_RESTARTING"))
    dlog("RESTART", user_id=message.from_user.id)
    await asyncio.sleep(3)
    await msg.edit(get(lang, "BOT_RESTARTED"))
    os.execl(sys.executable, sys.executable, *sys.argv)


# ─────────────────────────────────────────────────────────────────────────────
# /start
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message: Message):
    m = await message.reply_sticker(_sticker())
    await asyncio.sleep(1)

    user_id = message.from_user.id if message.from_user else None
    lang = await db.get_user_lang(user_id) if user_id else "en"

    # ── Group start ───────────────────────────────────────────────────────────
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [InlineKeyboardButton(get_btn(lang, "BTN_UPDATES"), url="https://t.me/iAmRashmibot")],
            [InlineKeyboardButton(get_btn(lang, "BTN_HELP"),    url=f"https://t.me/{temp.U_NAME}?start=help")],
        ]
        await message.reply(
            get(lang, "START", name=message.from_user.mention if message.from_user else message.chat.title,
                uname=temp.U_NAME, bname=temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        await m.delete()
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(
                LOG_CHANNEL,
                get("en", "LOG_TEXT_G",
                    title=message.chat.title, chat_id=message.chat.id,
                    members=total, added_by="Unknown")
            )
            await db.add_chat(message.chat.id, message.chat.title)
        return

    # ── New user registration ─────────────────────────────────────────────────
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(
            LOG_CHANNEL,
            get("en", "LOG_TEXT_P",
                user_id=message.from_user.id,
                name=message.from_user.mention)
        )
        tz = pytz.timezone('Asia/Kolkata')
        VERIFIED[message.from_user.id] = str(date.today())
        await m.delete()

        # First-time user → show language picker before anything else
        from plugins.help import _lang_kb
        await message.reply_text(
            get("en", "LANG_SELECT_MSG"),
            reply_markup=_lang_kb(),
            parse_mode=enums.ParseMode.HTML
        )
        return

    # ── Simple /start (no payload) ────────────────────────────────────────────
    if len(message.command) != 2:
        buttons = [
            [InlineKeyboardButton(get_btn(lang, "BTN_SHARE"),  url=Share_msg)],
            [
                InlineKeyboardButton(get_btn(lang, "BTN_SEARCH"), switch_inline_query_current_chat=""),
                InlineKeyboardButton(get_btn(lang, "BTN_GROUP"),  url=GRP_LNK),
            ],
            [
                InlineKeyboardButton(get_btn(lang, "BTN_HELP"),  callback_data="help"),
                InlineKeyboardButton(get_btn(lang, "BTN_ABOUT"), callback_data="about"),
            ],
        ]
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=get(lang, "START", name=message.from_user.mention,
                        uname=temp.U_NAME, bname=temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return

    # ── Force subscribe gate ──────────────────────────────────────────────────
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            await m.delete()
            invite_link = await client.create_chat_invite_link(AUTH_CHANNELS)
        except ChatAdminRequired:
            logger.error("Bot is not admin in AUTH_CHANNEL — cannot create invite link")
            return
        except Exception:
            return

        btn = [[InlineKeyboardButton(get_btn(lang, "BTN_JOIN_CHANNEL"), url=invite_link.invite_link)]]
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton(get_btn(lang, "BTN_TRY_AGAIN"),
                                                 callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(get_btn(lang, "BTN_TRY_AGAIN"),
                                                 url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])

        await client.send_message(
            chat_id=message.from_user.id,
            text=get(lang, "FORCE_SUB_MSG"),
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.HTML
        )
        dlog("FORCE_SUB_GATE", user_id=message.from_user.id)
        return

    # ── /start subscribe|error|okay|help ─────────────────────────────────────
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [InlineKeyboardButton(get_btn(lang, "BTN_ADD_TO_GROUP"),
                                  url=f"http://t.me/{temp.U_NAME}?startgroup=true")],
            [
                InlineKeyboardButton(get_btn(lang, "BTN_SEARCH"), switch_inline_query_current_chat=""),
                InlineKeyboardButton(get_btn(lang, "BTN_GROUP"),  url=GRP_LNK),
            ],
            [
                InlineKeyboardButton(get_btn(lang, "BTN_HELP"),  callback_data="help"),
                InlineKeyboardButton(get_btn(lang, "BTN_ABOUT"), callback_data="about"),
            ],
        ]
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=get(lang, "START", name=message.from_user.mention,
                        uname=temp.U_NAME, bname=temp.B_NAME),
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode=enums.ParseMode.HTML
        )
        return

    # ── Deep-link dispatch ────────────────────────────────────────────────────
    data = message.command[1]
    try:
        pre, file_id = data.split("_", 1)
    except Exception:
        file_id = data
        pre = ""

    # BATCH link
    if data.split("-", 1)[0] == "BATCH":
        await _handle_batch(client, message, m, data, lang)
        return

    # verify link
    if data.split("-", 1)[0] == "verify":
        await _handle_verify(client, message, m, data, lang)
        return

    # sendfiles (single-click all-files link)
    if data.startswith("sendfiles"):
        await m.delete()
        await message.reply(get(lang, "FILE_NOT_FOUND"))   # g undefined — guard
        return

    # all-files link
    if data.startswith("all"):
        await _handle_all_files(client, message, m, data, file_id, pre, lang)
        return

    # DSTORE link
    if data.split("-", 1)[0] == "DSTORE":
        await _handle_dstore(client, message, m, data, lang)
        return

    # Single file
    await _handle_single_file(client, message, m, data, file_id, pre, lang)


# ─────────────────────────────────────────────────────────────────────────────
# Deep-link sub-handlers (keeps /start readable)
# ─────────────────────────────────────────────────────────────────────────────

def _file_buttons(lang: str) -> list:
    return [
        [InlineKeyboardButton(get_btn(lang, "BTN_JOIN_OFFER"), url=OFR_CNL)],
        [InlineKeyboardButton(get_btn(lang, "BTN_DONATE"),     callback_data="donation")],
    ]


async def _handle_batch(client, message, m, data, lang):
    await m.delete()
    sts = await message.reply(get(lang, "FILE_WAIT"))
    batch_id = data.split("-", 1)[1]
    batch_metadata = await get_batch_by_id(batch_id)

    if not batch_metadata:
        return await sts.edit(get(lang, "BATCH_NOT_FOUND"))

    files_metadata = batch_metadata.get("file_data")
    batch_name     = batch_metadata.get("batch_name", "Unnamed Batch")
    optional_msg   = batch_metadata.get("optional_message", "")

    if not files_metadata:
        return await sts.edit(get(lang, "BATCH_NO_FILES"))
    if not isinstance(files_metadata, builtins.list):
        return await sts.edit(get(lang, "BATCH_INVALID_DATA"))

    await message.reply(get(lang, "BATCH_INFO",
                            name=batch_name,
                            msg=optional_msg or "—",
                            count=len(files_metadata)))

    files_sent = []
    for fm in files_metadata:
        try:
            title   = clean_file_name(fm.get("title"))
            size    = get_size(int(fm.get("size", 0)))
            caption = fm.get("caption", "")
            protect = fm.get("protect", False)

            if BATCH_FILE_CAPTION:
                try:
                    caption = BATCH_FILE_CAPTION.format(
                        file_name=clean_file_name(title) or "",
                        file_size=size or "",
                        file_caption=caption or ""
                    )
                except Exception:
                    caption = caption or title or "File"

            unique_link = fm.get("unique_link")
            fetched     = await fetch_file_by_link(batch_id, unique_link)
            if fetched:
                fid = fetched.get("file_id")
                if fid:
                    msg = await client.send_cached_media(
                        chat_id=message.from_user.id,
                        file_id=fid,
                        caption=caption,
                        protect_content=protect,
                        reply_markup=InlineKeyboardMarkup(_file_buttons(lang))
                    )
                    files_sent.append(msg)
                    dlog("BATCH_FILE_SENT", user_id=message.from_user.id,
                         extra={"link": unique_link})
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as exc:
            logger.warning("Batch send error: %s", exc)

        await asyncio.sleep(0.5)

    await sts.delete()
    minutes = int(DLTTM // 60) if DLTTM >= 60 else 1
    cleanup = await client.send_message(
        message.from_user.id,
        get(lang, "DELETEMSG", minutes=minutes),
        protect_content=True
    )
    await asyncio.sleep(DLTTM)
    for msg in files_sent:
        try:
            await msg.delete()
        except Exception:
            pass
    await cleanup.edit_text(get(lang, "ALL_DELETED_OK"))
    dlog("BATCH_DONE", user_id=message.from_user.id)


async def _handle_verify(client, message, m, data, lang):
    parts = data.split("-")
    userid = parts[1] if len(parts) > 1 else ""
    token  = parts[2] if len(parts) > 2 else ""

    if str(message.from_user.id) != str(userid):
        await m.delete()
        return await message.reply_text(get(lang, "VERIFY_INVALID_LINK"), protect_content=True)

    from utils import check_token, verify_user
    is_valid = await check_token(client, userid, token)
    if is_valid:
        await m.delete()
        n = await message.reply_text(
            get(lang, "VERIFY_SUCCESS", name=message.from_user.mention),
            protect_content=True
        )
        await verify_user(client, userid, token)
        dlog("VERIFY_OK", user_id=message.from_user.id)
        await asyncio.sleep(300)
        await n.delete()
    else:
        await m.delete()
        await message.reply_text(get(lang, "VERIFY_INVALID_LINK"), protect_content=True)


async def _handle_all_files(client, message, m, data, file_id, pre, lang):
    await m.delete()
    files = temp.GETALL.get(file_id)
    if not files:
        return await message.reply(get(lang, "FILE_NOT_FOUND"))

    if VERIFY:
        from utils import check_verification, get_token
        if not await check_verification(client, message.from_user.id):
            btn = [
                [InlineKeyboardButton(get_btn(lang, "BTN_VERIFY"),
                                      url=await get_token(client, message.from_user.id,
                                                          f"https://telegram.me/{temp.U_NAME}?start="))],
                [InlineKeyboardButton(get_btn(lang, "BTN_VERIFY_HOW"), url=VERIFY_TUTORIAL)],
            ]
            return await message.reply_text(
                get(lang, "VERIFY_REQUIRED"),
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )

    filesarr = []
    for file in files:
        fid    = file["file_id"]
        files1 = await get_file_details1(fid)
        title  = clean_file_name(files1["file_name"])
        size   = get_size(files1["file_size"])
        f_cap  = files1["caption"]

        if CUSTOM_FILE_CAPTION:
            try:
                f_cap = CUSTOM_FILE_CAPTION.format(
                    file_name=title, file_size=size, file_caption=f_cap)
            except Exception:
                f_cap = f_cap or title
        if not f_cap:
            f_cap = title

        msg = await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=fid,
            caption=f_cap,
            protect_content=(pre == "filep"),
            reply_markup=InlineKeyboardMarkup(_file_buttons(lang))
        )
        filesarr.append(msg)
        dlog("ALL_FILE_SENT", user_id=message.from_user.id)

    minutes = int(DLTTM // 60) if DLTTM >= 60 else 1
    k = await client.send_message(
        message.from_user.id,
        get(lang, "DELETEMSG", minutes=minutes),
        protect_content=True
    )
    await asyncio.sleep(DLTTM)
    for x in filesarr:
        await x.delete()
    await k.edit_text(get(lang, "ALL_DELETED_OK"))


async def _handle_dstore(client, message, m, data, lang):
    await m.delete()
    sts = await message.reply(get(lang, "FILE_WAIT"))
    b_string = data.split("-", 1)[1]
    decoded  = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
    try:
        f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
    except Exception:
        f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
        protect = "/pbatch" if PROTECT_CONTENT else "batch"

    async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
        if msg.media:
            media = getattr(msg, msg.media.value)
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(
                        file_name=getattr(media, "file_name", ""),
                        file_size=getattr(media, "file_size", ""),
                        file_caption=getattr(msg, "caption", "")
                    )
                except Exception:
                    f_caption = getattr(msg, "caption", "")
            else:
                f_caption = getattr(msg, "caption", getattr(media, "file_name", ""))
            try:
                await msg.copy(message.chat.id, caption=f_caption,
                               protect_content=(protect == "/pbatch"))
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await msg.copy(message.chat.id, caption=f_caption,
                               protect_content=(protect == "/pbatch"))
            except Exception as exc:
                logger.exception(exc)
        elif msg.empty:
            continue
        else:
            try:
                await msg.copy(message.chat.id, protect_content=(protect == "/pbatch"))
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await msg.copy(message.chat.id, protect_content=(protect == "/pbatch"))
            except Exception as exc:
                logger.exception(exc)
        await asyncio.sleep(0.5)
    await sts.delete()


async def _handle_single_file(client, message, m, data, file_id, pre, lang):
    if VERIFY:
        from utils import check_verification, get_token
        if not await check_verification(client, message.from_user.id):
            btn = [
                [InlineKeyboardButton(get_btn(lang, "BTN_VERIFY"),
                                      url=await get_token(client, message.from_user.id,
                                                          f"https://telegram.me/{temp.U_NAME}?start="))],
                [InlineKeyboardButton(get_btn(lang, "BTN_VERIFY_HOW"), url=VERIFY_TUTORIAL)],
            ]
            await m.delete()
            return await message.reply_text(
                get(lang, "VERIFY_REQUIRED"),
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )

    files_ = await get_file_details(file_id)

    if not files_:
        # Try base64 decode fallback
        try:
            pre, file_id = ((base64.urlsafe_b64decode(
                data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=(pre == "filep"),
            )
            filetype = msg.media
            file     = getattr(msg, filetype.value)
            title    = clean_file_name(file.file_name)
            size     = get_size(file.file_size)
            f_cap    = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_cap = CUSTOM_FILE_CAPTION.format(
                        file_name=title or "", file_size=size or "", file_caption="")
                except Exception:
                    pass
            await msg.edit_caption(f_cap)
            minutes = int(DLTTM // 60) if DLTTM >= 60 else 1
            k = await msg.reply(get(lang, "DELETEMSG", minutes=minutes),
                                quote=True, protect_content=True)
            await asyncio.sleep(DLTTM)
            await msg.delete()
            await k.edit_text(get(lang, "FILE_DELETED_OK"))
            dlog("SINGLE_FILE_B64", user_id=message.from_user.id)
        except Exception:
            pass
        return await message.reply(get(lang, "FILE_NOT_FOUND"))

    files = files_[0]
    title = clean_file_name(files.file_name)
    size  = get_size(files.file_size)
    f_cap = files.caption

    if CUSTOM_FILE_CAPTION:
        try:
            f_cap = CUSTOM_FILE_CAPTION.format(
                file_name=title or "", file_size=size or "", file_caption=f_cap or "")
        except Exception as exc:
            logger.exception(exc)
    if f_cap is None:
        f_cap = files.file_name

    await m.delete()
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_cap,
        protect_content=(pre == "filep"),
        reply_markup=InlineKeyboardMarkup(_file_buttons(lang))
    )
    minutes = int(DLTTM // 60) if DLTTM >= 60 else 1
    k = await msg.reply(get(lang, "DELETEMSG", minutes=minutes),
                        quote=True, protect_content=True)
    dlog("SINGLE_FILE_SENT", user_id=message.from_user.id,
         extra={"file": files.file_name})
    await asyncio.sleep(DLTTM)
    await msg.delete()
    await k.edit_text(get(lang, "FILE_DELETED_OK"))


# ─────────────────────────────────────────────────────────────────────────────
# /channel  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("channel") & filters.user(ADMINS))
async def channel_info(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    channels = [CHANNELS] if isinstance(CHANNELS, (int, str)) else CHANNELS
    text = "📑 <b>Indexed channels/groups</b>\n"
    for ch in channels:
        chat = await bot.get_chat(ch)
        text += "\n@" + chat.username if chat.username else "\n" + (chat.title or chat.first_name)
    text += f"\n\n<b>Total:</b> {len(CHANNELS)}"
    if len(text) < 4096:
        await message.reply(text, parse_mode=enums.ParseMode.HTML)
    else:
        fname = "indexed_channels.txt"
        with open(fname, "w") as f:
            f.write(text)
        await message.reply_document(fname)
        os.remove(fname)


# ─────────────────────────────────────────────────────────────────────────────
# /logs  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("logs") & filters.user(ADMINS))
async def log_file(bot, message: Message):
    try:
        await message.reply_document("TelegramBot.log")
    except Exception as exc:
        await message.reply(str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# /delete  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("delete") & filters.user(ADMINS))
async def delete_file(bot, message: Message):
    lang  = await db.get_user_lang(message.from_user.id)
    reply = message.reply_to_message
    if not (reply and reply.media):
        return await message.reply(get(lang, "REPLY_TO_FILE"), quote=True)

    msg = await message.reply(get(lang, "PROCESSING"), quote=True)

    for ftype in ("document", "video", "audio"):
        media = getattr(reply, ftype, None)
        if media is not None:
            break
    else:
        return await msg.edit(get(lang, "UNSUPPORTED_FMT"))

    file_id, _ = unpack_new_file_id(media.file_id)
    result = await Media.collection.delete_one({"_id": file_id})
    if result.deleted_count:
        return await msg.edit(get(lang, "FILE_DEL_DB_OK"))

    file_name = re.sub(r"(_|\-|\.|\\+)", " ", str(media.file_name))
    result = await Media.collection.delete_many({
        "file_name": file_name, "file_size": media.file_size, "mime_type": media.mime_type
    })
    if result.deleted_count:
        return await msg.edit(get(lang, "FILE_DEL_DB_OK"))

    result = await Media.collection.delete_many({
        "file_name": media.file_name, "file_size": media.file_size, "mime_type": media.mime_type
    })
    await msg.edit(get(lang, "FILE_DEL_DB_OK") if result.deleted_count else get(lang, "FILE_NOT_IN_DB"))


# ─────────────────────────────────────────────────────────────────────────────
# /deleteall  (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("deleteall") & filters.user(ADMINS))
async def delete_all_index(bot, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.reply_text(
        get(lang, "DELETE_ALL_CONFIRM"),
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton(get_btn(lang, "BTN_YES"),    callback_data="autofilter_delete")],
            [InlineKeyboardButton(get_btn(lang, "BTN_CANCEL"), callback_data="close_data")],
        ]),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r"^autofilter_delete"))
async def delete_all_index_confirm(bot, query):
    lang = await db.get_user_lang(query.from_user.id)
    await Media.collection.drop()
    await query.answer(get(lang, "DELETE_THANK"))
    await query.message.edit(get(lang, "DELETE_ALL_DONE"))


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


# ─────────────────────────────────────────────────────────────────────────────
# /scrub  — bulk DB purge with pattern matching (admin)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("scrub") & filters.user(ADMINS))
async def scrub_database(client, message: Message):
    lang = await db.get_user_lang(message.from_user.id)
    if len(message.command) < 2:
        return await message.reply_text(get(lang, "SCRUB_USAGE"))

    raw_args = message.text.split(maxsplit=1)[1].strip()

    # 1. Parse 'name:' parameter
    pattern = None
    name_match = re.search(r"name:\s*(.*?)(?=\s*size:|$)", raw_args, re.IGNORECASE | re.DOTALL)
    if name_match:
        pattern = name_match.group(1).strip()
    
    # 2. Parse 'size:' parameter
    size_args = None
    size_match = re.search(r"size:\s*(.*)", raw_args, re.IGNORECASE | re.DOTALL)
    if size_match:
        size_args = size_match.group(1).strip()

    # Fallback if the user didn't use parameters explicitly, treat the whole string as the name
    if not name_match and not size_match:
        pattern = raw_args

    db_query = {}

    # 3. Build File Name Query
    if pattern:
        # Flatten special characters for matching if your database normalizes them, 
        # or use directly with wildcards converted safely.
        clean_pattern = re.sub(r'[^a-zA-Z0-9\s\*]', ' ', pattern)
        safe_pat = re.escape(clean_pattern).replace(r"\*", ".*")
        # Removing strict ^ and $ anchors so it behaves like a flexible search string
        db_query["file_name"] = {"$regex": f"{safe_pat}", "$options": "i"}

    # 4. Build Size Filter Query (Handles ranges like >50MB <1GB)
    size_label = "None"
    if size_args:
        size_query = {}
        all_sizes = re.findall(r"([<>])\s*([\d\.]+)\s*([KMG]?B)", size_args.upper())
        
        labels = []
        for op, val, unit in all_sizes:
            val = float(val)
            mult = {"KB": 1024, "MB": 1024**2, "GB": 1024**3}.get(unit, 1)
            size_bytes = int(val * mult)
            
            if op == ">":
                size_query["$gt"] = size_bytes
            elif op == "<":
                size_query["$lt"] = size_bytes
            labels.append(f"{op}{val}{unit}")
                
        if size_query:
            db_query["file_size"] = size_query
            size_label = " ".join(labels)

    if not db_query:
        return await message.reply_text(get(lang, "SCRUB_USAGE"))

    msg = await message.reply_text(get(lang, "SCRUB_SCANNING"))
    try:
        pipeline = [{"$match": db_query}, {"$group": {
            "_id": None, "total_count": {"$sum": 1},
            "max_size": {"$max": "$file_size"}, "min_size": {"$min": "$file_size"}
        }}]
        stats_cur = Media.collection.aggregate(pipeline)
        stats     = await stats_cur.to_list(length=1)
        if not stats:
            return await msg.edit_text(get(lang, "SCRUB_NOT_FOUND", pattern=pattern or "None"))

        stats       = stats[0]
        total_count = stats.get("total_count", 0)
        max_size    = get_size(stats.get("max_size", 0))
        min_size    = get_size(stats.get("min_size", 0))

        samples_cur  = Media.collection.find(db_query).limit(5)
        sample_docs  = await samples_cur.to_list(length=5)
        sample_names = "\n".join([f" ├ <code>{d['file_name']}</code>" for d in sample_docs])

        query_id           = str(uuid.uuid4())[:8]
        PURGE_CACHE[query_id] = db_query

        text = get(lang, "SCRUB_CONFIRM",
                   pattern=pattern or "None", size=size_label,
                   count=total_count, min_size=min_size, max_size=max_size,
                   samples=sample_names)
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_DELETE_ALL_DB"), callback_data=f"purge_yes_{query_id}"),
            InlineKeyboardButton(get_btn(lang, "BTN_CANCEL"),        callback_data=f"purge_no_{query_id}"),
        ]]
        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons),
                            parse_mode=enums.ParseMode.HTML)
        dlog("SCRUB_SCAN", user_id=message.from_user.id,
             extra={"pattern": pattern or "None", "count": total_count})

    except Exception as exc:
        logger.exception("Scrub scan error")
        await msg.edit_text(get(lang, "SCRUB_ERROR", error=str(exc)))


@Client.on_callback_query(filters.regex(r"^purge_(yes|no)_"))
async def handle_purge_confirmation(client, query):
    lang     = await db.get_user_lang(query.from_user.id)
    parts    = query.data.split("_")
    action   = parts[1]           # "yes" or "no"
    query_id = parts[2]

    if str(query.from_user.id) not in [str(a) for a in ADMINS]:
        return await query.answer(get(lang, "SCRUB_ADMIN_ONLY"), show_alert=True)

    if action == "no":
        PURGE_CACHE.pop(query_id, None)
        return await query.message.edit_text(get(lang, "SCRUB_CANCELLED"))

    if action == "yes":
        db_query = PURGE_CACHE.pop(query_id, None)
        if not db_query:
            return await query.answer(get(lang, "SCRUB_EXPIRED"), show_alert=True)

        await query.answer("Deleting... please wait.", show_alert=True)
        try:
            result = await Media.collection.delete_many(db_query)
            await query.message.edit_text(get(lang, "SCRUB_DONE", count=result.deleted_count))
            dlog("SCRUB_DONE", user_id=query.from_user.id,
                 extra={"deleted": result.deleted_count})
        except Exception as exc:
            logger.exception("Scrub delete error")
            await query.message.edit_text(get(lang, "SCRUB_ERROR", error=str(exc)))
