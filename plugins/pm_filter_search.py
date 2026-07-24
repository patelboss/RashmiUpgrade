"""
plugins/pm_filter_search.py — Search / auto-filter / spell-check engine.

Split out of the original monolithic pm_filter.py (see plugins/pm_filter.py
and plugins/pm_filter_callbacks.py for the other two parts). This file has
NO Pyrogram handlers of its own — it only exports the async helper
functions that the message/callback handlers in the sibling modules call
into:

    auto_filter()            — runs a group text message through search
    mongo_spell_fallback()   — regex-based fallback candidate list for spell-check
    manual_filters()         — matches configured keyword filters in a group
    advantage_spell_chok()   — full spell-check / suggestion flow

Logic and control flow are unchanged from the original file — only the
file boundary moved.
"""

import re
import math
import logging

from pyrogram.errors.exceptions.bad_request_400 import (
    MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode
from fuzzywuzzy import fuzz

from info import *
from database.ia_filterdb import Media, get_search_results
from database.filters_mdb import find_filter, get_filters
from database.spell_feedback_mdb import *
from utils import get_size, temp, get_settings, clean_file_name, get_poster

from plugins.pm_filter_state import FRESH, BUTTONS, SPELL_CHECK
from database.users_chats_db import db
from langs.i18n import get, get_btn, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


async def auto_filter(client, msg, spoll=False, webapp=False):
    if not spoll:
        message = msg
        lang = await _user_lang(getattr(message, "from_user", None))
        settings = await get_settings(message.chat.id)

        if message.text.startswith("/"):
            return

        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return

        if len(message.text) < 100:
            # 1. Flatten hidden carriage returns and vertical line breaks cleanly
            flattened = message.text.replace("\n", " ").replace("\r", " ")
            if DEBUG_MODE:
                logger.info("[AUTOFILTER] step1 flattened=%r", flattened)

            # 2. Extract only English characters, numbers, and white spaces
            alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
            if DEBUG_MODE:
                logger.info("[AUTOFILTER] step2 alphanumeric_only=%r", alphanumeric_only)

            # 3. Compress double spaces left behind by stripped special characters
            search = " ".join(alphanumeric_only.split())
            if DEBUG_MODE:
                logger.info("[AUTOFILTER] step3 search=%r", search)

            if not search or len(search) < 3:
                if DEBUG_MODE:
                    logger.info("[AUTOFILTER] query too short, aborting | query=%r", search)

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
                        get(lang, "SEARCH_INVALID_QUERY"),
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
        search, files, offset, total_results = spoll
        if hasattr(msg, "message"):  # CallbackQuery
            settings = await get_settings(msg.message.chat.id)
            message = msg.message.reply_to_message
        else:                               # Normal Message (spell check)
            settings = await get_settings(msg.chat.id)
            message = msg
            #search, files, offset, total_results = spoll
        lang = await _user_lang(getattr(message, "from_user", None))

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
            InlineKeyboardButton(get_btn(lang, "BTN_SEND_ALL"), callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(get(lang, "BTN_RESULTS_OF", search=search), callback_data=f"fsendfiles#{key}")
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
            InlineKeyboardButton(get_btn(lang, "BTN_SEND_ALL"), callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(get(lang, "BTN_RESULTS_OF", search=search), callback_data=f"fsendfiles#{key}")
        ])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [
                InlineKeyboardButton(
                    text=get(lang, "BTN_PAGES_COUNTER", total_pages=math.ceil(int(total_results) / 10)),
                    callback_data="pages"
                ),
                InlineKeyboardButton(text=get_btn(lang, "BTN_NEXT"), callback_data=f"next_{req}_{key}_{offset}")
            ]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text=get_btn(lang, "BTN_PAGES_SINGLE"), callback_data="pages")]
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
        cap = get(lang, "SEARCH_NO_IMDB_CAPTION", search=search)

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
    # Use exactly 4 standard spaces here:
    if spoll:
        # Use exactly 8 standard spaces here:
        if hasattr(msg, "message") and msg.message:
            # Use exactly 12 standard spaces here:
            await msg.message.delete()
        else:
            # Use exactly 12 standard spaces here:
            await msg.delete()


async def mongo_spell_fallback(query: str, limit: int = 250) -> list[dict]:
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


async def manual_filters(client, message, text=False):
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            if DEBUG_MODE:
                logger.info("[MANUALFILTER] keyword matched | group_id=%s keyword=%r", group_id, keyword)
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


async def advantage_spell_chok(client, msg, webapp=False):
    """Handles spell check for movie queries."""
    mv_id = msg.id
    user_id = msg.from_user.id if msg.from_user else 0

    lang = await _user_lang(msg.from_user if hasattr(msg, "from_user") else None)

    if webapp:
        req_user = None
    else:
        req_user = await client.get_users(user_id)
        if DEBUG_MODE:
            logger.info(
                "[SPELL] request received | user=%s user_id=%s",
                req_user.username or user_id, user_id
            )

    cleaned_text = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "",
        msg.text,
        flags=re.IGNORECASE
    ).strip()
    if DEBUG_MODE:
        logger.info("[SPELL] step1 cleaned_text=%r", cleaned_text)

    flattened = cleaned_text.replace("\n", " ").replace("\r", " ")
    if DEBUG_MODE:
        logger.info("[SPELL] step2 flattened=%r", flattened)
    alphanumeric_only = re.sub(r'[^a-zA-Z0-9\s]', ' ', flattened)
    if DEBUG_MODE:
        logger.info("[SPELL] step3 alphanumeric_only=%r", alphanumeric_only)
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

    if DEBUG_MODE:
        logger.info("[SPELL] step4 query=%r", query)

    try:
        movies = []

        feedback_movies = await get_spell_feedback_suggestions(query, limit=250)
        if feedback_movies:
            movies = feedback_movies
            if DEBUG_MODE:
                logger.info("[SPELL] feedback suggestions used | count=%s", len(movies))
                logger.info(
                    "[SPELL] feedback candidates sample -> %s",
                    [m.get("title") for m in movies[:10] if isinstance(m, dict)]
                )

        if not movies:
            movies = await mongo_spell_fallback(query) or []
            if DEBUG_MODE:
                logger.info("[SPELL] mongo fallback used | count=%s", len(movies))
                if movies:
                    logger.info(
                        "[SPELL] mongo candidates sample -> %s",
                        [m.get("title") for m in movies[:10] if isinstance(m, dict)]
                    )

        if not movies:
            if DEBUG_MODE:
                logger.info("[SPELL] IMDb fallback used for query=%r", query)
            movies = await get_poster(query, bulk=True) or []

        if DEBUG_MODE:
            logger.info("[SPELL] SpellCheck returned: %s", len(movies) if movies else 0)

        if DEBUG_MODE and movies:
            logger.info(
                "[SPELL] candidates sample -> %s",
                [m.get("title") for m in movies[:10] if isinstance(m, dict)]
            )

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
                [InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GOOGLE"), url=f"https://www.google.com/search?q={search_query}")],
                [InlineKeyboardButton(get_btn(lang, "BTN_REQUEST_GROUP"), url="https://t.me/+GXTgHzS9LtViN2U9")]
            ]
            await msg.reply(
                get(lang, "SPELL_NOT_FOUND", query=query),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
            return

    except Exception as e:
        logger.error(f"Error fetching movies for query '{query}': {e}")
        if DEBUG_MODE:
            logger.exception("[SPELL] feedback / mongo / imdb fallback failed")

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
            [InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GOOGLE"), url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton(get_btn(lang, "BTN_REQUEST_GROUP"), url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            get(lang, "SPELL_GENERIC_ERROR"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    movielist = [
        movie.get('title')
        for movie in movies
        if isinstance(movie, dict) and movie.get('title')
    ]

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
            [InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GOOGLE"), url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton(get_btn(lang, "BTN_REQUEST_GROUP"), url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            get(lang, "SPELL_NO_VALID_TITLES", query=query),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return

    SPELL_CHECK[mv_id] = movielist

    try:
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

            if files:
                await auto_filter(client, msg, (matched_movie, files, offset, total_results))
                return

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
        buttons.append([InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GOOGLE"), url=f"https://www.google.com/search?q={search_query}")])
        buttons.append([InlineKeyboardButton(get_btn(lang, "BTN_REQUEST_GROUP"), url="https://t.me/+GXTgHzS9LtViN2U9")])
        buttons.append([InlineKeyboardButton(get_btn(lang, "BTN_SPELL_CLOSE"), callback_data=f"spolling#{user_id}#close_spellcheck")])

        await msg.reply(
            get(lang, "SPELL_NO_CLOSE_MATCHES", query=query),
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
            [InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GOOGLE"), url=f"https://www.google.com/search?q={search_query}")],
            [InlineKeyboardButton(get_btn(lang, "BTN_REQUEST_GROUP"), url="https://t.me/+GXTgHzS9LtViN2U9")]
        ]
        await msg.reply(
            get(lang, "SPELL_GENERIC_ERROR"),
            reply_markup=InlineKeyboardMarkup(buttons)
        )
        return
