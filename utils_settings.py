"""
utils_settings.py — group settings cache (get_settings/save_group_settings)
and the Google-search fallback (search_gagala), split out of utils.py.
See utils_state.py for the module-split overview.
"""

import logging
import requests
from bs4 import BeautifulSoup

from info import *
from database.users_chats_db import db
from utils_state import temp

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
