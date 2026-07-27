"""
spell_feedback_mdb.py – lightweight spell-feedback memory for movie searches.

Purpose:
- Save user-selected corrections like:
    mirgapur -> Mirzapur
- Learn from repeated user choices.
- Return IMDb-like suggestion objects: [{"title": "..."}]

This module does NOT replace your current workflow.
It only gives you:
- record_spell_feedback(...)
- get_spell_feedback_suggestions(...)
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from info import DATABASE_NAME, DATABASE_URI, DEBUG_MODE

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

_client = MongoClient(DATABASE_URI)
_db = _client[DATABASE_NAME]

# Collections
spell_feedback_col = _db["spell_feedback"]
spell_title_col = _db["spell_title_stats"]

_NORMALIZE_RE = re.compile(r"[^a-z0-9\s]+", re.IGNORECASE)
_SPACE_RE = re.compile(r"\s+")


def _norm(text: str | None) -> str:
    """
    Normalize text for matching.
    Keeps letters/numbers/spaces, collapses whitespace, lowercases.
    """
    if not text:
        return ""
    text = text.strip().lower()
    text = _NORMALIZE_RE.sub(" ", text)
    text = _SPACE_RE.sub(" ", text).strip()
    return text


def ensure_spell_feedback_indexes() -> None:
    """
    Create indexes once. Safe to call multiple times.
    """
    try:
        spell_feedback_col.create_index(
            [("search_norm", ASCENDING), ("selected_norm", ASCENDING)],
            unique=True,
            background=True,
            name="spell_feedback_pair_idx",
        )
        spell_feedback_col.create_index(
            [("search_norm", ASCENDING)],
            background=True,
            name="spell_feedback_search_idx",
        )
        spell_feedback_col.create_index(
            [("selected_norm", ASCENDING)],
            background=True,
            name="spell_feedback_selected_idx",
        )
        spell_feedback_col.create_index(
            [("count", DESCENDING)],
            background=True,
            name="spell_feedback_count_idx",
        )

        spell_title_col.create_index(
            [("title_norm", ASCENDING)],
            unique=True,
            background=True,
            name="spell_title_norm_idx",
        )
        spell_title_col.create_index(
            [("count", DESCENDING)],
            background=True,
            name="spell_title_count_idx",
        )

        if DEBUG_MODE:
            logger.info("[SPELLFDB] indexes ensured")
    except Exception as exc:
        logger.exception("[SPELLFDB] failed to create indexes: %s", exc)


ensure_spell_feedback_indexes()


async def record_spell_feedback(
    search_query: str,
    selected_title: str,
    user_id: int | None = None,
    source: str = "telegram",
) -> bool:
    """
    Save a user selection mapping.

    Example:
        search_query   = "mirgapur"
        selected_title = "Mirzapur"

    This stores and increments:
        search_norm + selected_norm pair count
        total title popularity count
    """
    try:
        search_raw = (search_query or "").strip()
        title_raw = (selected_title or "").strip()

        search_norm = _norm(search_raw)
        title_norm = _norm(title_raw)

        if DEBUG_MODE:
            logger.info(
                "[SPELLFDB] record entered | search=%r | selected=%r | user_id=%s | source=%s",
                search_raw,
                title_raw,
                user_id,
                source,
            )

        if not search_norm or not title_norm:
            if DEBUG_MODE:
                logger.info("[SPELLFDB] record skipped due to empty normalized values")
            return False

        now = datetime.utcnow()

        pair_set_on_insert = {
            "search": search_raw,
            "selected_title": title_raw,
            "search_norm": search_norm,
            "selected_norm": title_norm,
            "first_seen": now,
        }
        pair_set = {
            "last_seen": now,
            "source": source,
        }
        if user_id is not None:
            pair_set["last_user_id"] = int(user_id)

        pair_update: dict[str, Any] = {
            "$setOnInsert": pair_set_on_insert,
            "$set": pair_set,
            "$inc": {"count": 1},
        }
        if user_id is not None:
            pair_update["$addToSet"] = {"user_ids": int(user_id)}

        spell_feedback_col.update_one(
            {"search_norm": search_norm, "selected_norm": title_norm},
            pair_update,
            upsert=True,
        )

        title_set_on_insert = {
            "title": title_raw,
            "title_norm": title_norm,
            "first_seen": now,
        }
        title_set = {
            "last_seen": now,
        }
        if user_id is not None:
            title_set["last_user_id"] = int(user_id)

        spell_title_col.update_one(
            {"title_norm": title_norm},
            {
                "$setOnInsert": title_set_on_insert,
                "$set": title_set,
                "$inc": {"count": 1},
            },
            upsert=True,
        )

        if DEBUG_MODE:
            logger.info("[SPELLFDB] record saved | search=%r | selected=%r", search_norm, title_norm)
        return True

    except PyMongoError as exc:
        logger.exception("[SPELLFDB] database error while recording feedback: %s", exc)
        return False
    except Exception as exc:
        logger.exception("[SPELLFDB] unexpected error while recording feedback: %s", exc)
        return False


async def get_spell_feedback_suggestions(query: str, limit: int = 10) -> list[dict]:
    """
    Return IMDb-like suggestion objects from user feedback.

    Output example:
        [
            {"title": "Mirzapur", "count": 14},
            {"title": "Mirzapur Season 2", "count": 4},
        ]
    """
    try:
        raw_query = (query or "").strip()
        q_norm = _norm(raw_query)

        if DEBUG_MODE:
            logger.info("[SPELLFDB] fetch entered | query=%r | normalized=%r | limit=%s", raw_query, q_norm, limit)

        if not q_norm:
            return []

        tokens = [t for t in q_norm.split() if len(t) >= 3]
        if not tokens:
            tokens = [q_norm]

        regex_parts = [re.escape(q_norm)] + [re.escape(t) for t in tokens]
        regex = "|".join(regex_parts)

        pipeline = [
            {
                "$match": {
                    "$or": [
                        {"search_norm": q_norm},
                        {"selected_norm": q_norm},
                        {"search_norm": {"$regex": regex, "$options": "i"}},
                        {"selected_norm": {"$regex": regex, "$options": "i"}},
                    ]
                }
            },
            {
                "$group": {
                    "_id": "$selected_norm",
                    "title": {"$first": "$selected_title"},
                    "count": {"$sum": "$count"},
                    "last_seen": {"$max": "$last_seen"},
                }
            },
            {"$sort": {"count": -1, "last_seen": -1, "title": 1}},
            {"$limit": int(limit)},
        ]

        docs = list(spell_feedback_col.aggregate(pipeline))
        results = [
            {
                "title": (doc.get("title") or "").strip(),
                "count": int(doc.get("count") or 0),
            }
            for doc in docs
            if (doc.get("title") or "").strip()
        ]

        if DEBUG_MODE:
            logger.info(
                "[SPELLFDB] feedback suggestions | query=%r | count=%s | sample=%s",
                q_norm,
                len(results),
                [r["title"] for r in results[:10]],
            )
        return results

    except PyMongoError as exc:
        logger.exception("[SPELLFDB] database error while fetching suggestions: %s", exc)
        return []
    except Exception as exc:
        logger.exception("[SPELLFDB] unexpected error while fetching suggestions: %s", exc)
        return []


async def get_spell_feedback_top_titles(limit: int = 50) -> list[dict]:
    """
    Return the most selected canonical titles overall.
    """
    try:
        pipeline = [
            {"$sort": {"count": -1, "last_seen": -1}},
            {"$limit": int(limit)},
            {
                "$project": {
                    "_id": 0,
                    "title": 1,
                    "count": 1,
                    "last_seen": 1,
                }
            },
        ]
        docs = list(spell_title_col.aggregate(pipeline))
        if DEBUG_MODE:
            logger.info("[SPELLFDB] top titles fetched | count=%s", len(docs))
        return docs
    except Exception as exc:
        logger.exception("[SPELLFDB] failed to fetch top titles: %s", exc)
        return []


async def get_spell_feedback_pair_stats(search_query: str, limit: int = 10) -> list[dict]:
    """
    Return the top selected titles for a single query.
    """
    try:
        q_norm = _norm(search_query)
        if not q_norm:
            return []

        pipeline = [
            {"$match": {"search_norm": q_norm}},
            {
                "$group": {
                    "_id": "$selected_norm",
                    "title": {"$first": "$selected_title"},
                    "count": {"$sum": "$count"},
                    "last_seen": {"$max": "$last_seen"},
                }
            },
            {"$sort": {"count": -1, "last_seen": -1, "title": 1}},
            {"$limit": int(limit)},
        ]
        docs = list(spell_feedback_col.aggregate(pipeline))
        results = [
            {
                "title": (doc.get("title") or "").strip(),
                "count": int(doc.get("count") or 0),
            }
            for doc in docs
            if (doc.get("title") or "").strip()
        ]
        if DEBUG_MODE:
            logger.info("[SPELLFDB] pair stats | query=%r | count=%s", q_norm, len(results))
        return results
    except Exception as exc:
        logger.exception("[SPELLFDB] failed to fetch pair stats: %s", exc)
        return []
