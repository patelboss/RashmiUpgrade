"""
plugins/commands_start.py — /start and its deep-link sub-handlers.

Split out of plugins/commands.py (which was 931 lines) purely for
readability — this block alone was ~500 lines. No logic changed, only the
file boundary moved. See plugins/commands.py and plugins/commands_admin.py
for the other two pieces.

All user-facing strings are served from langs/i18n.py via get() / get_btn().
Debug events are emitted via debug.dlog() — only printed when DEBUG_MODE=true.
"""

import random
import asyncio
import base64
import builtins

import pytz
from datetime import date

from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.ia_filterdb import get_file_details, get_file_details1
from database.users_chats_db import db
from database.batch_filedb import fetch_file_by_link, get_batch_by_id

from info import (
    LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, PROTECT_CONTENT,
    GRP_LNK, OFR_CNL, Share_msg, AUTH_CHANNEL,
)
from variables import CUSTOM_FILE_CAPTION, VERIFY, VERIFY_TUTORIAL, DLTTM, AUTH_CHANNELS
from utils import get_size, is_subscribed, temp, clean_file_name, VERIFIED
from langs.i18n import get, get_btn
from debug import dlog

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# ── Sticker pool (random greeting) ────────────────────────────────────────────
_STICKER_IDS = [
    "CAACAgUAAxkBAAI15Wd8MrA2SLTI-Li_SmwkWxcxOoTVAALNBAACWe0YVlcLt2c9ppYFHgQ",
    "CAACAgIAAxkBAAI1z2d8MVKnvJ68w1OVqj6XCYTFCNS5AALUEQADwKBJeScB4o8r9AweBA",
    "CAACAgIAAxkBAAI102d8MVe_iLmKqD6BCfGvxxHmNUK4AAK8NwAC2VrBSCneSsfNGnZUHgQ",
    "CAACAgEAAxkBAAI112d8MV0hEjLP2-Re5U3DkgtF_0zsAALJAwACgtDpR9eFnD06DCjbHgQ",
    "CAACAgIAAxkBAAI122d8MWryfJiBYYFQnHswu2MUi0uIAAJiAANOXNIpTqLDGEjEK3EeBA",
]


def _sticker() -> str:
    return random.choice(_STICKER_IDS)


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
                InlineKeyboardButton(get_btn(lang, "BTN_HELP"),  callback_data="help:main"),
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
                InlineKeyboardButton(get_btn(lang, "BTN_HELP"),  callback_data="help:main"),
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
