#from database.verified import *
import logging, asyncio, os, re, random, pytz, aiohttp, requests, string, json, http.client
from info import *
#from info import AUTH_CHANNEL, LONG_IMDB_DESCRIPTION, MAX_LIST_ELM, DEBUG_MODE
from datetime import datetime, date
import logging
from pyrogram.errors import InputUserDeactivated, UserNotParticipant, FloodWait, UserIsBlocked, PeerIdInvalid
from variables import AUTH_CHANNELS
import asyncio
from pyrogram import enums
from typing import Union
import re
import os
from imdb import Cinemagoer
#from datetime import datetime
from typing import List
from database.users_chats_db import db
from bs4 import BeautifulSoup
import requests
from shortzy import Shortzy
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, InlineQuery
import sys

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

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)
imdb = Cinemagoer()
#imdb = IMDb()
TOKENS = {}
VERIFIED = {}
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)

# temp db for banned
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    GETALL = {}
    SHORT = {}
    SETTINGS = {}

import os
from pyrogram.errors import UserNotParticipant
from pyrogram import enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

REQUEST_TO_JOIN_MODE = 'False'

async def is_subscribed(bot, query):
    missing_channels = []

    if DEBUG_MODE:
        logger.info(
            "[SUB] is_subscribed entered | user_id=%s | query_type=%s | total_channels=%s",
            getattr(getattr(query, "from_user", None), "id", None),
            type(query).__name__,
            len(AUTH_CHANNELS),
        )

    for channel_id in AUTH_CHANNELS:
        try:
            if DEBUG_MODE:
                logger.info(
                    "[SUB] checking channel_id=%s for user_id=%s",
                    channel_id,
                    query.from_user.id,
                )
            user = await bot.get_chat_member(int(channel_id), query.from_user.id)
            if DEBUG_MODE:
                logger.info(
                    "[SUB] channel_id=%s status=%s",
                    channel_id,
                    getattr(user, "status", None),
                )
            if user.status == enums.ChatMemberStatus.BANNED:
                if DEBUG_MODE:
                    logger.warning(
                        "[SUB] user_id=%s is banned in channel_id=%s",
                        query.from_user.id,
                        channel_id,
                    )
                return False
        except UserNotParticipant:
            if DEBUG_MODE:
                logger.info(
                    "[SUB] user_id=%s is not participant in channel_id=%s",
                    query.from_user.id,
                    channel_id,
                )
            missing_channels.append(channel_id)
            continue
        except Exception as e:
            logger.error(
                "Error while checking channel %s for user %s: %s",
                channel_id,
                query.from_user.id,
                e,
            )

    if missing_channels:
        if DEBUG_MODE:
            logger.info(
                "[SUB] missing channels for user_id=%s -> %s",
                query.from_user.id,
                missing_channels,
            )
        join_buttons = []
        for channel_id in missing_channels:
            if DEBUG_MODE:
                logger.info("[SUB] fetching chat info for missing channel_id=%s", channel_id)
            channel = await bot.get_chat(int(channel_id))
            join_buttons.append(
                InlineKeyboardButton(f"Join {channel.title}", url=channel.invite_link)
            )
        reply_markup = InlineKeyboardMarkup([join_buttons])

        if isinstance(query, CallbackQuery):
            if DEBUG_MODE:
                logger.info("[SUB] responding via CallbackQuery prompt")
            await query.answer(
                text="Please join all required channels & Unmute Them to use the bot.\nTap on Files Again",
                show_alert=True
            )
            await query.message.reply(
                "Join the channels using the buttons below.\nTap on Join Then Unmute\nTap On Files Again To Get Files",
                reply_markup=reply_markup
            )
        elif isinstance(query, InlineQuery):
            if DEBUG_MODE:
                logger.info("[SUB] responding via InlineQuery prompt")
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="Please subscribe to all required channels.",
                switch_pm_parameter="subscribe"
            )
        else:
            if DEBUG_MODE:
                logger.info("[SUB] responding via Message prompt")
            await query.reply(
                "You need to join all the required channels & Unmute Them to get the files.",
                reply_markup=reply_markup
            )
        return False

    if DEBUG_MODE:
        logger.info("[SUB] user_id=%s is subscribed to all required channels", query.from_user.id)
    return True


async def get_poster(query, bulk=False, id=False, file=None):
    if DEBUG_MODE:
        logger.info(
            "[IMDB] get_poster entered | query=%r | bulk=%s | id=%s | file=%r",
            query, bulk, id, file
        )

    if not id:
        query = (query.strip()).lower()
        title = query
        if DEBUG_MODE:
            logger.info("[IMDB] normalized query=%r", query)

        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
            if DEBUG_MODE:
                logger.info("[IMDB] trailing year detected=%r | title=%r", year, title)
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                if DEBUG_MODE:
                    logger.info("[IMDB] year inferred from file=%r", year)
        else:
            year = None
            if DEBUG_MODE:
                logger.info("[IMDB] no year detected")

        if DEBUG_MODE:
            logger.info("[IMDB] searching movie title=%r", title.lower())

        movieid = imdb.search_movie(title.lower(), results=10)

        if DEBUG_MODE:
            logger.info("[IMDB] search_movie returned count=%s", len(movieid) if movieid else 0)

        if not movieid:
            if DEBUG_MODE:
                logger.info("[IMDB] no search results for query=%r", query)
            return None

        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if DEBUG_MODE:
                logger.info(
                    "[IMDB] year filter applied=%r | before=%s | after=%s",
                    year,
                    len(movieid),
                    len(filtered)
                )
            if not filtered:
                filtered = movieid
                if DEBUG_MODE:
                    logger.info("[IMDB] year filter empty, falling back to original results")
        else:
            filtered = movieid

        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if DEBUG_MODE:
            logger.info(
                "[IMDB] kind filter applied | before=%s | after=%s",
                len(filtered),
                len(movieid)
            )
        if not movieid:
            movieid = filtered
            if DEBUG_MODE:
                logger.info("[IMDB] kind filter empty, falling back to filtered results")

        if bulk:
            if DEBUG_MODE:
                logger.info("[IMDB] bulk=True returning count=%s", len(movieid) if movieid else 0)
            return movieid if movieid else None

        movieid = movieid[0].movieID
        if DEBUG_MODE:
            logger.info("[IMDB] selected movieid=%s", movieid)
    else:
        movieid = query
        if DEBUG_MODE:
            logger.info("[IMDB] id=True using direct movieid=%s", movieid)

    movie = imdb.get_movie(movieid)
    if DEBUG_MODE:
        logger.info("[IMDB] get_movie fetched=%s", bool(movie))
    if not movie:
        if DEBUG_MODE:
            logger.info("[IMDB] movie not found for movieid=%s", movieid)
        return None

    date = movie.get("original air date") or movie.get("year") or "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
        if DEBUG_MODE:
            logger.info("[IMDB] plot source=plot | length=%s", len(plot) if plot else 0)
    else:
        plot = movie.get('plot outline')
        if DEBUG_MODE:
            logger.info("[IMDB] plot source=plot outline | length=%s", len(plot) if plot else 0)
    if plot and len(plot) > 800:
        if DEBUG_MODE:
            logger.info("[IMDB] truncating plot from %s to 800 chars", len(plot))
        plot = plot[:800] + "..."

    result = {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

    if DEBUG_MODE:
        logger.info(
            "[IMDB] result ready | title=%r | year=%r | kind=%r | poster=%s",
            result.get("title"),
            result.get("year"),
            result.get("kind"),
            bool(result.get("poster")),
        )

    return result


async def get_poster2(query, bulk=False, id=False, file=None):
    if DEBUG_MODE:
        logger.info(
            "[IMDB2] get_poster2 entered | query=%r | bulk=%s | id=%s | file=%r",
            query, bulk, id, file
        )

    if not id:
        query = (query.strip()).lower()
        title = query
        if DEBUG_MODE:
            logger.info("[IMDB2] normalized query=%r", query)

        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = (query.replace(year, "")).strip()
            if DEBUG_MODE:
                logger.info("[IMDB2] trailing year detected=%r | title=%r", year, title)
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
                if DEBUG_MODE:
                    logger.info("[IMDB2] year inferred from file=%r", year)
        else:
            year = None
            if DEBUG_MODE:
                logger.info("[IMDB2] no year detected")

        if DEBUG_MODE:
            logger.info("[IMDB2] searching movie title=%r", title.lower())

        movieid = imdb.search_movie(title.lower(), results=10)
        if DEBUG_MODE:
            logger.info("[IMDB2] search_movie returned count=%s", len(movieid) if movieid else 0)

        if not movieid:
            if DEBUG_MODE:
                logger.info("[IMDB2] no search results for query=%r", query)
            return None

        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if DEBUG_MODE:
                logger.info(
                    "[IMDB2] year filter applied=%r | before=%s | after=%s",
                    year,
                    len(movieid),
                    len(filtered)
                )
            if not filtered:
                filtered = movieid
                if DEBUG_MODE:
                    logger.info("[IMDB2] year filter empty, falling back to original results")
        else:
            filtered = movieid

        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if DEBUG_MODE:
            logger.info(
                "[IMDB2] kind filter applied | before=%s | after=%s",
                len(filtered),
                len(movieid)
            )
        if not movieid:
            movieid = filtered
            if DEBUG_MODE:
                logger.info("[IMDB2] kind filter empty, falling back to filtered results")

        if bulk:
            if DEBUG_MODE:
                logger.info("[IMDB2] bulk=True returning count=%s", len(movieid) if movieid else 0)
            return movieid

        movieid = movieid[0].movieID
        if DEBUG_MODE:
            logger.info("[IMDB2] selected movieid=%s", movieid)
    else:
        movieid = query
        if DEBUG_MODE:
            logger.info("[IMDB2] id=True using direct movieid=%s", movieid)

    movie = imdb.get_movie(movieid)
    if DEBUG_MODE:
        logger.info("[IMDB2] get_movie fetched=%s", bool(movie))
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"

    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
        if DEBUG_MODE:
            logger.info("[IMDB2] plot source=plot | length=%s", len(plot) if plot else 0)
    else:
        plot = movie.get('plot outline')
        if DEBUG_MODE:
            logger.info("[IMDB2] plot source=plot outline | length=%s", len(plot) if plot else 0)
    if plot and len(plot) > 800:
        if DEBUG_MODE:
            logger.info("[IMDB2] truncating plot from %s to 800 chars", len(plot))
        plot = plot[0:800] + "..."

    result = {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }

    if DEBUG_MODE:
        logger.info(
            "[IMDB2] result ready | title=%r | year=%r | kind=%r | poster=%s",
            result.get("title"),
            result.get("year"),
            result.get("kind"),
            bool(result.get("poster")),
        )

    return result


async def broadcast_messages(user_id, message, forward=False):
    try:
        if DEBUG_MODE:
            logger.info(
                "[BROADCAST] entered | user_id=%s | forward=%s | message_id=%s",
                user_id,
                forward,
                getattr(message, "id", None),
            )
        if forward:
            if DEBUG_MODE:
                logger.info("[BROADCAST] forwarding message to user_id=%s", user_id)
            await message.forward(chat_id=user_id)
        else:
            if DEBUG_MODE:
                logger.info("[BROADCAST] copying message to user_id=%s", user_id)
            await message.copy(chat_id=user_id)
        if DEBUG_MODE:
            logger.info("[BROADCAST] success | user_id=%s", user_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
        if DEBUG_MODE:
            logger.info("[BROADCAST] FloodWait encountered | seconds=%s", e.value)
        await asyncio.sleep(e.value)
        return await broadcast_messages(user_id, message, forward)
    except InputUserDeactivated:
        if DEBUG_MODE:
            logger.info("[BROADCAST] user_id=%s deactivated; removing from db", user_id)
        await db.delete_user(int(user_id))
        logger.info(f"{user_id} - Removed from database (deleted account).")
        return False, "Deleted"
    except UserIsBlocked:
        logger.info(f"{user_id} - Blocked the bot. will be deleted")
        if DEBUG_MODE:
            logger.info("[BROADCAST] user_id=%s blocked bot; removing from db", user_id)
        await db.delete_user(int(user_id))
        return False, "Blocked"
    except PeerIdInvalid:
        logger.info(f"{user_id} - PeerIdInvalid. & deleted")
        if DEBUG_MODE:
            logger.info("[BROADCAST] peer id invalid for user_id=%s; removing from db", user_id)
        await db.delete_user(int(user_id))
        return False, "Error"
    except Exception as e:
        logger.error(f"Error broadcasting to {user_id}: {e}")
        if DEBUG_MODE:
            logger.exception("[BROADCAST] unexpected failure | user_id=%s", user_id)
        return False, "Error"


async def broadcast_messages_group(chat_id, message, forward=False):
    try:
        if DEBUG_MODE:
            logger.info(
                "[BROADCAST_GROUP] entered | chat_id=%s | forward=%s | message_id=%s",
                chat_id,
                forward,
                getattr(message, "id", None),
            )
        if forward:
            if DEBUG_MODE:
                logger.info("[BROADCAST_GROUP] forwarding message to chat_id=%s", chat_id)
            await message.forward(chat_id=chat_id)
        else:
            if DEBUG_MODE:
                logger.info("[BROADCAST_GROUP] copying message to chat_id=%s", chat_id)
            msg = await message.copy(chat_id=chat_id)
            try:
                if DEBUG_MODE:
                    logger.info("[BROADCAST_GROUP] attempting pin | chat_id=%s", chat_id)
                await msg.pin()
                if DEBUG_MODE:
                    logger.info("[BROADCAST_GROUP] pin success | chat_id=%s", chat_id)
            except Exception as e:
                logger.warning(f"Could not pin message in group {chat_id}: {e}")
                if DEBUG_MODE:
                    logger.exception("[BROADCAST_GROUP] pin failed | chat_id=%s", chat_id)
        if DEBUG_MODE:
            logger.info("[BROADCAST_GROUP] success | chat_id=%s", chat_id)
        return True, "Success"
    except FloodWait as e:
        logger.warning(f"FloodWait: Sleeping for {e.value} seconds.")
        if DEBUG_MODE:
            logger.info("[BROADCAST_GROUP] FloodWait encountered | seconds=%s", e.value)
        await asyncio.sleep(e.value)
        return await broadcast_messages_group(chat_id, message, forward)
    except Exception as e:
        logger.error(f"Error broadcasting to group {chat_id}: {e}")
        if DEBUG_MODE:
            logger.exception("[BROADCAST_GROUP] unexpected failure | chat_id=%s", chat_id)
        return False, "Error"


async def search_gagala(text):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/61.0.3163.100 Safari/537.36'
    }
    if DEBUG_MODE:
        logger.info("[GAGALA] entered | text=%r", text)
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    if DEBUG_MODE:
        logger.info("[GAGALA] requesting url=%s", url)
    response = requests.get(url, headers=usr_agent)
    if DEBUG_MODE:
        logger.info("[GAGALA] response status=%s", getattr(response, "status_code", None))
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('h3')
    if DEBUG_MODE:
        logger.info("[GAGALA] titles found=%s", len(titles))
    return [title.getText() for title in titles]


async def get_settings(group_id):
    if DEBUG_MODE:
        logger.info("[SETTINGS] get_settings entered | group_id=%s", group_id)
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        if DEBUG_MODE:
            logger.info("[SETTINGS] cache miss | group_id=%s | loading from db", group_id)
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    else:
        if DEBUG_MODE:
            logger.info("[SETTINGS] cache hit | group_id=%s", group_id)
    return settings

async def save_group_settings(group_id, key, value):
    if DEBUG_MODE:
        logger.info(
            "[SETTINGS] save_group_settings entered | group_id=%s | key=%s | value=%r",
            group_id, key, value
        )
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)
    if DEBUG_MODE:
        logger.info(
            "[SETTINGS] save_group_settings saved | group_id=%s | key=%s",
            group_id, key
        )

def get_size(size):
    if DEBUG_MODE:
        logger.info("[UTIL] get_size entered | size=%r", size)
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    result = "%.2f %s" % (size, units[i])
    if DEBUG_MODE:
        logger.info("[UTIL] get_size result=%s", result)
    return result

def split_list(l, n):
    if DEBUG_MODE:
        logger.info("[UTIL] split_list entered | length=%s | chunk=%s", len(l), n)
    for i in range(0, len(l), n):
        yield l[i:i + n]

def get_file_id(msg: Message):
    if DEBUG_MODE:
        logger.info("[UTIL] get_file_id entered | has_media=%s", bool(getattr(msg, "media", None)))
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                if DEBUG_MODE:
                    logger.info("[UTIL] get_file_id matched type=%s", message_type)
                return obj

def extract_user(message: Message) -> Union[int, str]:
    if DEBUG_MODE:
        logger.info("[UTIL] extract_user entered | message_id=%s", getattr(message, "id", None))
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    if DEBUG_MODE:
        logger.info("[UTIL] extract_user result | user_id=%r | user_first_name=%r", user_id, user_first_name)
    return (user_id, user_first_name)

def list_to_str(k):
    if DEBUG_MODE:
        logger.info("[UTIL] list_to_str entered | type=%s | length=%s", type(k).__name__, len(k) if k else 0)
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)

def last_online(from_user):
    if DEBUG_MODE:
        logger.info("[UTIL] last_online entered | user_id=%s", getattr(from_user, "id", None))
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot :("
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago :("
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    if DEBUG_MODE:
        logger.info("[UTIL] last_online result=%r", time)
    return time

def split_quotes(text: str) -> List:
    if DEBUG_MODE:
        logger.info("[UTIL] split_quotes entered | text=%r", text)
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    result = list(filter(None, [key, rest]))
    if DEBUG_MODE:
        logger.info("[UTIL] split_quotes result=%r", result)
    return result

def parser(text, keyword):
    if DEBUG_MODE:
        logger.info("[UTIL] parser entered | keyword=%r | text_len=%s", keyword, len(text))
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        result = (note_data, buttons, alerts)
        if DEBUG_MODE:
            logger.info(
                "[UTIL] parser result | note_len=%s | buttons=%s | alerts=%s",
                len(note_data),
                len(buttons),
                len(alerts),
            )
        return result
    except Exception:
        return note_data, buttons, None

def remove_escapes(text: str) -> str:
    if DEBUG_MODE:
        logger.info("[UTIL] remove_escapes entered | text=%r", text)
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    if DEBUG_MODE:
        logger.info("[UTIL] remove_escapes result=%r", res)
    return res

def humanbytes(size):
    if DEBUG_MODE:
        logger.info("[UTIL] humanbytes entered | size=%r", size)
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    result = str(round(size, 2)) + " " + Dic_powerN[n] + 'B'
    if DEBUG_MODE:
        logger.info("[UTIL] humanbytes result=%s", result)
    return result

FILTER_KEYWORDS = ['[', '@', 'www.', 'clipmate', 'apd', 'movie', 'www', 'telegram', 'tg', 'Tg', 'Movies', 'Filmy4cap', 'clipmate']

def clean_file_name(file_name):
    if DEBUG_MODE:
        logger.info("[UTIL] clean_file_name entered | file_name=%r", file_name)
    result = ' '.join(filter(lambda x: not any(keyword in x for keyword in FILTER_KEYWORDS), file_name.split()))
    if DEBUG_MODE:
        logger.info("[UTIL] clean_file_name result=%r", result)
    return result

URL = "api.shareus.io"
SHORTLINK_API = "xLsXcbTQX2fPiDCCA1Wmh5eCLnp1"
VERIFY_SECOND_SHORTNER = "False"
VERIFY_SHORTLINK_API = "xLsXcbTQX2fPiDCCA1Wmh5eCLnp1"
VERIFY_SHORTLINK_URL = "api.shareus.io"

async def get_verify_shorted_link(link, url, api):
    API = api
    URL = url
    if DEBUG_MODE:
        logger.info(
            "[VERIFY_SHORT] entered | link=%r | url=%r | api_present=%s",
            link, url, bool(api)
        )
    if URL == "api.shareus.io":
        url = f'https://{URL}/easy_api'
        params = {
            "key": API,
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.text()
                    if DEBUG_MODE:
                        logger.info("[VERIFY_SHORT] success | response_len=%s", len(data))
                    return data
        except Exception as e:
            logger.error(e)
            if DEBUG_MODE:
                logger.exception("[VERIFY_SHORT] failed, returning original link")
            return link
    else:
        shortzy = Shortzy(api_key=API, base_site=URL)
        link = await shortzy.convert(link)
        if DEBUG_MODE:
            logger.info("[VERIFY_SHORT] shortzy converted link")
        return link

async def check_token(bot, userid, token):
    if DEBUG_MODE:
        logger.info("[TOKEN] check_token entered | userid=%s | token=%r", userid, token)
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        if DEBUG_MODE:
            logger.info("[TOKEN] user missing in db; adding user_id=%s", user.id)
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if DEBUG_MODE:
                logger.info("[TOKEN] token exists | used=%s", is_used)
            if is_used == True:
                return False
            else:
                return True
    else:
        if DEBUG_MODE:
            logger.info("[TOKEN] no token bucket for user_id=%s", user.id)
        return False

async def get_token(bot, userid, link):
    if DEBUG_MODE:
        logger.info("[TOKEN] get_token entered | userid=%s | link=%r", userid, link)
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        if DEBUG_MODE:
            logger.info("[TOKEN] user missing in db; adding user_id=%s", user.id)
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    link = f"{link}verify-{user.id}-{token}"
    if DEBUG_MODE:
        logger.info("[TOKEN] generated token=%s | verify_link=%r", token, link)
    shortened_verify_url = await get_verify_shorted_link(link, VERIFY_SHORTLINK_URL, VERIFY_SHORTLINK_API)
    if VERIFY_SECOND_SHORTNER == True:
        if DEBUG_MODE:
            logger.info("[TOKEN] second shortener enabled")
        snd_link = await get_verify_shorted_link(shortened_verify_url, VERIFY_SND_SHORTLINK_URL, VERIFY_SND_SHORTLINK_API)
        return str(snd_link)
    else:
        return str(shortened_verify_url)

async def verify_user(bot, userid, token):
    if DEBUG_MODE:
        logger.info("[VERIFY] verify_user entered | userid=%s | token=%r", userid, token)
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        if DEBUG_MODE:
            logger.info("[VERIFY] user missing in db; adding user_id=%s", user.id)
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    VERIFIED[user.id] = str(today)
    if DEBUG_MODE:
        logger.info("[VERIFY] user verified | user_id=%s | date=%s", user.id, today)

async def check_verification(bot, userid):
    if DEBUG_MODE:
        logger.info("[VERIFY] check_verification entered | userid=%s", userid)
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        if DEBUG_MODE:
            logger.info("[VERIFY] user missing in db; adding user_id=%s", user.id)
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(user.id, user.mention))
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    if user.id in VERIFIED.keys():
        EXP = VERIFIED[user.id]
        years, month, day = EXP.split('-')
        comp = date(int(years), int(month), int(day))
        if DEBUG_MODE:
            logger.info("[VERIFY] verified date=%s | today=%s", comp, today)
        if comp < today:
            return False
        else:
            return True
    else:
        if DEBUG_MODE:
            logger.info("[VERIFY] user_id=%s not verified", user.id)
        return False

async def send_all(bot, userid, files, ident, chat_id, user_name, query):
    if DEBUG_MODE:
        logger.info(
            "[SEND_ALL] entered | userid=%s | chat_id=%s | ident=%s | file_count=%s | user_name=%r",
            userid, chat_id, ident, len(files) if files else 0, user_name
        )
    settings = await get_settings(chat_id)
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    try:
        if ENABLE_SHORTLINK:
            if DEBUG_MODE:
                logger.info("[SEND_ALL] shortlink mode enabled")
            for file in files:
                title = file["file_name"]
                size = get_size(file["file_size"])
                if DEBUG_MODE:
                    logger.info("[SEND_ALL] processing file=%r | size=%r", title, size)
                if not await db.has_premium_access(userid) and SHORTLINK_MODE == True:
                    if DEBUG_MODE:
                        logger.info("[SEND_ALL] sending shortlink message to userid=%s", userid)
                    await bot.send_message(chat_id=userid, text=f"<b>Hᴇʏ ᴛʜᴇʀᴇ {user_name} 👋🏽 \n\n✅ Sᴇᴄᴜʀᴇ ʟɪɴᴋ ᴛᴏ ʏᴏᴜʀ ғɪʟᴇ ʜᴀs sᴜᴄᴄᴇssғᴜʟʟʏ ʙᴇᴇɴ ɢᴇɴᴇʀᴀᴛᴇᴅ ᴘʟᴇᴀsᴇ ᴄʟɪᴄᴋ ᴅᴏᴡɴʟᴏᴀᴅ ʙᴜᴛᴛᴏɴ\n\n🗃️ Fɪʟᴇ Nᴀᴍᴇ : {title}\n🔖 Fɪʟᴇ Sɪᴢᴇ : {size}</b>", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📤 Dᴏᴡɴʟᴏᴀᴅ 📥", url=await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start=files_{file['file_id']}"))]]))
        else:
            if DEBUG_MODE:
                logger.info("[SEND_ALL] direct media mode enabled")
            for file in files:
                f_caption = file["caption"]
                title = file["file_name"]
                size = get_size(file["file_size"])
                if DEBUG_MODE:
                    logger.info("[SEND_ALL] sending file=%r | size=%r", title, size)
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                                file_size='' if size is None else size,
                                                                file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        print(e)
                        if DEBUG_MODE:
                            logger.exception("[SEND_ALL] caption format failed for file=%r", title)
                        f_caption = f_caption
                if f_caption is None:
                    f_caption = f"{title}"
                await bot.send_cached_media(
                    chat_id=userid,
                    file_id=file["file_id"],
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton('Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ', url=GRP_LNK),
                                InlineKeyboardButton('Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ', url=CHNL_LNK)
                            ],[
                                InlineKeyboardButton("Check What's New", url="t.me/filmykeedha")
                            ],[
                                InlineKeyboardButton("Want To Earn", url="t.me/earningdailyforyou")
                            ]
                        ]
                    )
                )
        if DEBUG_MODE:
            logger.info("[SEND_ALL] completed successfully | userid=%s", userid)
    except UserIsBlocked:
        if DEBUG_MODE:
            logger.info("[SEND_ALL] user blocked bot | userid=%s", userid)
        await query.answer('Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !', show_alert=True)
    except PeerIdInvalid:
        if DEBUG_MODE:
            logger.info("[SEND_ALL] peer id invalid | userid=%s", userid)
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
    except Exception as e:
        logger.error(f"Error broadcasting to {userid}: {e}")
        if DEBUG_MODE:
            logger.exception("[SEND_ALL] unexpected failure | userid=%s", userid)
        await query.answer('Hᴇʏ, Sᴛᴀʀᴛ Bᴏᴛ Fɪʀsᴛ Aɴᴅ Cʟɪᴄᴋ Sᴇɴᴅ Aʟʟ', show_alert=True)
