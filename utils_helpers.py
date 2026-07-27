"""
plugins/... no — this lives at project root: utils_helpers.py

Small, mostly-synchronous helper functions with no dependency on other
utils_* modules (aside from utils_state for the SMART_OPEN/CLOSE/START_CHAR
constants used by split_quotes). See utils_state.py for the module-split
overview.
"""

import re
import logging
from typing import Union, List

from pyrogram import enums
from pyrogram.types import Message, InlineKeyboardButton

from info import *
from utils_state import SMART_OPEN, SMART_CLOSE, START_CHAR

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

FILTER_KEYWORDS = ['[', '@', 'www.', 'clipmate', 'apd', 'movie', 'www', 'telegram', 'tg', 'Tg', 'Movies', 'Filmy4cap', 'clipmate']


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

def clean_file_name(file_name):
    if DEBUG_MODE:
        logger.info("[UTIL] clean_file_name entered | file_name=%r", file_name)
    result = ' '.join(filter(lambda x: not any(keyword in x for keyword in FILTER_KEYWORDS), file_name.split()))
    if DEBUG_MODE:
        logger.info("[UTIL] clean_file_name result=%r", result)
    return result
