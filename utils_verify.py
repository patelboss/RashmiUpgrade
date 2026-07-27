"""
utils_verify.py — verification-link / token helpers, split out of utils.py.
See utils_state.py for the module-split overview.

NOTE: URL / SHORTLINK_API / VERIFY_SECOND_SHORTNER / VERIFY_SHORTLINK_API /
VERIFY_SHORTLINK_URL below are kept as the same hardcoded literal constants
that were in the original utils.py (they are NOT read from variables.py's
env-configurable settings of the same name — the original file never
imported those, so this preserves the exact original behavior, including
the fact that VERIFY_SECOND_SHORTNER is the literal string "False" and the
`if VERIFY_SECOND_SHORTNER == True` branch in get_token() below is
therefore always skipped, same as before).
"""

import random
import string
import logging
import pytz
import aiohttp
from datetime import date

from Script import script
from info import *
from database.users_chats_db import db
from shortzy import Shortzy
from utils_state import TOKENS, VERIFIED

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

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
