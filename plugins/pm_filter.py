import asyncio
import re
import ast
import math
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from Script import script
import pyrogram
from info import *
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from info import ADMINS, AUTH_CHANNEL, AUTH_USERS, AUTH_GROUPS, P_TTI_SHOW_OFF, IMDB, \
    SINGLE_BUTTON, SPELL_CHECK_REPLY, IMDB_TEMPLATE
from variables import CUSTOM_FILE_CAPTION, VERIFY
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong, PeerIdInvalid
from info import ADMINS, LOG_CHANNEL, SUPPORT_CHAT, MELCOW_NEW_USERS, SUPPORT_CHAT_ID
from database.users_chats_db import db
from database.ia_filterdb import Media
from utils import get_size, temp, get_settings, clean_file_name
from Script import script
from pyrogram.errors import ChatAdminRequired
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import (
    del_all,
    find_filter,
    get_filters,
)
from variables import CUSTOM_FILE_CAPTION, VERIFY, VERIFY_TUTORIAL, DLTTM, AUTH_CHANNELS

import logging
from pyrogram.enums import ParseMode
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

#BUTTONS = {}
#SPELL_CHECK = {}
BUTTON = {}
BUTTONS = {}
FRESH = {}
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}
SPELL_CHECK = {}
AUTO_DELETE = 'False'
#VERIFY = 'False'
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
@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    chat_id = message.chat.id
    user = message.from_user  # Get the user object
    user_id = user.id if user else 0  # Fallback to 0 if no user ID is available

    # Debugging: Log both the chat_id and SUPPORT_CHAT_ID
#    logger.info(f"Received message in chat {chat_id} from user {user_id}. SUPPORT_CHAT_ID: {SUPPORT_CHAT_ID}")
#    logger.info(f"Type of chat_id: {type(chat_id)}, Type of SUPPORT_CHAT_ID: {type(SUPPORT_CHAT_ID)}")

    # Check if the user is an anonymous admin
    if user_id == 0:
 #       logger.info("User is an anonymous admin. Request will not be processed.")
        await message.reply_text(
            "<b>You are an anonymous admin. I can't process your request. "
            "Please disable 'Remain Anonymous' in admin rights to continue.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    try:
        # Check if this is the support chat
        if chat_id == SUPPORT_CHAT_ID:
  #          logger.info(f"User is in the support chat (chat_id: {chat_id}). Sending search group link.")
            # Inline button to join the search group
            inline_button = InlineKeyboardButton("Join Search Group", url="https://t.me/Filmykeedha/306")
            reply_markup = InlineKeyboardMarkup([[inline_button]])

            T = await message.reply_text(
                "<b>This is not the search group. Please join the search group by tapping the button below:</b>",
                reply_markup=reply_markup,  # Add the inline button
                disable_web_page_preview=True
            )
            await asyncio.sleep(300)
            await T.delete() # await delete(T)
            return

        # If not in the support chat, execute manual and auto-filter logic
        #logger.info(f"User is not in the support chat (chat_id: {chat_id}). Executing filters.")
        L = await message.reply_text("<b>This Group Ban Anytime so Join Another Private Group.</b><i>👉🏻Link(1) : https://t.me/+5pa88NB3YAhiNDQ1 </i>\n<i>👉🏻Link(2) : https://t.me/+13JZ5BMiiSM4ZmE1 </i>\n\n Wait 10 second Bot is finding Movie", disable_web_page_preview=True)
        await manual_filters(client, message)
        await auto_filter(client, message)
        await asyncio.sleep(60)
        await L.delete() #await delete (L)
    except FloodWait as e:
        # Handle FloodWait exception
        logger.error(f"FloodWait exception: {e.value} seconds")
        await asyncio.sleep(e.value)
        await message.reply_text(
            f"<b>FloodWait detected. Please wait {e.value} seconds before trying again.</b>",
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        # Handle generic exceptions
        logger.error(f"Unexpected exception: {str(e)}")
        await message.reply_text(
            f"<b>An unexpected error occurred. Please try again later.\n\nDetails: {str(e)}</b>",
            parse_mode=ParseMode.HTML
            )

def get_butto1ns():
    buttons = [
        [
            InlineKeyboardButton("🔍 Search Group", url="https://t.me/Filmykeedha/306"),
            InlineKeyboardButton("📢 Offer Channel", url="https://t.me/+4dWp2gDjwC43YmJl"),
        ],
        [
            InlineKeyboardButton("💰 Donate", callback_data="donation2"),
            InlineKeyboardButton("🏠 Main Channel", url="https://t.me/+zhtB8CYxfxFhOTM1"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)

"""
@Client.on_message(filters.private & filters.text & filters.incoming)
async def private_message_handler(client, message):
    if message.text.startswith("/"):  # Ignore commands
        return

    p = await message.reply_text(
        "<b>🚫 I am not working here; I only work in groups.</b>\n\n"
        "<b>👉 Explore the options below:</b>",
        reply_markup=get_butto1ns()  # Replace `get_buttons` with your actual function
    )
    await asyncio.sleep(60)
    await p.delete()

"""
@Client.on_callback_query(filters.regex("donation2"))
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

@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer("This Message is not for you dear. Don't worry you can send new one !", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
           # InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])
        btn.insert(0, [
             InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")

        ])
        
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
           # InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])
        btn.insert(0, [
             InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")

        ])

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⬅𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⬅𝐁𝐀𝐂𝐊", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("This Message is not for you dear. Don't worry you can send new one !", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            k = await query.message.edit(' 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐮𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 ! \n𝐰𝐞 𝐚𝐫𝐞 𝐫𝐞𝐚𝐥𝐥𝐲 𝐬𝐨𝐫𝐫𝐲 𝐟𝐨𝐫 𝐢𝐧𝐜𝐨𝐧𝐯𝐞𝐧𝐢𝐞𝐧𝐜𝐞 !\n\n 𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐭 𝐭𝐡𝐢𝐬 𝐌𝐨𝐯𝐢𝐞 𝐨𝐫 𝐖𝐞𝐛𝐬𝐞𝐫𝐢𝐞𝐬 𝐧𝐚𝐦𝐞 𝐢𝐧 #Request 𝐓𝐨𝐩𝐢𝐜 𝐨𝐫 𝐬𝐞𝐧𝐭 𝐮𝐬𝐢𝐧𝐠 "#𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞 & 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 𝐘𝐞𝐚𝐫.\n example: <code> #Request Mirzapur Season 1 2018 </code>\n 𝐨𝐮𝐫 𝐠𝐫𝐞𝐚𝐭 𝐚𝐝𝐦𝐢𝐧𝐬 𝐰𝐢𝐥𝐥 𝐮𝐩𝐥𝐨𝐚𝐝 𝐢𝐭 𝐚𝐬 𝐬𝐨𝐨𝐧 𝐚𝐬 𝐩𝐨𝐬𝐬𝐢𝐛𝐥𝐞 !')
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!!", quote=True)
                    return await query.answer('♥️ Love @Filmykeedha ♥️')
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nमैं आपके किसी भी ग्रुप से कनेक्ट या जुड़ी नही हूं।\nCheck /connections or connect to any groups",
                    quote=True
                )
                return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞 @Filmykeedha ♥️')

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be Group Owner or an Auth User to do that!\nऐसा करने के लिए आपको समूह का owner या admin होना चाहिए!", show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("𝐓𝐡𝐚𝐭'𝐬 𝐧𝐨𝐭 𝐟𝐨𝐫 𝐲𝐨𝐮 𝐬𝐨𝐧𝐚!\n यह तुम्हारे लिए नहीं है!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])

        await query.message.edit_text(
            f"Group Name : **{title}**\nGroup ID : `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            await query.message.edit_text(
                f"Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('Some error occurred!!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            await query.message.edit_text(
                f"Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                "Successfully deleted connection"
            )
        else:
            await query.message.edit_text(
                f"Some error occurred!!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "There are no active connections!! Connect to some groups first.",
            )
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
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
            await query.message.edit_text(
                "Your connected group details ;\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
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

        try:
            if settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                msg = await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False 
                )
             #   await query.answer('𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦', show_alert=True)


                await query.answer('𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦 \nCheck @Rashmika_mandanana_bot', show_alert=True)
             #   logger.info("show alert")
                
                k = await msg.reply(script.DELETEMSG ,quote=True, protect_content=True)
                await asyncio.sleep(DLTTM)
                await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>") #,reply_markup=InlineKeyboardMarkup(btn))
                await msg.delete()
                
        
        except UserIsBlocked:
            await query.answer('𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐭𝐡𝐞 𝐁𝐨𝐭!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = BUTTON0.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
        
    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
            return
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(f"Hey {query.from_user.first_name}, All files on this page has been sent successfully to your PM !", show_alert=True)
            
    
    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)
        
        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
            return 
           # if settings['is_shortlink'] and not await db.has_premium_access(query.from_user.id):
            #    if SHORTLINK_MODE == True:
             #       await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles1_{key}")
                    
             #   else:
             #       await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
           # elif settings['is_shortlink'] and await db.has_premium_access(query.from_user.id):
           #     await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
           #     return 
            #else:
             #   await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
                
            
                
        except UserIsBlocked:
            await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            #await send_error_log(client, "1497", e)
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")
            #await send_error_log(client, "1500", e)
            
    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("𝐈𝐬𝐤𝐨 𝐉𝐨𝐢𝐧 𝐊𝐚𝐫 𝐏𝐡𝐥𝐞 ✋🏻", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton('➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton('🧞‍♀️ 𝗦𝗲𝗮𝗿𝗰𝗵 🧐', switch_inline_query_current_chat=''),
            InlineKeyboardButton('✪𝙂𝙍𝙊𝙐𝙋✪', url='https://t.me/filmykeedha_search')
        ], [
            InlineKeyboardButton('🙆🏻 𝗛𝗲𝗹𝗽 🦾', callback_data='help'),
            InlineKeyboardButton('♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.START_TXT.format(query.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    elif query.data == "help":
        buttons = [[
            InlineKeyboardButton('𝗠𝗮𝗻𝘂𝗮𝗹 𝗙𝗶𝗹𝘁𝗲𝗿', callback_data='manuelfilter'),
            InlineKeyboardButton('𝗔𝘂𝘁𝗼 𝗙𝗶𝗹𝘁𝗲𝗿', callback_data='autofilter')
        ], [
            InlineKeyboardButton('𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻', callback_data='coct'),
            InlineKeyboardButton('𝗘𝘅𝘁𝗿𝗮 𝗠𝗼𝗱𝘀', callback_data='extra')
        ], [
            InlineKeyboardButton('🏠 𝗛𝗼𝗺𝗲', callback_data='start'),
            InlineKeyboardButton('🦠 𝗦𝘁𝗮𝘁𝘂𝘀', callback_data='stats')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "about":
        buttons = [[
            InlineKeyboardButton('⁠✪𝙂𝙍𝙊𝙐𝙋✪ ', url='https://t.me/filmykeedha_search'),
            InlineKeyboardButton('♥️ 𝗦𝗼𝘂𝗿𝗰𝗲', callback_data='source')
        ], [
            InlineKeyboardButton('🏠 𝗛𝗼𝗺𝗲', callback_data='start'),
            InlineKeyboardButton('🔐 𝗖𝗹𝗼𝘀𝗲', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "source":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='about')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "manuelfilter":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('◉⁠𝐁𝐮𝐭𝐭𝐨𝐧𝐬', callback_data='button')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "button":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='manuelfilter')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "autofilter":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "coct":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "extra":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('♚ 𝗔𝗱𝗺𝗶𝗻', callback_data='admin')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "admin":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='extra')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "stats":
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('↺', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDb DataBase")
        buttons = [[
            InlineKeyboardButton('⬅𝐁𝐀𝐂𝐊', callback_data='help'),
            InlineKeyboardButton('↺', callback_data='rfrsh')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit("Your Active Connection Has Been Changed. Go To /settings.")
            return await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('Single' if settings["button"] else 'Double',
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Bot PM', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["botpm"] else '❌ No',
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('File Secure',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["file_secure"] else '❌ No',
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDB', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["imdb"] else '❌ No',
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["spell_check"] else '❌ No',
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ Yes' if settings["welcome"] else '❌ No',
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer('♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️')
    
"""

async def auto_filter(client, msg, spoll=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"): return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
                        # 1. Flatten hidden carriage returns and vertical line breaks cleanly
            flattened = message.text.replace("\n", " ").replace("\r", " ")
            logger.info(f"Processed query in auto_filter: {flattened}")

            
            # 2. Extract only English characters, numbers, and white spaces
            alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
            logger.info(f"Processed query in auto_filter: {alphanumeric_only}")
            # 3. Compress double spaces left behind by stripped special characters
            search = " ".join(alphanumeric_only.split())
            logger.info(f"Processed query in auto_filter: {search}")
            if not search or len(search) < 3:
                
                logger.warning(f"Aborting search. Cleaned query '{search}' is too short or empty.")
                try:
                    await message.reply_text(
                        "<b>⚠️ Invalid Search Query!</b>\n\n"
                        "• Please type at least <b>3 characters</b> of the movie/series name.\n"
                        "• Avoid sending only special characters or symbols (like <code>*, !, ?, @, #</code>).",
                        parse_mode=ParseMode.HTML
                    )
                except Exception as reply_err:
                    logger.error(f"Failed to send short-query warning message: {reply_err}")
                return
                            
           # search = " ".join(message.text.replace("\n", " ").replace("\r", " ").split())
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            #search = message.text
            #files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_chok(client, msg)
                else:
                    return
        else:
            return
    else:
        settings = await get_settings(msg.message.chat.id)
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    req = message.from_user.id if message.from_user else 0
    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id
    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}", callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
            #InlineKeyboardButton("ʟanguage", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])
        btn.insert(0, [
             InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")

        ])
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{clean_file_name(file.file_name)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            
        
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}") #,
           # InlineKeyboardButton("ʟᴀɴɢᴜᴀɢᴇs", callback_data=f"languages#{key}"),
            #InlineKeyboardButton("ʏᴇᴀʀs", callback_data=f"years#{key}")
        ])
        btn.insert(0, [
             InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")

        ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"⁠✧✧ 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="(⁠✧ 1/1 ✧", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"𝐒𝐚𝐡𝐞𝐛! 𝐌𝐮𝐣𝐡𝐞 𝐊𝐮𝐜𝐡 𝐌𝐢𝐥𝐚 𝐇𝐚𝐢 {search}\n\n"
    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024],
                                      reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    if spoll:
        await msg.message.delete()

import asyncio
import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fuzzywuzzy import fuzz  # Assuming fuzzywuzzy is used for spell-checking

# Define required functions like get_poster, send_error_log, and others
import logging
async def advantage_spell_chok(client, msg):

    mv_id = msg.id
    user_id = msg.from_user.id if msg.from_user else 0
    req_user = await client.get_users(user_id)
    logger.info(f"Received spell check request from user {req_user.username or user_id} (User ID: {user_id}).")

   # query = re.sub(
   #     r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
   #     "", msg.text, flags=re.IGNORECASE
   # ).strip()
    # 1. Strip structural keywords cleanly using regex rules
        # 1. Clean out the bot keyword commands using your existing filter layout
    cleaned_text = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE
    ).strip()
    logger.info(f"Processed query in adv spell check: {cleaned_text}")

    # 2. ✅ THE FIX: Drop all lines breaks, turn symbols into spaces, and compress double spaces
    flattened = cleaned_text.replace("\n", " ").replace("\r", " ")
    logger.info(f"Processed query in adv spell check: {flattened}")
    alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
    logger.info(f"Processed query in adv spell check: {alphanumeric_only}")
    query = " ".join(alphanumeric_only.split())

    if not query:
        return

    logger.info(f"Processed query in adv spell check: {query}")

    try:
        # Fetch movie suggestions
#        logger.info(f"check by get poster {query}")
        movies = await get_poster(query, bulk=True)
        if not movies:
#            logger.warning(f"No movies found for query: {query}")
            search_query = query.replace(" ", "+")
            buttons = [
                [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
                [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
            ]
            await msg.reply(
                f"I couldn't find any movies related to **{query}**. Try searching on Google or in the request group.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return
    except Exception as e:
        logger.error(f"Error fetching movies for query '{query}': {e}")
        search_query = query.replace(" ", "+")
        buttons = [
            [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            "An error occurred while processing your request. Please try again or check the request group.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    # Ensure movies have valid titles and years
    movielist = [
        movie.get('title') for movie in movies if movie.get('title')
    ] + [
        f"{movie.get('title')} {movie.get('year')}" for movie in movies if movie.get('title') and movie.get('year')
    ]

    if not movielist:
#        logger.warning(f"No valid movie titles found for query '{query}'.")
        search_query = query.replace(" ", "+")
        buttons = [
            [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            f"No valid movie titles found for **{query}**. Try searching on Google or in the request group.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

#    logger.info(f"Found {len(movielist)} movies for query '{query}'.")
    SPELL_CHECK[mv_id] = movielist

    try:
        matched_movie = None
        for title in movielist:
            ratio = fuzz.ratio(query.lower(), title.lower())
            logger.debug(f"Matching '{query}' with '{title}', Ratio: {ratio}")
            if ratio > 60:  # Consider adjusting the threshold
                matched_movie = title
                break

        if matched_movie:
#            logger.info(f"Spell check found a match: {matched_movie}")
            await auto_filter(client, msg, matched_movie)
        else:
#            logger.info(f"No close matches found for query '{query}'.")
            search_query = query.replace(" ", "+")
            buttons = [
                [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
                [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
            ]
            await msg.reply(
                f"<b>No close matches found for **{query}**. Try searching on Google or request in the group.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    except Exception as e:
        logger.error(f"Error during spell check for query '{query}': {e}")

    try:
        buttons = [
            [InlineKeyboardButton(movie.strip(), callback_data=f"spolling#{user_id}#{idx}")]
            for idx, movie in enumerate(movielist)
        ]
        buttons.append([InlineKeyboardButton("Close", callback_data=f'spolling#{user_id}#close_spellcheck')])
        t = await msg.reply(
            f"<b>Here are some suggestions for **{query}**:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        await asyncio.sleep(120)
        await t.delete()
#        logger.info(f"Displayed suggestions for query '{query}'.")
    except Exception as e:
        logger.error(f"Error displaying movie suggestions for query '{query}': {e}")

"""

async def auto_filter(client, msg, spoll=False, webapp=False):
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)

        if message.text.startswith("/"):
            return

        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

        if len(message.text) < 100:
            # 1. Flatten hidden carriage returns and vertical line breaks cleanly
            flattened = message.text.replace("\n", " ").replace("\r", " ")
            logger.info(f"Processed query in auto_filter: {flattened}")

            # 2. Extract only English characters, numbers, and white spaces
            alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
            logger.info(f"Processed query in auto_filter: {alphanumeric_only}")

            # 3. Compress double spaces left behind by stripped special characters
            search = " ".join(alphanumeric_only.split())
            logger.info(f"Processed query in auto_filter: {search}")

            if not search or len(search) < 3:
                logger.warning(f"Aborting search. Cleaned query '{search}' is too short or empty.")

                if webapp:
                    return {
                        "status": "too_short",
                        "query": search,
                        "files": [],
                        "total_results": 0,
                        "next_offset": "",
                        "suggestions": [],
                    }

                try:
                    await message.reply_text(
                        "<b>⚠️ Invalid Search Query!</b>\n\n"
                        "• Please type at least <b>3 characters</b> of the movie/series name.\n"
                        "• Avoid sending only special characters or symbols (like <code>*, !, ?, @, #</code>).",
                        parse_mode=ParseMode.HTML
                    )
                except Exception as reply_err:
                    logger.error(f"Failed to send short-query warning message: {reply_err}")
                return

            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)

            if not files:
                if settings["spell_check"]:
                    spell_result = await advantage_spell_chok(client, msg, webapp=webapp)
                    if webapp:
                        return spell_result
                    return
                else:
                    if webapp:
                        return {
                            "status": "not_found",
                            "query": search,
                            "files": [],
                            "total_results": 0,
                            "next_offset": "",
                            "suggestions": [],
                        }
                    return

        else:
            return


    else:
        if hasattr(msg, "message"):  # CallbackQuery
            settings = await get_settings(msg.message.chat.id)
            message = msg.message.reply_to_message
        else:                               # Normal Message (spell check)
            settings = await get_settings(msg.chat.id)
            message = msg
            search, files, offset, total_results = spoll

    pre = 'filep' if settings['file_secure'] else 'file'
    key = f"{message.chat.id}-{message.id}"
    req = message.from_user.id if message.from_user else 0

    if webapp:
        return {
            "status": "found",
            "query": search,
            "files": files,
            "offset": offset,
            "total_results": total_results,
            "next_offset": offset,
        }

    FRESH[key] = search
    temp.GETALL[key] = files
    temp.SHORT[message.from_user.id] = message.chat.id

    if settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}",
                    callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")
        ])
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{clean_file_name(file.file_name)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton("𝐒𝐞𝐧𝐝 𝐀𝐥𝐥", callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(f"Results Of👉🏻 {search} 👈🏻", callback_data=f"fsendfiles#{key}")
        ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [
                InlineKeyboardButton(
                    text=f"⁠✧✧ 1/{math.ceil(int(total_results) / 10)}",
                    callback_data="pages"
                ),
                InlineKeyboardButton(text="𝐍𝐄𝐗𝐓➡", callback_data=f"next_{req}_{key}_{offset}")
            ]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="(⁠✧ 1/1 ✧", callback_data="pages")]
        )

    imdb = await get_poster(search, file=(files[0]).file_name) if settings["imdb"] else None
    TEMPLATE = settings['template']

    if imdb:
        cap = TEMPLATE.format(
            query=search,
            title=imdb['title'],
            votes=imdb['votes'],
            aka=imdb["aka"],
            seasons=imdb["seasons"],
            box_office=imdb['box_office'],
            localized_title=imdb['localized_title'],
            kind=imdb['kind'],
            imdb_id=imdb["imdb_id"],
            cast=imdb["cast"],
            runtime=imdb["runtime"],
            countries=imdb["countries"],
            certificates=imdb["certificates"],
            languages=imdb["languages"],
            director=imdb["director"],
            writer=imdb["writer"],
            producer=imdb["producer"],
            composer=imdb["composer"],
            cinematographer=imdb["cinematographer"],
            music_team=imdb["music_team"],
            distributors=imdb["distributors"],
            release_date=imdb['release_date'],
            year=imdb['year'],
            genres=imdb['genres'],
            poster=imdb['poster'],
            plot=imdb['plot'],
            rating=imdb['rating'],
            url=imdb['url'],
            **locals()
        )
    else:
        cap = f"𝐒𝐚𝐡𝐞𝐛! 𝐌𝐮𝐣𝐡𝐞 𝐊𝐮𝐜𝐡 𝐌𝐢𝐥𝐚 𝐇𝐚𝐢 {search}\n\n"

    if imdb and imdb.get('poster'):
        try:
            await message.reply_photo(
                photo=imdb.get('poster'),
                caption=cap[:1024],
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await message.reply_photo(
                photo=poster,
                caption=cap[:1024],
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except Exception as e:
            logger.exception(e)
            await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply_text(cap, reply_markup=InlineKeyboardMarkup(btn))

    #if spoll:
       # await msg.message.delete(

	if spoll:
        if hasattr(msg, "message") and msg.message:
            await msg.message.delete()
        else:
            await msg.delete()
			


import asyncio
import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from fuzzywuzzy import fuzz
import logging

from database.ia_filterdb import Media
from utils import clean_file_name

async def mongo_spell_fallback(query: str, limit: int = 250) -> list[dict]:
    """
    Lightweight MongoDB fallback for spell checking.

    Returns:
        IMDb-like list:
        [
            {
                "title": "...",
                "year": "2023" | None
            }
        ]
    """

    if not query:
        return []

    words = [w for w in query.split() if len(w) >= 3]
    if not words:
        words = [query]

    regex = "|".join(re.escape(w) for w in words)

    try:
        cursor = (
            Media.find(
                {
                    "file_name": {
                        "$regex": regex,
                        "$options": "i",
                    }
                }
            )
            .limit(limit)
        )

        docs = await cursor.to_list(length=limit)

    except Exception as e:
        logger.exception("mongo_spell_fallback failed: %s", e)
        return []

    REMOVE_PATTERN = re.compile(
        r"""
        \b(
            480p|720p|1080p|1440p|2160p|4k|
            hdrip|webrip|web[- ]?dl|bluray|brrip|dvdrip|hdr|
            x264|x265|h264|h265|hevc|av1|
            aac|ac3|dd5\.?1|dts|atmos|
            esub|proper|remux|uncut|extended|
            dual\s*audio|multi\s*audio|
            hindi|english|tamil|telugu|malayalam|kannada|
            mkv|mp4|avi|m4v
        )\b
        """,
        re.IGNORECASE | re.VERBOSE,
    )

    YEAR_PATTERN = re.compile(r"\b((?:19|20)\d{2})\b")

    seen = set()
    candidates = []

    for doc in docs:
        try:
            name = clean_file_name(getattr(doc, "file_name", "") or "").strip()

            if not name:
                continue

            # Remove extension
            name = re.sub(r"\.[A-Za-z0-9]{2,5}$", "", name)

            # Normalize separators
            name = re.sub(r"[._\-]+", " ", name)

            # Extract year BEFORE removing it
            year_match = YEAR_PATTERN.search(name)
            year = year_match.group(1) if year_match else None

            # Remove year from title
            title = YEAR_PATTERN.sub("", name)

            # Remove quality / codec tags
            title = REMOVE_PATTERN.sub("", title)

            # Remove brackets
            title = re.sub(r"[\[\]\(\)\{\}]", " ", title)

            # Compress spaces
            title = " ".join(title.split()).strip()

            if len(title) < 3:
                continue

            key = title.lower()

            if key in seen:
                continue

            seen.add(key)

            candidates.append({
                "title": title,
                "year": year
            })

        except Exception:
            continue

    candidates.sort(
        key=lambda item: (
            fuzz.token_set_ratio(query.lower(), item["title"].lower()),
            fuzz.partial_ratio(query.lower(), item["title"].lower()),
            fuzz.ratio(query.lower(), item["title"].lower()),
        ),
        reverse=True,
    )

    if DEBUG_MODE:
        logger.info(
            "[SPELL] mongo_spell_fallback(%r) -> %d candidates | sample=%s",
            query,
            len(candidates),
            [
                f"{m['title']} ({m['year']})" if m["year"] else m["title"]
                for m in candidates[:10]
            ],
        )

    return candidates

async def advantage_spell_chok(client, msg, webapp=False):
    """Handles spell check for movie queries."""
    mv_id = msg.id
    user_id = msg.from_user.id if msg.from_user else 0

    if webapp:
        req_user = None
    else:
        req_user = await client.get_users(user_id)
        logger.info(
            f"Received spell check request from user {req_user.username or user_id} (User ID: {user_id})."
        )

    cleaned_text = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "",
        msg.text,
        flags=re.IGNORECASE
    ).strip()
    logger.info(f"Processed query in adv spell check: {cleaned_text}")

    flattened = cleaned_text.replace("\n", " ").replace("\r", " ")
    logger.info(f"Processed query in adv spell check: {flattened}")
    alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
    logger.info(f"Processed query in adv spell check: {alphanumeric_only}")
    query = " ".join(alphanumeric_only.split())

    if not query:
        if webapp:
            return {
                "status": "not_found",
                "query": "",
                "files": [],
                "total_results": 0,
                "next_offset": "",
                "suggestions": [],
            }
        return

    logger.info(f"Processed query in adv spell check: {query}")

    try:
        movies = await get_poster(query, bulk=True)

        if not movies:
            if DEBUG_MODE:
                logger.info("[SPELL] IMDb returned no movies, trying mongo_spell_fallback(query=%r)", query)
            movies = await mongo_spell_fallback(query) or []

        logger.info("SpellCheck returned: %s", len(movies) if movies else 0)

        if DEBUG_MODE and movies:
            logger.info("[SPELL] candidates sample -> %s", [m.get("title") for m in movies[:10] if isinstance(m, dict)])

        if not movies:
            search_query = query.replace(" ", "+")
            if webapp:
                return {
                    "status": "not_found",
                    "query": query,
                    "files": [],
                    "total_results": 0,
                    "next_offset": "",
                    "suggestions": [],
                }

            buttons = [
                [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
                [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
            ]
            await msg.reply(
                f"I couldn't find any movies related to **{query}**. Try searching on Google or in the request group.",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    except Exception as e:
        logger.error(f"Error fetching movies for query '{query}': {e}")
        if DEBUG_MODE:
            logger.exception("[SPELL] get_poster / mongo fallback failed")

        search_query = query.replace(" ", "+")
        if webapp:
            return {
                "status": "not_found",
                "query": query,
                "files": [],
                "total_results": 0,
                "next_offset": "",
                "suggestions": [],
            }

        buttons = [
            [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            "An error occurred while processing your request. Please try again or check the request group.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    movielist = (
        [movie.get('title') for movie in movies if isinstance(movie, dict) and movie.get('title')]
    )

    movielist = [x.strip() for x in movielist if x and x.strip()]
    movielist = list(dict.fromkeys(movielist))

    if DEBUG_MODE:
        logger.info("[SPELL] movielist size=%s | sample=%s", len(movielist), movielist[:10])

    if not movielist:
        search_query = query.replace(" ", "+")
        if webapp:
            return {
                "status": "not_found",
                "query": query,
                "files": [],
                "total_results": 0,
                "next_offset": "",
                "suggestions": [],
            }

        buttons = [
            [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            f"No valid movie titles found for **{query}**. Try searching on Google or in the request group.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    SPELL_CHECK[mv_id] = movielist

    try:
"""
        matched_movie = None
        for title in movielist:
            ratio = fuzz.ratio(query.lower(), title.lower())
            logger.debug(f"Matching '{query}' with '{title}', Ratio: {ratio}")
            if ratio > 60:
                matched_movie = title
				break
"""
        matched_movie = None
        best_ratio = 60  # Only accept matches strictly better than 60
        for title in movielist:

            ratio = fuzz.ratio(query.lower(), title.lower())
            logger.debug(f"Matching '{query}' with '{title}', Ratio: {ratio}")
            
            if ratio > best_ratio:
                best_ratio = ratio
                matched_movie = title
        
                

		
        if DEBUG_MODE:
            logger.info("[SPELL] matched_movie=%r", matched_movie)

        if matched_movie:
            files, offset, total_results = await get_search_results(matched_movie.lower(), offset=0, filter=True)

            if webapp:
                if files:
                    return {
                        "status": "corrected",
                        "query": query,
                        "corrected_query": matched_movie,
                        "files": files,
                        "offset": offset,
                        "total_results": total_results,
                        "next_offset": offset,
                    }
                return {
                    "status": "suggestions",
                    "query": query,
                    "suggestions": movielist[:10],
                    "files": [],
                    "total_results": 0,
                    "next_offset": "",
                }

            #if files:
               # await auto_filter(client, msg, (matched_movie, files, offset, total_results))
               # return

        if webapp:
            return {
                "status": "suggestions",
                "query": query,
                "suggestions": movielist[:10],
                "files": [],
                "total_results": 0,
                "next_offset": "",
            }

        search_query = query.replace(" ", "+")
        buttons = [
            [InlineKeyboardButton(movie.strip(), callback_data=f"spolling#{user_id}#{idx}")]
            for idx, movie in enumerate(movielist[:10])
        ]
        buttons.append([InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")])
        buttons.append([InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")])
        buttons.append([InlineKeyboardButton("Close", callback_data=f"spolling#{user_id}#close_spellcheck")])

        await msg.reply(
            f"<b>No close matches found for **{query}**.</b>\n\n"
            f"<b>Here are some suggestions:</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    except Exception as e:
        logger.error(f"Error during spell check for query '{query}': {e}")
        if DEBUG_MODE:
            logger.exception("[SPELL] fuzzy matching or follow-up flow failed")

        if webapp:
            return {
                "status": "not_found",
                "query": query,
                "files": [],
                "total_results": 0,
                "next_offset": "",
                "suggestions": [],
            }

        search_query = query.replace(" ", "+")
        buttons = [
            [InlineKeyboardButton("Search Google", url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton("Request Group", url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            "An error occurred while processing your request. Please try again or check the request group.",
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            await client.send_message(group_id, reply_text, disable_web_page_preview=True)
                        else:
                            button = eval(btn)
                            await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                    elif btn == "[]":
                        await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                    else:
                        button = eval(btn)
                        await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
