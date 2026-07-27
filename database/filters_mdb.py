"""
filters_mdb.py – Group keyword filter CRUD.
FIXED: replaced bare except, replaced deprecated .count() with count_documents().
"""
import logging

import pymongo
from pymongo import MongoClient
from pyrogram import enums

from info import DATABASE_URI, DATABASE_NAME, DEBUG_MODE
from langs.i18n import get, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

myclient: MongoClient = pymongo.MongoClient(DATABASE_URI)
mydb = myclient[DATABASE_NAME]


# ── CRUD ──────────────────────────────────────────────────────────────────────

async def add_filter(grp_id: int, text: str, reply_text: str, btn: str, file: str, alert: str) -> None:
    mycol = mydb[str(grp_id)]
    data = {
        "text":  str(text),
        "reply": str(reply_text),
        "btn":   str(btn),
        "file":  str(file),
        "alert": str(alert),
    }
    try:
        mycol.update_one({"text": str(text)}, {"$set": data}, upsert=True)
    except Exception:
        logger.exception("Failed to add/update filter '%s' in group %s.", text, grp_id)


async def find_filter(group_id: int, name: str):
    mycol = mydb[str(group_id)]
    query = mycol.find({"text": name})
    try:
        for doc in query:
            return (
                doc.get("reply"),
                doc.get("btn"),
                doc.get("alert"),
                doc.get("file"),
            )
    except Exception:
        logger.debug("No filter '%s' found in group %s.", name, group_id)
    return None, None, None, None


async def get_filters(group_id: int):
    mycol = mydb[str(group_id)]
    texts: list[str] = []
    try:
        for doc in mycol.find():
            if "text" in doc:
                texts.append(doc["text"])
    except Exception:
        logger.exception("Failed to list filters for group %s.", group_id)
    return texts


async def delete_filter(message, text: str, group_id: int, lang: str = DEFAULT_LANG) -> None:
    mycol  = mydb[str(group_id)]
    query  = {"text": text}
    # FIXED: .count() is removed in PyMongo 4.x; use count_documents()
    if mycol.count_documents(query) == 1:
        mycol.delete_one(query)
        if DEBUG_MODE:
            logger.info("[FILTERDB] filter deleted | group_id=%s text=%s", group_id, text)
        await message.reply_text(
            get(lang, "FILTERMDB_DELETED", text=text),
            quote=True,
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    else:
        await message.reply_text(get(lang, "FILTERMDB_NOT_FOUND"), quote=True)


async def del_all(message, group_id: int, title: str, lang: str = DEFAULT_LANG) -> None:
    if str(group_id) not in mydb.list_collection_names():
        await message.edit_text(get(lang, "FILTERMDB_DELALL_NOTHING", title=title))
        return
    mycol = mydb[str(group_id)]
    try:
        mycol.drop()
        if DEBUG_MODE:
            logger.info("[FILTERDB] all filters removed | group_id=%s", group_id)
        await message.edit_text(get(lang, "FILTERMDB_DELALL_SUCCESS", title=title))
    except Exception:
        logger.exception("Failed to drop filter collection for group %s.", group_id)
        await message.edit_text(get(lang, "FILTERMDB_DELALL_FAIL"))


async def count_filters(group_id: int):
    mycol = mydb[str(group_id)]
    # FIXED: replaced deprecated .count() with count_documents()
    count = mycol.count_documents({})
    return count if count > 0 else False


async def filter_stats() -> tuple[int, int]:
    collections = mydb.list_collection_names()
    if "CONNECTION" in collections:
        collections.remove("CONNECTION")

    total_count = 0
    for name in collections:
        # FIXED: count_documents instead of .count()
        total_count += mydb[name].count_documents({})

    return len(collections), total_count
