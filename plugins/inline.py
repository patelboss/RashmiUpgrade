import logging
from pyrogram import Client, emoji, filters
from pyrogram.errors.exceptions.bad_request_400 import QueryIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultCachedDocument, InlineQuery
from database.ia_filterdb import get_search_results
from utils import is_subscribed, get_size, clean_file_name
from info import CACHE_TIME, AUTH_CHANNEL, GRP_LNK, CHNL_LNK
from database.connections_mdb import active_connection
from variables import CUSTOM_FILE_CAPTION
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cache_time = 0 if AUTH_CHANNEL else CACHE_TIME

@Client.on_inline_query()
async def answer(bot, query):
    """Show search results for the given inline query."""
#   logger.info(f"Received inline query from user {query.from_user.id}: {query.query}")

    chat_id = await active_connection(str(query.from_user.id))

    # Check if the user is subscribed to the required channel
    if AUTH_CHANNEL and not await is_subscribed(bot, query):
#        logger.warning(f"User {query.from_user.id} is not subscribed to the required channel.")
        await query.answer(
            results=[],
            cache_time=0,
            switch_pm_text='You must subscribe to use this bot',
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
#        logger.info(f"User {query.from_user.id} provided an empty query.")
        await query.answer(
            results=[],
            cache_time=cache_time,
            switch_pm_text="📂 Type any movie or web series name to search.",
            switch_pm_parameter="default"
        )
        return

    offset = int(query.offset or 0)

    reply_markup = get_reply_markup(query=string)

    try:
        # Ensure correct argument mapping for get_search_results
        files, next_offset, total_results = await get_search_results(
            query=string,
            file_type=file_type,
            max_results=10,
            offset=offset
        )
#        logger.info(f"Search results retrieved for query '{string}' by user {query.from_user.id}.")
    except Exception as e:
        logger.error(f"Error while fetching search results for query '{string}': {e}")
        await query.answer(
            results=[],
            cache_time=cache_time,
            switch_pm_text="Error occurred",
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
        switch_pm_text = f"{emoji.FILE_FOLDER} Results - {total_results}"
        if string:
            switch_pm_text += f" for '{string}'"
        try:
            await query.answer(
                results=results,
                is_personal=True,
                cache_time=cache_time,
                switch_pm_text=switch_pm_text,
                switch_pm_parameter="start",
                next_offset=str(next_offset)
            )
#            logger.info(f"Search results sent for query '{string}' by user {query.from_user.id}.")
        except QueryIdInvalid:
            logger.warning(f"QueryIdInvalid error for user {query.from_user.id}.")
    else:
        switch_pm_text = f"{emoji.CROSS_MARK} No results"
        if string:
            switch_pm_text += f" for '{string}'"

        await query.answer(
            results=[],
            is_personal=True,
            cache_time=cache_time,
            switch_pm_text=switch_pm_text,
            switch_pm_parameter="no_results"
        )
#       logger.info(f"No results found for query '{string}' by user {query.from_user.id}.")

def get_reply_markup1(query):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)
        ]
    ]
    return InlineKeyboardMarkup(buttons)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def get_reply_markup(query):
    """Generate reply markup for inline results."""
    buttons = [
        [
            InlineKeyboardButton('Search again', switch_inline_query_current_chat=query)  # Existing button
        ],
        [
            InlineKeyboardButton('Search Group', url=GRP_LNK),  # Link to the search group
            InlineKeyboardButton('Main Channel', url=CHNL_LNK)  # Link to the main channel
        ],
        [
            InlineKeyboardButton('Donate Us', callback_data='donation') #,  # Callback to trigger donation action
          #  InlineKeyboardButton('Contact Support', url="http://example.com/contact")  # Example of a second button in this row
        ]
    ]
    return InlineKeyboardMarkup(buttons)
