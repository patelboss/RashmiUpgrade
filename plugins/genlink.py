import re
import logging
import hashlib
from pyrogram import Client, filters
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, UsernameInvalid, UsernameNotModified
from info import LOG_CHANNEL, PUBLIC_FILE_CHANNEL, BATCH_FILE_CHANNEL, ADMINS, DEBUG_MODE
from database.batch_filedb import save_batch_details
from database.users_chats_db import db
from utils import temp
from langs.i18n import get, get_btn
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Remove admin verification: Allow everyone
async def allowed(_, __, message):
    if DEBUG_MODE:
        logger.info("[BATCH] access check for user: %s", message.from_user.id)
    return True  # Allow everyone

@Client.on_message(filters.command(['batch', 'pbatch']) & filters.create(allowed) & filters.user(ADMINS))
async def gen_link_batch(bot, message):
    lang = await db.get_user_lang(message.from_user.id)
    if DEBUG_MODE:
        logger.info("[BATCH] /batch command from user: %s", message.from_user.id)

    links = message.text.strip().split(" ")
    if DEBUG_MODE:
        logger.info("[BATCH] parsing batch links from user: %s", message.from_user.id)

    if len(links) < 3:  # Minimum: Command + at least 2 links
        if DEBUG_MODE:
            logger.warning("[BATCH] incorrect batch command format from user: %s", message.from_user.id)
        return await message.reply(get(lang, "BATCH_USAGE"))

    cmd = links[0]
    links = links[1:]  # Remove the command from the links

    def validate_link(link):
        regex = re.compile(r"(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(link)
        if not match:
            if DEBUG_MODE:
                logger.warning("[BATCH] invalid link format: %s", link)
            return None, None
        chat_id = match.group(4)
        msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id = int("-100" + chat_id)  # Convert to negative for supergroups
        return chat_id, msg_id

    processed_links = [validate_link(link) for link in links]
    if DEBUG_MODE:
        logger.info("[BATCH] validated links: %s", processed_links)

    if any(link is None for link in processed_links):
        if DEBUG_MODE:
            logger.warning("[BATCH] invalid link(s) provided by user: %s", message.from_user.id)
        return await message.reply(get(lang, "BATCH_INVALID_LINKS"))

    chat_ids = {chat_id for chat_id, _ in processed_links if chat_id}
    if len(chat_ids) > 1:
        if DEBUG_MODE:
            logger.warning("[BATCH] links from different chats detected: %s", message.from_user.id)
        return await message.reply(get(lang, "BATCH_DIFFERENT_CHATS"))

    chat_id = next(iter(chat_ids))
    if DEBUG_MODE:
        logger.info("[BATCH] resolved chat ID: %s", chat_id)

    try:
        if DEBUG_MODE:
            logger.info("[BATCH] fetching chat details for chat ID: %s", chat_id)
        chat_id = (await bot.get_chat(chat_id)).id
        if DEBUG_MODE:
            logger.info("[BATCH] chat ID resolved: %s", chat_id)
    except (ChannelInvalid, UsernameInvalid, UsernameNotModified) as e:
        logger.error("[BATCH] error accessing chat: %s", str(e))
        return await message.reply(get(lang, "BATCH_CHAT_ACCESS_ERROR"))
    except Exception as e:
        logger.error("[BATCH] unexpected error: %s", str(e))
        return await message.reply(f"Error: {e}")

    await message.reply(get(lang, "BATCH_ASK_NAME"))  # Ask for the batch name
    response = await bot.listen(message.chat.id)  # Wait for the user's input for the batch name
    batch_name = response.text.strip()  # Assign the batch name
    if DEBUG_MODE:
        logger.info("[BATCH] received batch name: %s", batch_name)

    await message.reply(get(lang, "BATCH_ASK_OPTIONAL_MSG"))  # Ask for the optional message
    response = await bot.listen(message.chat.id)  # Wait for the user's input for the optional message
    optional_message = response.text.strip() if response.text.strip().lower() != 'pass' else ""
    if DEBUG_MODE:
        logger.info("[BATCH] received optional message: %s", optional_message)

    sts = await message.reply(get(lang, "BATCH_PROCESSING"))
    if DEBUG_MODE:
        logger.info("[BATCH] sending processing status update to user")

    outlist = []
    links_sent = 0

    for sequence_num, (_, msg_id) in enumerate(processed_links, 1):
        try:
            if DEBUG_MODE:
                logger.info("[BATCH] fetching message with ID: %s", msg_id)
            msg = await bot.get_messages(chat_id=chat_id, message_ids=msg_id)

            # Ensure the message has media and is either a document, video, or photo
            if not msg or msg.empty or not msg.media:
                continue

            file = getattr(msg, msg.media.value)
            caption = getattr(msg, 'caption', '') or ''
            title = getattr(file, "file_name", 'Unnamed file')
            size = getattr(file, "file_size", 0)

            # Generate a unique hash for each file based on file_id and sequence_num
            file_hash = hashlib.sha256(f"{file.file_id}{sequence_num}".encode()).hexdigest()[:15]
            unique_link = file_hash  # Use the file hash directly as the unique link

            outlist.append({
                "file_id": file.file_id,
                "caption": caption,
                "title": title,
                "size": size,
                "protect": cmd.lower() == "/pbatch",  # Optional protection for batch
                "unique_link": unique_link
            })

            links_sent += 1

        except Exception as e:
            logger.exception("Error processing message ID: %s", msg_id)

    # Save the batch details and get the batch ID
    batch_id = await save_batch_details(outlist, batch_name, optional_message)
    if DEBUG_MODE:
        logger.info("[BATCH] batch details saved in db for Batch ID: %s", batch_id)

    # Generate the batch link
    short_link = f"https://t.me/{temp.U_NAME}?start=BATCH-{batch_id}"
    await sts.edit(get(lang, "BATCH_CREATED", name=batch_name, count=links_sent, link=short_link))
    if DEBUG_MODE:
        logger.info("[BATCH] batch creation status sent to user")

    # Send log to the admin channel
    await bot.send_message(
        LOG_CHANNEL,
        f"New Batch Created:\nBatch ID: {batch_id}\nName: {batch_name}\n\n"
        f"Link: {short_link}"
    )
    # Send the message with an inline button
    await bot.send_message(
        BATCH_FILE_CHANNEL,
         f"Name: {batch_name}\nDetails: {optional_message}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(get_btn(lang, "BTN_GET_ALL_FILES"), url=short_link)]]
        )
    )
