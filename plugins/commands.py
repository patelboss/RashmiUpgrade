import os
import logging
import random
import asyncio
from Script import script
from pyrogram.types import Message
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_file_details1
from database.users_chats_db import db
from info import CHANNELS, ADMINS, AUTH_CHANNEL, LOG_CHANNEL, PICS, BATCH_FILE_CAPTION, PROTECT_CONTENT
from utils import get_settings, get_size, is_subscribed, save_group_settings, temp, clean_file_name
from utils import *
#from verify import *
from database.connections_mdb import active_connection
import re
from info import *
import json
from database.batch_filedb import fetch_file_by_link, get_batch_by_id, save_batch_details, get_latest_batch_sequence, generate_batch_id
import base64
from variables import CUSTOM_FILE_CAPTION, VERIFY, VERIFY_TUTORIAL, DLTTM, AUTH_CHANNELS
#logger = logging.getLogger(__name__)
import builtins
from datetime import datetime, date
from utils import VERIFIED
import pytz
BATCH_FILES = {}
STREAM_MODE = "False"
#VERIFY = "False"
AUTO_DELETE = "False"
GRP_LNK = "https://t.me/Filmykeedha/306"
#OFR_CNL = "https://t.me/+4dWp2gDjwC43YmJl"
#VERIFY_TUTORIAL = "https://t.me/Filmykeedha/394"
sticker_ids = [
    "CAACAgUAAxkBAAI15Wd8MrA2SLTI-Li_SmwkWxcxOoTVAALNBAACWe0YVlcLt2c9ppYFHgQ",
    "CAACAgIAAxkBAAI1z2d8MVKnvJ68w1OVqj6XCYTFCNS5AALUEQADwKBJeScB4o8r9AweBA",
    "CAACAgIAAxkBAAI102d8MVe_iLmKqD6BCfGvxxHmNUK4AAK8NwAC2VrBSCneSsfNGnZUHgQ",
    "CAACAgEAAxkBAAI112d8MV0hEjLP2-Re5U3DkgtF_0zsAALJAwACgtDpR9eFnD06DCjbHgQ",
    "CAACAgIAAxkBAAI122d8MWryfJiBYYFQnHswu2MUi0uIAAJiAANOXNIpTqLDGEjEK3EeBA"
]
import logging
import sys
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# Configure logging explicitly to write to stdout
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create a stream handler for stdout
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)

# Set a formatter for better readability
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
stdout_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(stdout_handler)
def get_random_sticker():
    return random.choice(sticker_ids)

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="**🔄 𝙿𝚁𝙾𝙲𝙴𝚂𝚂𝙴𝚂 𝚂𝚃𝙾𝙿𝙴𝙳. 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙸𝙽𝙶...**", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("**✅️ 𝙱𝙾𝚃 𝙸𝚂 𝚁𝙴𝚂𝚃𝙰𝚁𝚃𝙴𝙳. 𝙽𝙾𝚆 𝚈𝙾𝚄 𝙲𝙰𝙽 𝚄𝚂𝙴 𝙼𝙴**")
    os.execl(sys.executable, sys.executable, *sys.argv)


@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    #await message.react(emoji="🤩")
    random_sticker = get_random_sticker()
    m = await message.reply_sticker(random_sticker)
    await asyncio.sleep(1)
    
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('🔔 𝗨𝗽𝗱𝗮𝘁𝗲 🤖', url='https://t.me/iAmRashmibot')
            ],
            [
                InlineKeyboardButton('🙆🏻𝗛𝗲𝗹𝗽 🦾', url=f"https://t.me/{temp.U_NAME}?start=help"),
            ]
            ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await m.delete()
        await asyncio.sleep(2) # 😢 https://github.com/patelboss/Rashmibot/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
        if not await db.get_chat(message.chat.id):
            total=await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(message.chat.title, message.chat.id, total, "Unknown"))       
            await db.add_chat(message.chat.id, message.chat.title)
        return 
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
        user = message.from_user
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        VERIFIED[user.id] = str(today)
       # logger.info(f"added in verified.")
        await m.delete()
    if len(message.command) != 2:
        buttons = [[
            InlineKeyboardButton('➕↖️<b> Share To Your Friend</b>↗️➕', url=Share_msg)
            ],[
            InlineKeyboardButton('🔎 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url=GRP_LNK)
            ],[
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            await m.delete()
            invite_link = await client.create_chat_invite_link(AUTH_CHANNELS)
                                                              
        except ChatAdminRequired:
            logger.error("𝗛𝗲𝘆 𝘀𝗼𝗻𝗮, 𝗘𝗸 𝗱𝗳𝗮 𝗰𝗵𝗲𝗰𝗸 𝗸𝗿 𝗹𝗼 𝗸𝗶 𝗺𝗮𝗶𝗻 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗺𝗲𝗶 𝗔𝗱𝗱 𝗵𝘂 𝘆𝗮 𝗻𝗵𝗶...!")
            return

        except Exception as e:
    #        logger.error(f" is subscribe error {e}")
            return 
        btn = [
            [
                InlineKeyboardButton(
                    "⚠️ 𝗝𝗼𝗶𝗻 𝗨𝗽𝗱𝗮𝘁𝗲𝘀 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 ⚠️", url=invite_link.invite_link
                )
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton(" 🔄 𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton(" 🔄 𝗧𝗿𝘆 𝗔𝗴𝗮𝗶𝗻", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
      #  await m.delete()
        await client.send_message(
            chat_id=message.from_user.id,
            text="**𝗣𝗹𝗲𝗮𝘀𝗲 𝗝𝗼𝗶𝗻 𝗠𝘆 𝗨𝗽𝗱𝗮𝘁𝗲𝘀 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝘁𝗼 𝘂𝘀𝗲 𝘁𝗵𝗶𝘀 𝗕𝗼𝘁!**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [[
            InlineKeyboardButton('➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
            ],[
            InlineKeyboardButton('🔎 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url=GRP_LNK)
            ],[
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await m.delete()
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return
    data = message.command[1]
    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    if data.split("-", 1)[0] == "BATCH":
        await m.delete()
        # Notify user that the process is starting
        sts = await message.reply("<b>Please wait...</b>")
        batch_id = data.split("-", 1)[1]

        # Fetch batch metadata from the database
        batch_metadata = await get_batch_by_id(batch_id)

        if not batch_metadata:
            logger.error("Batch ID not found: %s", batch_id)
            return await sts.edit("Invalid or expired batch link.")

#        logger.info("Batch ID %s found. Processing...", batch_id)

        # Extract metadata
        files_metadata = batch_metadata.get("file_data")
        batch_name = batch_metadata.get("batch_name", "Unnamed Batch")
        optional_message = batch_metadata.get("optional_message", "")
        files_sent = []

        # Check if files_metadata exists and is iterable
        if not files_metadata:
            await message.reply("No files found in this batch.")
#            logger.error(f"files_metadata is None or empty for batch {batch_metadata.get('batch_id', 'Unknown')}")
            return

        if not isinstance(files_metadata, builtins.list):
            await message.reply("Invalid file data format in this batch.")
#            logger.error(f"files_metadata is not a list for batch {batch_metadata.get('batch_id', 'Unknown')}. Type: {type(files_metadata)}")
            return

        # Notify user about the batch details
        await message.reply(f"<b>Batch Name:</b> {batch_name}\n"
                            f"<b>Message:</b> {optional_message if optional_message else 'No message provided.'}\n"
                            f"Processing {len(files_metadata)} files...")

        for file_metadata in files_metadata:  # start=1 for sequence number
            try:
                title = clean_file_name(file_metadata.get("title"))
                size = get_size(int(file_metadata.get("size", 0)))  # Assuming get_size is a function to get human-readable size
                caption = file_metadata.get("caption", "")
                protect = file_metadata.get("protect", False)

                # Apply custom caption logic (if defined)
                if "BATCH_FILE_CAPTION" in globals() and BATCH_FILE_CAPTION:
                    try:
                        caption = BATCH_FILE_CAPTION.format(
                            file_name= {clean_file_name(title)} or "",
                            file_size=size or "",
                            file_caption=caption or ""
                        )
                    except Exception as e:
                        logger.exception("Error formatting custom caption: %s", str(e))
                        caption = caption or title or "File"

                # Fetch the file using the unique_link
                unique_link = file_metadata.get("unique_link")  # Use unique_link directly from the database
                
                # Fetch the file using the unique_link
#                logger.info("Fetching file for link: %s", unique_link)
                file_metadata = await fetch_file_by_link(batch_id, unique_link)  # This function should retrieve the file from the store

                if file_metadata:
                    file_id = file_metadata.get('file_id')
                    if file_id:
    
     
                    # Send the file to the user
#                        logger.info("Sending file ID: %s to user", unique_link)
                        msg = await client.send_cached_media(
                        chat_id=message.from_user.id,
                            file_id=file_id,  # Sending the file retrieved from the link
                            caption=caption,
                            protect_content=protect,
                            reply_markup=InlineKeyboardMarkup([
                            [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
                            [InlineKeyboardButton('💳 Donate', callback_data='donation')]
                            ])
                        )
                        files_sent.append(msg)
#                        logger.info("File ID %s successfully sent to user", unique_link)
                    else:
                        logger.error("File not found for link: %s", unique_link)

                else:
                    logger.error("File metadata not found for link: %s", unique_link)


            except FloodWait as e:
#                logger.warning(f"FloodWait of {e.x} seconds while sending file.")
                await asyncio.sleep(e.value)
                continue

            except Exception as e:
                logger.warning("Error sending file: %s", str(e))
                continue

            await asyncio.sleep(1)  # Prevent rate-limiting

        # Remove the initial status message
        await sts.delete()

        # Optional cleanup after some time
#        logger.info("Cleaning up after sending files.")
        cleanup_msg = await client.send_message(
            chat_id=message.from_user.id,
            text = script.DELETEMSG,
            protect_content=True
        )
        await asyncio.sleep(DLTTM)  # Adjust duration as needed

        for msg in files_sent:
            try:
                await msg.delete()
#                logger.info("Deleted message for file ID: %s", msg.message_id)
            except Exception as e:
                logger.warning("Error deleting message: %s", str(e))

        await cleanup_msg.edit_text("<b>Your All Files/Videos have been successfully deleted!</b>")
#        logger.info("Batch processing completed for Batch ID: %s", batch_id)

    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        if str(message.from_user.id) != str(userid):
            await m.delete()
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )
        is_valid = await check_token(client, userid, token)
        if is_valid == True:
            await m.delete()
            n = await message.reply_text(
                text=f"<b>Hey {message.from_user.mention}, You are successfully verified !\nNow you have unlimited access for all movies till today midnight.\nआपको मिला आज का प्रीमियम।\nआप आज मध्य रात्रि तक सभी सेवाओं का मुफ्त लाभ उठा सकते हैं।🤩</b>",
                protect_content=True
            )
            
            await verify_user(client, userid, token)
            await asyncio.sleep(300)
            await n.delete()
        else:
            await m.delete()
            return await message.reply_text(
                text="<b>Invalid link or Expired link !</b>",
                protect_content=True
            )

        
    if data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        userid = message.from_user.id if message.from_user else None
        settings = await get_settings(chat_id)
        #g = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}")
        await m.delete()
        k = await client.send_message(chat_id=message.from_user.id,text=f"<b>Get All Files in a Single Click!!!\n\n📂 ʟɪɴᴋ ➠ : {g}</i></b>", reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)
                    ], [
                        InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')
                    ]
                ]
            )
        )
        await asyncio.sleep(120)
        await k.edit("<b>Your message is successfully deleted!!!</b>")
        return

    
    elif data.startswith("all"):
#        logger.info("Processing 'all' command.")
        await m.delete()
        files = temp.GETALL.get(file_id)
        if not files:
#            logger.warning("No such file exists for the given file_id.")
            return await message.reply('<b><i>No such file exist.</b></i>')
        
#        logger.info(f"Found {len(files)} files associated with file_id: {file_id}.")
        filesarr = []
    
    # Check verification status first, outside the loop
        if VERIFY:
            is_verified = await check_verification(client, message.from_user.id)
            if not is_verified:
                btn = [[
                    InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                ],[
                    InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
                ]]
                await message.reply_text(
                    text="<b>You are not verified!\nKindly verify to continue!</b>",
                    protect_content=True,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
#                logger.info(f"User {message.from_user.id} is not verified. Verification prompt sent.")
                return  # Stop further execution if user is not verified
    
    # Process files if verified
        for file in files:
            file_id = file["file_id"]
#            logger.info(f"Processing file with file_id: {file_id}.")
            
#            logger.info(f"Awaiting file details.")
            files_ = await get_file_details1(file_id)
#            logger.debug(f"File details retrieved: {files_}.")
            
            files1 = files_
            title = clean_file_name(files1['file_name'])
            size = get_size(files1['file_size'])
            f_caption = files1['caption']
            
#            logger.info(f"File details: title={title}, size={size}.")
            
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title,
                        file_size=size,
                        file_caption=f_caption
                    )
#                    logger.info("Custom caption applied successfully.")
                except Exception as e:
                    logger.exception("Error applying custom caption.")
                    f_caption = f_caption or title
            
            if not f_caption:
                f_caption = title
#                logger.info("Fallback caption applied.")

            if STREAM_MODE:
                button = [
                    [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
                    [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
                ]
#                logger.info("Stream mode enabled. Buttons configured.")
            else:
                button = [
                    [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
                    [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
                ]
#                logger.info("Default mode enabled. Buttons configured.")
            
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'filep' else False,
                reply_markup=InlineKeyboardMarkup(button)
            )
#            logger.info(f"File sent to user: {message.from_user.id}, message_id: {msg.id}.")
            filesarr.append(msg)
        
#        logger.info("All files sent. Sending confirmation message.")
        k = await client.send_message(chat_id=message.from_user.id, text = script.DELETEMSG, protect_content=True)
        await asyncio.sleep(DLTTM)
        
#        logger.info("Deleting sent files after delay.")
        for x in filesarr:
            await x.delete()
#            logger.info(f"Deleted message: {x.id}.")
        
        await k.edit_text("<b>Your All Files/Videos is successfully deleted!!!</b>")
#        logger.info("Confirmation message edited to indicate deletion.")
        return
    
    elif data.split("-", 1)[0] == "DSTORE":
        await m.delete()
        sts = await message.reply("Please wait")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
        diff = int(l_msg_id) - int(f_msg_id)
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption=BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            await asyncio.sleep(1) 
        return await sts.delete()

    files_ = await get_file_details(file_id)
    if VERIFY:
        is_verified = await check_verification(client, message.from_user.id)
        if not is_verified:
            btn = [[
                InlineKeyboardButton("Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
            ], [
                InlineKeyboardButton("How To Open Link & Verify", url=VERIFY_TUTORIAL)
            ]]
            await m.delete()
            await message.reply_text(
                text="<b>You are not verified!\nKindly verify to continue!</b>",
                protect_content=True,
                reply_markup=InlineKeyboardMarkup(btn)
            )
#            logger.info(f"User {message.from_user.id} is not verified. Verification prompt sent.")
            return  # Stop execution if the user is not verified

    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
            )
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = clean_file_name(file.file_name)
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name='' if title is None else title,
                        file_size='' if size is None else size,
                        file_caption=''
                    )
                except:
                    return
            await msg.edit_caption(f_caption)
            btn = [[
                InlineKeyboardButton("Get File Again", callback_data=f'del#{file_id}')
            ]]
            k = await msg.reply(script.DELETEMSG ,quote=True, protect_content=True)
            await asyncio.sleep(DLTTM)
            await msg.delete()
            await k.edit_text("<b>Your File/Video is successfully deleted!!!\n\n</b>") #,reply_markup=InlineKeyboardMarkup(btn))
            return
        except:
            pass
        return await message.reply('No such file exist.')
         #   return
     #   except:
      #      pass
       # return await message.reply('𝗡𝗼 𝘀𝘂𝗰𝗵 𝗳𝗶𝗹𝗲 𝗲𝘅𝗶𝘀𝘁.')
    files = files_[0]
    title = clean_file_name(files.file_name)
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(
                file_name='' if title is None else title,
                file_size='' if size is None else size,
                file_caption='' if f_caption is None else f_caption
            )
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:    
        f_caption = f"{files.file_name}"

    button = [
        [InlineKeyboardButton("Join Our Offer Zone 🤑", url=OFR_CNL)],
        [InlineKeyboardButton('💳 Dᴏɴᴀᴛᴇ', callback_data='donation')]
    ]
#    logger.info("Default mode enabled. Buttons configured.")

    await m.delete()
    msg = await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
        reply_markup=InlineKeyboardMarkup(button)
        )
    btn = [[
        InlineKeyboardButton("Get File Again", callback_data=f'del#{file_id}')
    ]]
    k = await msg.reply(script.DELETEMSG ,quote=True, protect_content=True)
    await asyncio.sleep(DLTTM)
    await msg.delete()
    await k.edit_text("<b>Your File/Video is successfully deleted!!!\n\nClick below button to get your deleted file 👇</b>") #,reply_markup=InlineKeyboardMarkup(btn))
    return
    

                     

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("𝗨𝗻𝗲𝘅𝗽𝗲𝗰𝘁𝗲𝗱 𝘁𝘆𝗽𝗲 𝗼𝗳 𝗖𝗛𝗔𝗡𝗡𝗘𝗟𝗦")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('TelegramBot.log')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("𝗣𝗿𝗼𝗰𝗲𝘀𝘀𝗶𝗻𝗴...⏳", quote=True)
    else:
        await message.reply('𝗥𝗲𝗽𝗹𝘆 𝘁𝗼 𝗳𝗶𝗹𝗲 𝘄𝗶𝘁𝗵 /delete 𝘄𝗵𝗶𝗰𝗵 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗱𝗲𝗹𝗲𝘁𝗲', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('𝗧𝗵𝗶𝘀 𝗶𝘀 𝗻𝗼𝘁 𝘀𝘂𝗽𝗽𝗼𝗿𝘁𝗲𝗱 𝗳𝗶𝗹𝗲 𝗳𝗼𝗿𝗺𝗮𝘁')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
        else:
            # files indexed before https://github.com/LazyDeveloperr/lazyPrincess/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('𝗙𝗶𝗹𝗲 𝗶𝘀 𝘀𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗱𝗲𝗹𝗲𝘁𝗲𝗱 𝗳𝗿𝗼𝗺 𝗱𝗮𝘁𝗮𝗯𝗮𝘀𝗲')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        '𝗧𝗵𝗶𝘀 𝘄𝗶𝗹𝗹 𝗱𝗲𝗹𝗲𝘁𝗲 𝗮𝗹𝗹 𝗶𝗻𝗱𝗲𝘅𝗲𝗱 𝗳𝗶𝗹𝗲𝘀.\n 𝗗𝗼 𝘆𝗼𝘂 𝘄𝗮𝗻𝘁 𝘁𝗼 𝗰𝗼𝗻𝘁𝗶𝗻𝘂𝗲??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="YES", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer('♥️ Thank You Filmykeedha ♥️')
    await message.message.edit('𝗦𝘂𝗰𝗰𝗲𝘀𝗳𝘂𝗹𝗹𝘆 𝗗𝗲𝗹𝗲𝘁𝗲𝗱 𝗔𝗹𝗹 𝗧𝗵𝗲 𝗜𝗻𝗱𝗲𝘅𝗲𝗱 𝗙𝗶𝗹𝗲𝘀.')


@Client.on_message(filters.command('settings') & filters.user(ADMINS))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗻𝗼𝗻𝘆𝗺𝗼𝘂𝘀 𝗮𝗱𝗺𝗶𝗻. 𝗨𝘀𝗲 /connect {message.chat.id} 𝗶𝗻 𝗣𝗠")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗜'𝗺 𝗽𝗿𝗲𝘀𝗲𝗻𝘁 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽!!", quote=True)
                return
        else:
            await message.reply_text("𝗜'𝗺 𝗻𝗼𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝘁𝗼 𝗮𝗻𝘆 𝗴𝗿𝗼𝘂𝗽𝘀!", quote=True)
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
        return

    settings = await get_settings(grp_id)

    if settings is not None:
        buttons = [
            [
                InlineKeyboardButton(
                    'Filter Button',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    'Single' if settings["button"] else 'Double',
                    callback_data=f'setgs#button#{settings["button"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Bot PM',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["botpm"] else '❌ No',
                    callback_data=f'setgs#botpm#{settings["botpm"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'File Secure',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["file_secure"] else '❌ No',
                    callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'IMDB',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["imdb"] else '❌ No',
                    callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Spell Check',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["spell_check"] else '❌ No',
                    callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}',
                ),
            ],
            [
                InlineKeyboardButton(
                    'Welcome',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
                InlineKeyboardButton(
                    '✅ Yes' if settings["welcome"] else '❌ No',
                    callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}',
                ),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_text(
            text=f"<b>𝗖𝗵𝗮𝗻𝗴𝗲 𝗬𝗼𝘂𝗿 𝗦𝗲𝘁𝘁𝗶𝗻𝗴𝘀 𝗳𝗼𝗿 {title} 𝗔𝘀 𝗬𝗼𝘂𝗿 𝗪𝗶𝘀𝗵 ⚙</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )

@Client.on_message(filters.command("donate"))
async def plans_cmd_handler(client, message): 
    btn = [            
        [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(btn)
    await message.reply_photo(
        photo=PAYMENT_QR,
        caption=PAYMENT_TEXT,
        reply_markup=reply_markup
    )

@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("Checking template")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"𝗬𝗼𝘂 𝗮𝗿𝗲 𝗮𝗻𝗼𝗻𝘆𝗺𝗼𝘂𝘀 𝗮𝗱𝗺𝗶𝗻. 𝗨𝘀𝗲 /connect {message.chat.id} 𝗶𝗻 𝗣𝗠")
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("𝗠𝗮𝗸𝗲 𝘀𝘂𝗿𝗲 𝗜'𝗺 𝗽𝗿𝗲𝘀𝗲𝗻𝘁 𝗶𝗻 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽!!", quote=True)
                return
        else:
            await message.reply_text("𝗜'𝗺 𝗻𝗼𝘁 𝗰𝗼𝗻𝗻𝗲𝗰𝘁𝗲𝗱 𝘁𝗼 𝗮𝗻𝘆 𝗴𝗿𝗼𝘂𝗽𝘀!", quote=True)
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
        return

    if len(message.command) < 2:
        return await sts.edit("No Input!!")
    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗰𝗵𝗮𝗻𝗴𝗲𝗱 𝘁𝗲𝗺𝗽𝗹𝗮𝘁𝗲 𝗳𝗼𝗿 {title}  𝘁𝗼\n\n{template}")
@Client.on_callback_query(filters.regex("donation"))
async def donation_callback(client, callback_query):
    await callback_query.answer()
    buttons = [
        [InlineKeyboardButton("ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾", url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton("⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️", callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.reply_photo(
        photo=PAYMENT_QR,
        caption=PAYMENT_TEXT,
        reply_markup=reply_markup
    )



import re
import uuid
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media
from utils import get_size
import logging

logger = logging.getLogger(__name__)

# Temporary RAM cache to hold database queries pending admin confirmation
PURGE_CACHE = {}

def parse_size_filter(size_str):
    """Parses formats like >500MB or <1.5GB into operators and bytes."""
    match = re.match(r"([<>])\s*([\d\.]+)\s*([KMG]?B)", size_str.upper())
    if not match:
        return None, None
    op, val, unit = match.groups()
    val = float(val)
    multiplier = 1
    if unit == 'KB': multiplier = 1024
    elif unit == 'MB': multiplier = 1024**2
    elif unit == 'GB': multiplier = 1024**3
    return op, int(val * multiplier)

@Client.on_message(filters.command('scrub') & filters.user(ADMINS))
async def scrub_database(client, message):
    """
    Usage: /scrub [pattern] [size_filter]
    Examples: 
    /scrub *avengers* /scrub avatar* >1GB
    /scrub *movie <500MB
    """
    if len(message.command) < 2:
        return await message.reply_text(
            "<b>⚠️ Invalid Format.</b>\n\n"
            "<b>Usage:</b> <code>/scrub [pattern] [size]</code>\n"
            "<b>Example:</b> <code>/scrub *spider-man* >1GB</code>\n"
            "<b>Example:</b> <code>/scrub batman* &lt;500MB</code>"
        )

    # 1. Parse the command arguments
    args = message.text.split(maxsplit=1)
    
    # Extract size filter if present (e.g., >100MB or <2GB)
    size_op, size_bytes = None, None
    size_match = re.search(r"([<>]\s*[\d\.]+\s*[KMG]?B)", args, re.IGNORECASE)
    
    if size_match:
        size_str = size_match.group(1)
        size_op, size_bytes = parse_size_filter(size_str)
        # Remove the size filter from the pattern string
        args = args.replace(size_str, "").strip()

    pattern = args

    # 2. Convert the * wildcard into a MongoDB-compatible regex pattern
    # Escape special characters first, then replace the escaped \* with .*
    safe_pattern = re.escape(pattern).replace(r"\*", ".*")
    regex_pattern = f"^{safe_pattern}$"

    # 3. Build the MongoDB Query Dictionary
    db_query = {'file_name': {'$regex': regex_pattern, '$options': 'i'}}
    
    if size_op and size_bytes:
        mongo_op = '$gt' if size_op == '>' else '$lt'
        db_query['file_size'] = {mongo_op: size_bytes}

    msg = await message.reply_text("<b>🔍 Scanning database... please wait.</b>")

    try:
        # 4. Use Aggregation to get stats without crashing RAM (OOM safe!)
        pipeline = [
            {"$match": db_query},
            {"$group": {
                "_id": None,
                "total_count": {"$sum": 1},
                "max_size": {"$max": "$file_size"},
                "min_size": {"$min": "$file_size"}
            }}
        ]
        
        stats_cursor = Media.collection.aggregate(pipeline)
        stats = await stats_cursor.to_list(length=1)

        if not stats:
            return await msg.edit_text(f"<b>❌ No files found matching:</b> <code>{pattern}</code>")

        stats = stats
        total_count = stats.get("total_count", 0)
        max_size = get_size(stats.get("max_size", 0))
        min_size = get_size(stats.get("min_size", 0))

        # 5. Fetch up to 5 sample file names for the admin to review
        samples_cursor = Media.collection.find(db_query).limit(5)
        sample_docs = await samples_cursor.to_list(length=5)
        sample_names = "\n".join([f" ├ <code>{doc['file_name']}</code>" for doc in sample_docs])

        # 6. Generate a unique cache key and store the query
        query_id = str(uuid.uuid4())[:8]
        PURGE_CACHE[query_id] = db_query

        # 7. Build the confirmation message
        text = (
            f"<b>⚠️ DATABASE PURGE WARNING</b>\n\n"
            f"<b>Pattern:</b> <code>{pattern}</code>\n"
            f"<b>Size Filter:</b> <code>{'None' if not size_op else f'{size_op} {get_size(size_bytes)}'}</code>\n\n"
            f"<b>📊 SCAN RESULTS:</b>\n"
            f" ├ <b>Total Files:</b> {total_count}\n"
            f" ├ <b>Min Size:</b> {min_size}\n"
            f" └ <b>Max Size:</b> {max_size}\n\n"
            f"<b>📂 SAMPLES:</b>\n{sample_names}\n\n"
            f"<b>Are you absolutely sure you want to delete these {total_count} files? This cannot be undone.</b>"
        )

        buttons = [
            [
                InlineKeyboardButton("🗑️ YES, DELETE ALL", callback_data=f"purge_yes_{query_id}"),
                InlineKeyboardButton("❌ CANCEL", callback_data=f"purge_no_{query_id}")
            ]
        ]

        await msg.edit_text(text, reply_markup=InlineKeyboardMarkup(buttons))

    except Exception as e:
        logger.exception("Error during database scrub scan.")
        await msg.edit_text(f"<b>❌ An error occurred during the scan:</b> {e}")


@Client.on_callback_query(filters.regex(r"^purge_(yes|no)_"))
async def handle_purge_confirmation(client, query):
    action, query_id = query.data.split("_"), query.data.split("_")

    # Ensure only authorized admins can click this button
    if str(query.from_user.id) not in ADMINS:
        return await query.answer("This button is strictly for admins.", show_alert=True)

    if action == "no":
        # Clean up cache and cancel
        PURGE_CACHE.pop(query_id, None)
        return await query.message.edit_text("<b>✅ Purge operation cancelled. No files were deleted.</b>")

    if action == "yes":
        db_query = PURGE_CACHE.pop(query_id, None)
        
        if not db_query:
            return await query.answer("This purge request has expired or was already executed.", show_alert=True)

        await query.answer("Deleting files... this might take a moment.", show_alert=True)
        
        try:
            # Execute the mass deletion natively on the MongoDB engine
            result = await Media.collection.delete_many(db_query)
            deleted_count = result.deleted_count
            
            await query.message.edit_text(
                f"<b>🗑️ PURGE COMPLETE</b>\n\n"
                f"<b>Successfully deleted:</b> {deleted_count} files from the database."
            )
            
        except Exception as e:
            logger.exception("Error executing mass deletion.")
            await query.message.edit_text(f"<b>❌ An error occurred while deleting files:</b> {e}")
