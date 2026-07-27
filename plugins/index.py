"""
plugins/index.py — /index (channel/group indexing request + moderator
approval flow) and /setskip.

All user-facing strings now go through langs.i18n.get()/get_btn() instead
of hardcoded literals. DEBUG_MODE logging added at each significant step.
No logic changed during this sweep — only text sourcing and logging.
The moderator LOG_CHANNEL post always renders in DEFAULT_LANG since it's
addressed to moderators, not the requesting user.
"""

import logging
import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS, DEBUG_MODE
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from database.users_chats_db import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
from pyrogram.enums import ParseMode, ChatMemberStatus
from langs.i18n import get, get_btn, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


# Retry mechanism for handling FloodWait errors
async def retry_on_floodwait(func, *args, **kwargs):
    while True:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            if DEBUG_MODE:
                logger.info("[INDEX] FloodWait, retrying | seconds=%s", e.value)
            logger.warning(f"FloodWait Error, retrying after {e.value} seconds...")
            await asyncio.sleep(e.value)


@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    lang = await _user_lang(query.from_user)
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        if DEBUG_MODE:
            logger.info("[INDEX] indexing cancelled by user | user_id=%s", query.from_user.id if query.from_user else None)
        return await query.answer(get(lang, "INDEX_CANCELLING"))

    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        if DEBUG_MODE:
            logger.info("[INDEX] request rejected | chat=%s from_user=%s", chat, from_user)
        await query.message.delete()
        await bot.send_message(int(from_user),
                               get(lang, "INDEX_REJECTED_NOTICE", chat=chat), parse_mode=ParseMode.HTML,
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        if DEBUG_MODE:
            logger.info("[INDEX] indexing blocked, lock held | chat=%s", chat)
        return await query.answer(get(lang, "INDEX_WAIT_PROCESS"), show_alert=True)

    msg = query.message

    await query.answer(get(lang, "INDEX_PROCESSING"), show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               get(lang, "INDEX_ACCEPTED_NOTICE", chat=chat),
                               reply_to_message_id=int(lst_msg_id))

    if DEBUG_MODE:
        logger.info("[INDEX] indexing accepted, starting | chat=%s requested_by=%s", chat, from_user)

    await msg.edit(
        get(lang, "INDEX_STARTING"),
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_btn(lang, "BTN_CANCEL_INDEX"), callback_data='index_cancel')]]
        )
    )

    try:
        chat = int(chat)
    except:
        chat = chat

    # Start the indexing process with time tracking
    await index_files_to_db(int(lst_msg_id), chat, msg, bot, lang)


@Client.on_message(filters.command("index") & filters.private)
async def index_command(bot, message):
    lang = await _user_lang(message.from_user)
    # Check if the command is a reply to a forwarded message
    if not message.reply_to_message:
        return await message.reply(get(lang, "INDEX_CMD_NO_REPLY"))

    # Process the replied message
    replied_msg = message.reply_to_message

    # For forwarded messages or valid Telegram links
    if replied_msg.forward_from_chat or replied_msg.text:
        # Extract details from forwarded message or link
        if replied_msg.text:
            regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
            match = regex.match(replied_msg.text)
            if not match:
                if DEBUG_MODE:
                    logger.info("[INDEX] /index: link did not match | user_id=%s", message.from_user.id)
                return await message.reply(get(lang, "INDEX_LINK_CANT_JOIN"), parse_mode=ParseMode.HTML)

            chat_id = match.group(4)
            last_msg_id = int(match.group(5))
            if chat_id.isnumeric():
                chat_id = int("-100" + chat_id)

        elif replied_msg.forward_from_chat.type == enums.ChatType.CHANNEL:
            last_msg_id = replied_msg.forward_from_message_id
            chat_id = replied_msg.forward_from_chat.username or replied_msg.forward_from_chat.id
        else:
            return await message.reply(get(lang, "INDEX_UNSUPPORTED_TYPE"), parse_mode=ParseMode.HTML)

        # Check bot permissions and chat validity
        try:
            await bot.get_chat(chat_id)
        except ChannelInvalid:
            if DEBUG_MODE:
                logger.info("[INDEX] /index: ChannelInvalid | chat_id=%s", chat_id)
            return await message.reply(get(lang, "INDEX_PRIVATE_CHANNEL"), parse_mode=ParseMode.HTML)
        except (UsernameInvalid, UsernameNotModified):
            return await message.reply(get(lang, "INDEX_INVALID_LINK"))
        except Exception as e:
            logger.exception(e)
            return await message.reply(get(lang, "INDEX_GENERIC_ERROR", e=e))

        # Verify message ID exists
        try:
            k = await bot.get_messages(chat_id, last_msg_id)
        except:
            return await message.reply(get(lang, "INDEX_ADMIN_CHECK_FAIL"), parse_mode=ParseMode.HTML)

        if k.empty:
            return await message.reply(get(lang, "INDEX_NOT_ADMIN_GROUP"), parse_mode=ParseMode.HTML)

        # Handle admin request or send to moderators
        if message.from_user.id in ADMINS:
            if DEBUG_MODE:
                logger.info("[INDEX] /index: admin requester, prompting confirm | chat_id=%s user_id=%s", chat_id, message.from_user.id)
            buttons = [
                [InlineKeyboardButton(get_btn(lang, "BTN_YES_INDEX"), callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}")],
                [InlineKeyboardButton(get_btn(lang, "BTN_CLOSE_LOWER"), callback_data="close_data")]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply(
                get(lang, "INDEX_CONFIRM_PROMPT", chat_id=chat_id, last_msg_id=last_msg_id), parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

        if type(chat_id) is int:
            try:
                link = (await bot.create_chat_invite_link(chat_id)).invite_link
            except ChatAdminRequired:
                return await message.reply(get(lang, "INDEX_INVITE_LINK_FAIL"), parse_mode=ParseMode.HTML)
        else:
            link = f"@{replied_msg.forward_from_chat.username}"

        buttons = [
            [InlineKeyboardButton(get_btn(DEFAULT_LANG, "BTN_ACCEPT_INDEX"), callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}")],
            [InlineKeyboardButton(get_btn(DEFAULT_LANG, "BTN_REJECT_INDEX"), callback_data=f"index#reject#{chat_id}#{message.id}#{message.from_user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        if DEBUG_MODE:
            logger.info("[INDEX] /index: non-admin submission forwarded to moderators | chat_id=%s user_id=%s", chat_id, message.from_user.id)
        await bot.send_message(
            LOG_CHANNEL,
            get(DEFAULT_LANG, "INDEX_LOG_REQUEST", mention=message.from_user.mention, user_id=message.from_user.id, chat_id=chat_id, last_msg_id=last_msg_id, link=link),
            reply_markup=reply_markup
        )
        return await message.reply(get(lang, "INDEX_THANKS_CONTRIBUTION"), parse_mode=ParseMode.HTML)
    else:
        return await message.reply(get(lang, "INDEX_CMD_INVALID_REPLY"), parse_mode=ParseMode.HTML)


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    lang = await _user_lang(message.from_user)
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply(get(lang, "SETSKIP_NOT_INT"))
        await message.reply(get(lang, "SETSKIP_SUCCESS", skip=skip))
        if DEBUG_MODE:
            logger.info("[INDEX] /setskip: skip number set | skip=%s user_id=%s", skip, message.from_user.id)
        temp.CURRENT = int(skip)
    else:
        await message.reply(get(lang, "SETSKIP_USAGE"))


# Function to format time in human-readable format: e.g., 1m 10s or 12h 20m 30s
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    # Return formatted time, based on whether it's over an hour or not
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"

async def index_files_to_db(lst_msg_id, chat, msg, bot, lang=DEFAULT_LANG):
    total_files = 0
    duplicate = 0
    errors = 0
    deleted = 0
    no_media = 0
    unsupported = 0

    start_time = time.time()  # Start time tracking

    last_message_text = ""  # To store the last edited message content

    async with lock:
        try:
            current = temp.CURRENT
            temp.CANCEL = False

            buttons = [
                [InlineKeyboardButton(get_btn(lang, "BTN_CANCEL_INDEX"), callback_data='index_cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            # Initial message update with cancel button
            await msg.edit(
                get(lang, "INDEX_PROGRESS_START"),
                reply_markup=reply_markup
            )

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
                    formatted_time = format_time(elapsed_time)  # Format the time
                    if DEBUG_MODE:
                        logger.info("[INDEX] indexing cancelled mid-run | saved=%s errors=%s", total_files, errors)
                    await msg.edit(
                        get(
                            lang, "INDEX_PROGRESS_CANCELLED",
                            total_files=total_files, duplicate=duplicate, deleted=deleted,
                            no_media_total=no_media + unsupported, unsupported=unsupported,
                            errors=errors, formatted_time=formatted_time
                        ),
                        reply_markup=None  # Remove cancel button after process is complete
                    )
                    break

                current += 1
                if current % 100 == 0:
                    elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
                    formatted_time = format_time(elapsed_time)  # Format the time

                    # New message content to be sent
                    new_message_text = get(
                        lang, "INDEX_PROGRESS_UPDATE",
                        current=current, total_files=total_files, duplicate=duplicate, deleted=deleted,
                        no_media_total=no_media + unsupported, unsupported=unsupported,
                        errors=errors, formatted_time=formatted_time
                    )

                    # Only edit the message if the content is different
                    if new_message_text != last_message_text:
                        if DEBUG_MODE:
                            logger.info("[INDEX] progress tick | current=%s saved=%s", current, total_files)
                        retry_count = 0
                        while retry_count < 5:  # Retry logic for editing the message
                            try:
                                await msg.edit_text(new_message_text, reply_markup=reply_markup)
                                last_message_text = new_message_text  # Update last message content
                                break
                            except TimeoutError:
                                retry_count += 1
                                await asyncio.sleep(1)
                            except Exception as e:
                                logger.exception(f"Error while editing message: {e}")
                                break

                if message.empty:
                    deleted += 1
                    continue
                elif not message.media:
                    no_media += 1
                    continue
                elif message.media not in [enums.MessageMediaType.VIDEO, enums.MessageMediaType.AUDIO, enums.MessageMediaType.DOCUMENT]:
                    unsupported += 1
                    continue

                media = getattr(message, message.media.value, None)
                if not media:
                    unsupported += 1
                    continue

                media.file_type = message.media.value
                media.caption = message.caption

                retry_count = 0
                while retry_count < 5:  # Retry 5 times for save_file
                    try:
                        aynav, vnay = await save_file(media)
                        if aynav:
                            total_files += 1
                        elif vnay == 0:
                            duplicate += 1
                        elif vnay == 2:
                            errors += 1
                        break
                    except FloodWait as e:
                        logger.warning(f"Flood wait encountered. Retrying after {e.x} seconds.")
                        await asyncio.sleep(e.x)
                        retry_count += 1
                        continue
                    except Exception as e:
                        logger.exception(f"Error during file save: {e}")
                        errors += 1
                        break

        except Exception as e:
            logger.exception(e)
            await msg.edit(get(lang, "INDEX_ERROR", e=e), reply_markup=None)
        else:
            elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
            formatted_time = format_time(elapsed_time)  # Format the time
            if DEBUG_MODE:
                logger.info("[INDEX] indexing completed | saved=%s duplicate=%s errors=%s", total_files, duplicate, errors)
            await msg.edit(
                get(
                    lang, "INDEX_PROGRESS_DONE",
                    total_files=total_files, duplicate=duplicate, deleted=deleted,
                    no_media_total=no_media + unsupported, unsupported=unsupported,
                    errors=errors, formatted_time=formatted_time
                ),
                reply_markup=None  # Remove cancel button after process is complete
            )
