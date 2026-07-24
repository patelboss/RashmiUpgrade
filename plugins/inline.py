import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, clean_file_name
from info import CACHE_TIME, AUTH_CHANNEL, GRP_LNK, CHNL_LNK, DEBUG_MODE
from database.connections_mdb import active_connection
from database.users_chats_db import db
from variables import CUSTOM_FILE_CAPTION
from langs.i18n import get, get_btn, DEFAULT_LANG
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

cache_time = 0 if AUTH_CHANNEL else CACHE_TIME


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for the given inline query."""
    lang = await _user_lang(query.from_user)
    if DEBUG_MODE:
        logger.info("[INLINE] query received | user_id=%s query=%r", query.from_user.id, query.query)

    chat_id = await active_connection(str(query.from_user.id))

    # Check if the user is subscribed to the required channel
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
        if DEBUG_MODE:
            logger.info("[INLINE] user not subscribed | user_id=%s", query.from_user.id)
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text=get(lang, "INLINE_NOT_SUBSCRIBED"),
            switch_pm_parameter="subscribe"
        )
        return

    results = []
    if '|' in query.query:
        string, file_type = query.query.split('|', maxsplit=1)
        string = string.strip()
        file_type = file_type.strip().lower()
    else:
        string = query.query.strip()
        file_type = None

    if not string:  # Default message for empty queries
        if DEBUG_MODE:
            logger.info("[INLINE] empty query | user_id=%s", query.from_user.id)
        await query.answer(
            results=[],
            cache_time=cache_time,
            switch_pm_text=get(lang, "INLINE_EMPTY_QUERY"),
            switch_pm_parameter="default"
        )
        return

    offset = int(query.offset or 0)

    reply_markup = get_reply_markup(query=string, lang=lang)

    try:
        # Ensure correct argument mapping for get_search_results
        files, next_offset, total_results = await get_search_results(
            query=string,
            file_type=file_type,
            max_results=10,
            offset=offset
        )
        if DEBUG_MODE:
            logger.info("[INLINE] search results retrieved | query=%r user_id=%s total=%s", string, query.from_user.id, total_results)
    except Exception as e:
        logger.error(f"Error while fetching search results for query '{string}': {e}")
        await query.answer(
            results=[],
            cache_time=cache_time,
            switch_pm_text=get(lang, "INLINE_SEARCH_ERROR"),
            switch_pm_parameter="error"
        )
        return

    for file in files:
        try:
            title = clean_file_name(file.file_name)
            size = get_size(file.file_size)
            f_caption = file.caption
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title,
                        file_size=size,
                        file_caption=f_caption
                    )
                except Exception:
                    logger.warning(f"Error formatting custom caption for file '{title}'.")
            if not f_caption:
                f_caption = title

            results.append(
                InlineQueryResultCachedDocument(
                    title=title,
                    document_file_id=file["file_id"],
                    caption=f_caption,
                    description=f"Size: {size}\nType: {file.file_type}",
                    reply_markup=reply_markup
                )
            )
        except Exception as e:
            logger.error(f"Error while processing file '{file.get('file_name', 'Unknown')}': {e}")
            continue

    if results:
        switch_pm_text = f"{emoji.FILE_FOLDER} " + get(lang, "INLINE_RESULTS_FOUND", total_results=total_results)
        if string:
            switch_pm_text += get(lang, "INLINE_RESULTS_SUFFIX", query=string)
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
            if DEBUG_MODE:
                logger.info("[INLINE] results sent | query=%r user_id=%s count=%s", string, query.from_user.id, len(results))
        except QueryIdInvalid:
            logger.warning(f"QueryIdInvalid error for user {query.from_user.id}.")
    else:
        switch_pm_text = f"{emoji.CROSS_MARK} " + get(lang, "INLINE_NO_RESULTS")
        if string:
            switch_pm_text += get(lang, "INLINE_RESULTS_SUFFIX", query=string)

        if DEBUG_MODE:
            logger.info("[INLINE] no results | query=%r user_id=%s", string, query.from_user.id)

        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="no_results"
        )

def get_reply_markup1(query, lang=DEFAULT_LANG):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_AGAIN"), switch_inline_query_current_chat=query)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_reply_markup(query, lang=DEFAULT_LANG):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_AGAIN"), switch_inline_query_current_chat=query)  # Existing button
        ],
        [
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH_GROUP_PLAIN"), url=GRP_LNK),  # Link to the search group
            InlineKeyboardButton(get_btn(lang, "BTN_MAIN_CHANNEL_PLAIN"), url=CHNL_LNK)  # Link to the main channel
        ],
        [
            InlineKeyboardButton(get_btn(lang, "BTN_DONATE_US"), callback_data='donation') #,  # Callback to trigger donation action
          #  InlineKeyboardButton('Contact Support', url="http://example.com/contact")  # Example of a second button in this row
        ]
    ]
    return InlineKeyboardMarkup(buttons)
