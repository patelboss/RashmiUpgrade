import logging
import asyncio
import time
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from info import ADMINS
from info import INDEX_REQ_CHANNEL as LOG_CHANNEL
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import temp
import re
from pyrogram.enums import ParseMode, ChatMemberStatus
import time  # Importing the time module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
lock = asyncio.Lock()

# Retry mechanism for handling FloodWait errors
async def retry_on_floodwait(func, *args, **kwargs):
    while True:
        try:
            return await func(*args, **kwargs)
        except FloodWait as e:
            print(dir(e))  # Lists all attributes of the exception
            print(f"Flood wait for {e.value} seconds.")  # Correct attribute
            logger.warning(f"FloodWait Error, retrying after {e.value} seconds...")
            await asyncio.sleep(e.value)

@Client.on_callback_query(filters.regex(r'^index'))
async def index_files(bot, query):
    if query.data.startswith('index_cancel'):
        temp.CANCEL = True
        return await query.answer("Cancelling Indexing")
    
    _, raju, chat, lst_msg_id, from_user = query.data.split("#")
    if raju == 'reject':
        await query.message.delete()
        await bot.send_message(int(from_user),
                               f'<b>Your Submission for indexing {chat} has been declined by our moderators.\nThis is may be because your channel not have media file\n\nIf you have anything to tell admin \ntype message and reply that message by /feedback<b>', parse_mode=ParseMode.HTML,
                               reply_to_message_id=int(lst_msg_id))
        return

    if lock.locked():
        return await query.answer('Wait until previous process completes.', show_alert=True)

    msg = query.message

    await query.answer('Processing...⏳', show_alert=True)
    if int(from_user) not in ADMINS:
        await bot.send_message(int(from_user),
                               f'Your Submission for indexing {chat} has been accepted by our moderators and will be added soon.',
                               reply_to_message_id=int(lst_msg_id))

    await msg.edit(
        "Starting Indexing",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton('Cancel', callback_data='index_cancel')]]
        )
    )

    try:
        chat = int(chat)
    except:
        chat = chat

    # Start the indexing process with time tracking
    await index_files_to_db(int(lst_msg_id), chat, msg, bot)


@Client.on_message(filters.command("index") & filters.private)
async def index_command(bot, message):
    # Check if the command is a reply to a forwarded message
    if not message.reply_to_message:
        return await message.reply("Please reply to a forwarded message to use the /index command.")
    
    # Process the replied message
    replied_msg = message.reply_to_message

    # For forwarded messages or valid Telegram links
    if replied_msg.forward_from_chat or replied_msg.text:
        # Extract details from forwarded message or link
        if replied_msg.text:
            regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
            match = regex.match(replied_msg.text)
            if not match:
                return await message.reply(f"<b>This is link but i can't join by this.\n\nplease add me in channel and send me any media file then reply /index</b>", parse_mode=ParseMode.HTML)

            chat_id = match.group(4)
            last_msg_id = int(match.group(5))
            if chat_id.isnumeric():
                chat_id = int("-100" + chat_id)

        elif replied_msg.forward_from_chat.type == enums.ChatType.CHANNEL:
            last_msg_id = replied_msg.forward_from_message_id
            chat_id = replied_msg.forward_from_chat.username or replied_msg.forward_from_chat.id
        else:
            return await message.reply(f"<b>Unsupported message type. Please reply to a valid forwarded message or link.</b>", parse_mode=ParseMode.HTML)

        # Check bot permissions and chat validity
        try:
            await bot.get_chat(chat_id)
        except ChannelInvalid:
            return await message.reply(f"<b>This may be a private channel/group. Make me an admin over there to index the files.</b>", parse_mode=ParseMode.HTML)
        except (UsernameInvalid, UsernameNotModified):
            return await message.reply("Invalid Link specified.")
        except Exception as e:
            logger.exception(e)
            return await message.reply(f"Errors - {e}")

        # Verify message ID exists
        try:
            k = await bot.get_messages(chat_id, last_msg_id)
        except:
            return await message.reply(f"<b>Make sure I am an admin in the channel, if the channel is private.</b>", parse_mode=ParseMode.HTML)

        if k.empty:
            return await message.reply(f"<b> I am not an admin of the group.</b>", parse_mode=ParseMode.HTML)

        # Handle admin request or send to moderators
        if message.from_user.id in ADMINS:
            buttons = [
                [InlineKeyboardButton("Yes", callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}")],
                [InlineKeyboardButton("close", callback_data="close_data")]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            return await message.reply(
                f"<b>Do you want to index this Channel/Group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code></b>", parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )

        if type(chat_id) is int:
            try:
                link = (await bot.create_chat_invite_link(chat_id)).invite_link
            except ChatAdminRequired:
                return await message.reply(f"<b>Make sure I am an admin in the chat and have permission to invite users.</b>", parse_mode=ParseMode.HTML)
        else:
            link = f"@{replied_msg.forward_from_chat.username}"

        buttons = [
            [InlineKeyboardButton("Accept Index", callback_data=f"index#accept#{chat_id}#{last_msg_id}#{message.from_user.id}")],
            [InlineKeyboardButton("Reject Index", callback_data=f"index#reject#{chat_id}#{message.id}#{message.from_user.id}")]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await bot.send_message(
            LOG_CHANNEL,
            f"#IndexRequest\n\nBy: {message.from_user.mention} (<code>{message.from_user.id}</code>)\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\nInviteLink: {link}",
            reply_markup=reply_markup
        )
        return await message.reply(f"<b>Thank you for the contribution. Wait for my moderators to verify the files.</b>", parse_mode=ParseMode.HTML)
    else:
        return await message.reply(f"<b>Please reply to a forwarded message or a valid link to use the /index command.</b>", parse_mode=ParseMode.HTML)


@Client.on_message(filters.command('setskip') & filters.user(ADMINS))
async def set_skip_number(bot, message):
    if ' ' in message.text:
        _, skip = message.text.split(" ")
        try:
            skip = int(skip)
        except:
            return await message.reply("Skip number should be an integer.")
        await message.reply(f"Successfully set SKIP number as {skip}")
        temp.CURRENT = int(skip)
    else:
        await message.reply("Give me a skip number.")


# Function to format time in human-readable format: e.g., 1m 10s or 12h 20m 30s
def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    # Return formatted time, based on whether it's over an hour or not
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    return f"{minutes}m {seconds}s"

async def index_files_to_db(lst_msg_id, chat, msg, bot):
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
                [InlineKeyboardButton("Cancel", callback_data='index_cancel')]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)

            # Initial message update with cancel button
            await msg.edit(
                "Starting to save files. Click 'Cancel' to stop.",
                reply_markup=reply_markup
            )

            async for message in bot.iter_messages(chat, lst_msg_id, temp.CURRENT):
                if temp.CANCEL:
                    elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
                    formatted_time = format_time(elapsed_time)  # Format the time
                    await msg.edit(
                        f"Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\n"
                        f"Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
                        f"Non-Media messages skipped: <code>{no_media + unsupported}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
                        f"Errors Occurred: <code>{errors}</code>\n"
                        f"Elapsed Time: <code>{formatted_time}</code>",
                        reply_markup=None  # Remove cancel button after process is complete
                    )
                    break

                current += 1
                if current % 100 == 0:
                    elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
                    formatted_time = format_time(elapsed_time)  # Format the time

                    # New message content to be sent
                    new_message_text = (
                        f"Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\n"
                        f"Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
                        f"Non-Media messages skipped: <code>{no_media + unsupported}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
                        f"Errors Occurred: <code>{errors}</code>\n"
                        f"Elapsed Time: <code>{formatted_time}</code>"
                    )

                    # Only edit the message if the content is different
                    if new_message_text != last_message_text:
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
            await msg.edit(f"Error: {e}", reply_markup=None)
        else:
            elapsed_time = round(time.time() - start_time)  # Calculate elapsed time
            formatted_time = format_time(elapsed_time)  # Format the time
            await msg.edit(
                f"Successfully saved <code>{total_files}</code> to dataBase!\n"
                f"Duplicate Files Skipped: <code>{duplicate}</code>\n"
                f"Deleted Messages Skipped: <code>{deleted}</code>\n"
                f"Non-Media messages skipped: <code>{no_media + unsupported}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
                f"Errors Occurred: <code>{errors}</code>\n"
                f"Elapsed Time: <code>{formatted_time}</code>",
                reply_markup=None  # Remove cancel button after process is complete
            )
