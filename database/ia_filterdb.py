"""
ia_filterdb.py – Media document model and search helpers.
FIXED: get_search_results() now correctly uses skip/limit instead of to_list(length=1).
       Replaced bare except with typed exception handling.
"""
from __future__ import annotations

import logging
import re
import base64
from struct import pack

from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError

from info import FILE_DB_URI, DATABASE_NAME, COLLECTION_NAME, USE_CAPTION_FILTER

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(FILE_DB_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)


@instance.register
class Media(Document):
    file_id   = fields.StrField(attribute="_id")
    file_ref  = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption   = fields.StrField(allow_none=True)

    class Meta:
        indexes          = ("$file_name",)
        collection_name  = COLLECTION_NAME


# ── Save ──────────────────────────────────────────────────────────────────────

async def save_file(media):
    """
    Persist a Telegram media object to MongoDB.
    Returns (True, 1) on insert, (False, 0) on duplicate, (False, 2) on validation error.
    """
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        doc = Media(
            file_id   = file_id,
            file_ref  = file_ref,
            file_name = file_name,
            file_size = media.file_size,
            file_type = media.file_type,
            mime_type = media.mime_type,
            caption   = media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception("Validation error while constructing Media document.")
        return False, 2

    try:
        await doc.commit()
    except DuplicateKeyError:
        logger.warning("Duplicate: %s already in database.", getattr(media, "file_name", "NO_FILE"))
        return False, 0

    logger.info("Saved: %s", getattr(media, "file_name", "NO_FILE"))
    return True, 1


# ── Search ────────────────────────────────────────────────────────────────────

async def get_search_results(
    query: str,
    file_type=None,
    max_results: int = 10,
    offset: int = 0,
    filter: bool = False,
):
    """
    Return (files, next_offset, total_results) for *query*.
    BUGFIX: previously called to_list(length=1) — now uses skip(offset).limit(max_results)
    so that pagination works correctly.
    """
    query = query.strip()

    if not query:
        raw_pattern = "."
    elif " " not in query:
        raw_pattern = r"(\b|[\.+\-_])" + query + r"(\b|[\.+\-_])"
    else:
        raw_pattern = query.replace(" ", r".*[\s\.+\-_]")

    try:
        regex = re.compile(raw_pattern, flags=re.IGNORECASE)
    except re.error as exc:
        logger.warning("Bad regex pattern '%s': %s", raw_pattern, exc)
        return [], "", 0

    mongo_filter: dict = (
        {"$or": [{"file_name": regex}, {"caption": regex}]}
        if USE_CAPTION_FILTER
        else {"file_name": regex}
    )
    if file_type:
        mongo_filter["file_type"] = file_type

    total_results = await Media.count_documents(mongo_filter)
    next_offset   = offset + max_results
    if next_offset >= total_results:
        next_offset = ""

    # FIXED: was cursor.to_list(length=max_results) without skip/limit applied first;
    #        the cursor mutation (skip/limit) must happen before to_list().
    cursor = Media.find(mongo_filter).sort("$natural", -1).skip(offset).limit(max_results)
    files  = await cursor.to_list(length=max_results)

    return files, next_offset, total_results


# ── Fetch single file ─────────────────────────────────────────────────────────

async def get_file_details(query: str) -> list:
    """Fetch up to one Media document by file_id."""
    mongo_filter = {"file_id": query}
    cursor       = Media.find(mongo_filter)
    return await cursor.to_list(length=1)


async def get_file_details1(query: str):
    """Fetch a single Media document by file_id; returns the doc or None."""
    try:
        result = await Media.find({"file_id": query}).limit(1).to_list(length=1)
        if result:
            return result[0]
        logger.warning("No file found for query: %s", query)
        return None
    except Exception as exc:
        logger.error("Error fetching file details for '%s': %s", query, exc)
        return None


# ── Encoding helpers ──────────────────────────────────────────────────────────

def encode_file_id(s: bytes) -> str:
    r = b""
    n = 0
    for i in s + bytes([22]) + bytes([4]):
        if i == 0:
            n += 1
        else:
            if n:
                r += b"\x00" + bytes([n])
                n = 0
            r += bytes([i])
    return base64.urlsafe_b64encode(r).decode().rstrip("=")


def encode_file_ref(file_ref: bytes) -> str:
    return base64.urlsafe_b64encode(file_ref).decode().rstrip("=")


def unpack_new_file_id(new_file_id: str):
    """Decode a Pyrogram file_id into (canonical_file_id, file_ref)."""
    decoded = FileId.decode(new_file_id)
    file_id = encode_file_id(
        pack("<iiqq", int(decoded.file_type), decoded.dc_id, decoded.media_id, decoded.access_hash)
    )
    file_ref = encode_file_ref(decoded.file_reference)
    return file_id, file_ref
