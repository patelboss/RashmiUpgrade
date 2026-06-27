import os
from pyrogram import Client, filters, enums
from pyrogram.errors.exceptions.bad_request_400 import UserNotParticipant, MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from info import IMDB_TEMPLATE
from utils import extract_user, get_file_id, get_poster, last_online
import time
from datetime import datetime
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

@Client.on_message(filters.command('id'))
async def showid(client, message):
    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        # Check if the user replied to a forwarded message
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            forwarded_chat = message.reply_to_message.forward_from_chat
            if forwarded_chat.type == enums.ChatType.CHANNEL:
                # Extract details for forwarded message
                channel_name = forwarded_chat.title
                channel_id = forwarded_chat.id
                user_id = message.from_user.id
                await message.reply_text(
                    f"<b>➲ User ID:</b> <code>{user_id}</code>\n"
                    f"<b>➲ Forwarded From {channel_name} </b>\n"
                    f"<b>➲ Forwarded Message From Channel ID:</b> <code>{channel_id}</code>",
                    quote=True
                )
            else:
                await message.reply_text("This message is not forwarded from a channel.", quote=True)
        else:
            # For private chat without a forwarded message
            user_id = message.chat.id
            first = message.from_user.first_name
            last = message.from_user.last_name or ""
            username = message.from_user.username
            dc_id = message.from_user.dc_id or ""
            await message.reply_text(
                f"<b>➲ First Name:</b> {first}\n"
                f"<b>➲ Last Name:</b> {last}\n"
                f"<b>➲ Username:</b> {username}\n"
                f"<b>➲ Telegram ID:</b> <code>{user_id}</code>\n"
                f"<b>➲ Data Centre:</b> <code>{dc_id}</code>",
                quote=True
            )

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        # For groups or supergroups
        if message.reply_to_message and message.reply_to_message.forward_from_chat:
            forwarded_chat = message.reply_to_message.forward_from_chat
            if forwarded_chat.type == enums.ChatType.CHANNEL:
                # Extract details for forwarded message
                channel_name = forwarded_chat.title
                channel_id = forwarded_chat.id
                user_id = message.from_user.id
                await message.reply_text(
                    f"<b>➲ User ID:</b> <code>{user_id}</code>\n"
                    f"<b>➲ Forwarded Message From <b>{channel_name}</b> Channel ID:</b> <code>{channel_id}</code>",
                    quote=True
                )
            else:
                await message.reply_text("This message is not forwarded from a channel.", quote=True)
        else:
            # General group or supergroup ID details
            _id = f"<b>➲ Chat ID:</b> <code>{message.chat.id}</code>\n"
            _id += (
                f"<b>➲ User ID:</b> "
                f"<code>{message.from_user.id if message.from_user else 'Anonymous'}</code>\n"
            )
            await message.reply_text(_id, quote=True)     
            
@Client.on_message(filters.command(["info"]))
async def who_is(client, message):
    # https://github.com/SpEcHiDe/PyroGramBot/blob/master/pyrobot/plugins/admemes/whois.py#L19
    status_message = await message.reply_text(
        "`Fetching user info...`"
    )
    await status_message.edit(
        "`Processing user info...`"
    )
    from_user = None
    from_user_id, _ = extract_user(message)
    try:
        from_user = await client.get_users(from_user_id)
    except Exception as error:
        await status_message.edit(str(error))
        return
    if from_user is None:
        return await status_message.edit("no valid user_id / message specified")
    message_out_str = ""
    message_out_str += f"<b>➲First Name:</b> {from_user.first_name}\n"
    last_name = from_user.last_name or "<b>None</b>"
    message_out_str += f"<b>➲Last Name:</b> {last_name}\n"
    message_out_str += f"<b>➲Telegram ID:</b> <code>{from_user.id}</code>\n"
    username = from_user.username or "<b>None</b>"
    dc_id = from_user.dc_id or "[User Doesn't Have A Valid DP]"
    message_out_str += f"<b>➲Data Centre:</b> <code>{dc_id}</code>\n"
    message_out_str += f"<b>➲User Name:</b> @{username}\n"
    message_out_str += f"<b>➲User 𝖫𝗂𝗇𝗄:</b> <a href='tg://user?id={from_user.id}'><b>Click Here</b></a>\n"
    if message.chat.type in ((enums.ChatType.SUPERGROUP, enums.ChatType.CHANNEL)):
        try:
            chat_member_p = await message.chat.get_member(from_user.id)
            joined_date = (
                chat_member_p.joined_date or datetime.now()
            ).strftime("%Y.%m.%d %H:%M:%S")
            message_out_str += (
                "<b>➲Joined this Chat on:</b> <code>"
                f"{joined_date}"
                "</code>\n"
            )
        except UserNotParticipant:
            pass
    chat_photo = from_user.photo
    if chat_photo:
        local_user_photo = await client.download_media(
            message=chat_photo.big_file_id
        )
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=local_user_photo,
            quote=True,
            reply_markup=reply_markup,
            caption=message_out_str,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
        os.remove(local_user_photo)
    else:
        buttons = [[
            InlineKeyboardButton('🔐 Close', callback_data='close_data')
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=message_out_str,
            reply_markup=reply_markup,
            quote=True,
            parse_mode=enums.ParseMode.HTML,
            disable_notification=True
        )
    await status_message.delete()

@Client.on_message(filters.command(["imdb"]))
async def imdb_search(client, message):
    if ' ' in message.text:
        k = await message.reply('Searching ImDB')
        r, title = message.text.split(None, 1)
        movies = await get_poster(title, bulk=True)
        if not movies:
            return await message.reply("No results Found")
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{movie.get('title')} - {movie.get('year')}",
                    callback_data=f"imdb#{movie.movieID}",
                )
            ]
            for movie in movies
        ]
        await k.edit('Here is what i found on IMDb', reply_markup=InlineKeyboardMarkup(btn))
    else:
        await message.reply('Give me a movie / series Name')

@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot: Client, quer_y: CallbackQuery):
    i, movie = quer_y.data.split('#')
    imdb = await get_poster(query=movie, id=True)
    btn = [
            [
                InlineKeyboardButton(
                    text=f"{imdb.get('title')}",
                    url=imdb['url'],
                )
            ]
        ]
    message = quer_y.message.reply_to_message or quer_y.message
    if imdb:
        caption = IMDB_TEMPLATE.format(
            query = imdb['title'],
            title = imdb['title'],
            votes = imdb['votes'],
            aka = imdb["aka"],
            seasons = imdb["seasons"],
            box_office = imdb['box_office'],
            localized_title = imdb['localized_title'],
            kind = imdb['kind'],
            imdb_id = imdb["imdb_id"],
            cast = imdb["cast"],
            runtime = imdb["runtime"],
            countries = imdb["countries"],
            certificates = imdb["certificates"],
            languages = imdb["languages"],
            director = imdb["director"],
            writer = imdb["writer"],
            producer = imdb["producer"],
            composer = imdb["composer"],
            cinematographer = imdb["cinematographer"],
            music_team = imdb["music_team"],
            distributors = imdb["distributors"],
            release_date = imdb['release_date'],
            year = imdb['year'],
            genres = imdb['genres'],
            poster = imdb['poster'],
            plot = imdb['plot'],
            rating = imdb['rating'],
            url = imdb['url'],
            **locals()
        )
    else:
        caption = "No Results"
    if imdb.get('poster'):
        try:
            await quer_y.message.reply_photo(photo=imdb['poster'], caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await quer_y.message.reply_photo(photo=poster, caption=caption, reply_markup=InlineKeyboardMarkup(btn))
        except Exception as e:
            logger.exception(e)
            await quer_y.message.reply(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
        await quer_y.message.delete()
    else:
        await quer_y.message.edit(caption, reply_markup=InlineKeyboardMarkup(btn), disable_web_page_preview=False)
    await quer_y.answer()
        
import logging
import json
import os

from pyrogram import Client, filters, enums
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
import variables
from database.ia_filterdb import get_file_details
from utils import get_size, clean_file_name

# Configure structured runtime logger
logger = logging.getLogger("Rashmibot.webapp")
logger.setLevel(logging.INFO)


def _webapp_url() -> str:
    """Build and validate the Web App URL served by this bot."""
    base = os.environ.get("BASE_URL", "").rstrip("/")
    logger.info("Resolving WebApp Base URL config. Found string: '%s'", base)
    if base:
        return f"{base}/webapp"
    return ""


@Client.on_message(filters.command("web_app"))
async def webapp_cmd1(client: Client, message: Message) -> None:
    """Send an inline button that opens the Telegram Web App."""
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Command /webapp triggered by user ID: %s", user_id)
    
    url = _webapp_url()
    if not url:
        logger.warning("Aborting /webapp command dispatch: BASE_URL environment string empty or invalid.")
        await message.reply_text(
            "<b>Web App URL is not configured.</b>\n"
            "Set the <code>BASE_URL</code> environment variable to your server URL.",
            parse_mode=enums.ParseMode.HTML,
        )
        return

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔎 Open Media Search", web_app=WebAppInfo(url=url))],
    ])
    
    logger.info("Successfully dispatched markup containing WebApp Target: %s", url)
    await message.reply_text(
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.",
        reply_markup=markup,
        parse_mode=enums.ParseMode.HTML,
    )


@Client.on_message(filters.text & filters.incoming, group=100)
async def webapp_inline_handler1(client: Client, message: Message) -> None:
    
    if not message.text or not message.text.startswith("get_"):
        return

    user_id = message.from_user.id if message.from_user else "Unknown"
    file_id = message.text.replace("get_", "").strip()
    logger.info("Token extraction pipeline hit! User: %s, Processing Key ID: %s", user_id, file_id)

    if not file_id:
        logger.warning("Extraction aborted: Extracted file token payload empty.")
        return

    try:
        logger.info("Querying MongoDB layer for target ID matching: %s", file_id)
        files = await get_file_details(file_id)
        
        if not files:
            logger.warning("Data fetch returned empty for token: %s", file_id)
            await message.reply_text("⚠️ File not found in database.")
            return

        f = files
        title = clean_file_name(f.file_name)
        size = get_size(f.file_size)
        caption = f.caption or ""
        
        logger.info("File resolving payload loaded. Original Name: %s | Size: %s", f.file_name, size)

        # Dynamic variable fallback extractions matching current database environment logs
        custom_caption = getattr(variables, "CUSTOM_FILE_CAPTION", "")
        protect_content = getattr(variables, "PROTECT_CONTENT", False)
        ofr_cnl = getattr(variables, "OFR_CNL", "https://t.me/Filmykeedha")

        if custom_caption:
            try:
                caption = custom_caption.format(
                    file_name=title or "",
                    file_size=size or "",
                    file_caption=caption or "",
                )
            except Exception as formatting_err:
                logger.error("Caption metadata string parsing failed: %s", formatting_err)
                caption = caption or title

        btn = InlineKeyboardMarkup([
            [InlineKeyboardButton("Join Offer Zone 🤑", url=ofr_cnl)],
        ])
        
        logger.info("Sending cached document media map payload stream to target chat index: %s", user_id)
        await client.send_cached_media(
            chat_id=user_id,
            file_id=f.file_id,
            caption=caption or title,
            protect_content=protect_content,
            reply_markup=btn,
        )
        logger.info("Cached media stream delivered successfully.")

    except Exception as exc:
        logger.error("Critical failure during handling of file dispatch loop: %s", exc, exc_info=True)
        await message.reply_text("⚠️ Could not process or send the requested file record.")
