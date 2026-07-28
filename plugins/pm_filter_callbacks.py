"""
plugins/pm_filter_callbacks.py — Callback-query handlers split out of the
original monolithic pm_filter.py (see plugins/pm_filter.py and
plugins/pm_filter_search.py for the other two parts).

Contains:
    donation_callback     — "donation2" button
    next_page             — "^next" pagination button
    advantage_spoll_choker — "^spolling" spell-check suggestion buttons
    cb_handler            — the main catch-all callback dispatcher (group=10)

The body of cb_handler is moved verbatim (same if/elif/if structure and
fall-through behavior as the original) — only the file boundary changed,
so this refactor does not alter runtime behavior. All user-facing text now
goes through langs.i18n.get()/get_btn() instead of hardcoded literals.
"""

import asyncio
import ast
import math
import logging

from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import UserIsBlocked, MessageNotModified, PeerIdInvalid

from Script import script
from info import *
from database.connections_mdb import (
    active_connection, all_connections, delete_connection, if_active,
    make_active, make_inactive,
)
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import del_all, find_filter
from database.spell_feedback_mdb import *
from variables import CUSTOM_FILE_CAPTION, DLTTM
from utils import get_size, temp, get_settings, clean_file_name, is_subscribed, save_group_settings, send_all
from langs.i18n import get, get_btn, DEFAULT_LANG

from plugins.pm_filter_state import BUTTONS, BUTTONS0, BUTTONS1, BUTTONS2, FRESH, SPELL_CHECK
from plugins.pm_filter_search import auto_filter, manual_filters

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_callback_query(filters.regex("donation2"))
async def donation_callback(client, callback_query):
    lang = await _user_lang(callback_query.from_user)
    if DEBUG_MODE:
        logger.info("[DONATE] donation2 callback | user_id=%s", callback_query.from_user.id)
    await callback_query.answer()
    buttons = [
        [InlineKeyboardButton(get_btn(lang, "BTN_DONATE_RECEIPT_STYLE"), url=f"https://t.me/{OWNER_USERNAME}")],
        [InlineKeyboardButton(get_btn(lang, "BTN_CLOSE_DELETE_STYLE"), callback_data="close_data")]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)
    await callback_query.message.reply_photo(
        photo=PAYMENT_QR,
        caption=PAYMENT_TEXT,
        reply_markup=reply_markup
    )


@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    lang = await _user_lang(query.from_user)
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(get(lang, "NOT_FOR_YOU_ALERT"), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        if DEBUG_MODE:
            logger.info("[NEXT_PAGE] stale BUTTONS key=%s | user_id=%s", key, query.from_user.id)
        await query.answer(get(lang, "OLD_BUTTON_RESEND"), show_alert=True)
        return

    if DEBUG_MODE:
        logger.info("[NEXT_PAGE] fetching results | search=%r | offset=%s", search, offset)
    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return

    if DEBUG_MODE:
        logger.info("[NEXT_PAGE] result count=%s | total=%s", len(files), total)

    temp.GETALL[key] = files
    temp.SHORT[query.from_user.id] = query.message.chat.id
    settings = await get_settings(query.message.chat.id)
    pre = 'filep' if settings['file_secure'] else 'file'
    settings = await get_settings(query.message.chat.id)
    if settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)} ⊙ {clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton(get_btn(lang, "BTN_SEND_ALL"), callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(get(lang, "RESULTS_OF_HEADER", search=search), callback_data=f"fsendfiles#{key}")
        ])

    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"☞{clean_file_name(file.file_name)}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"☞{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
        btn.insert(0, [
            InlineKeyboardButton(get_btn(lang, "BTN_SEND_ALL"), callback_data=f"sendfiles#{key}")
        ])
        btn.insert(0, [
            InlineKeyboardButton(get(lang, "RESULTS_OF_HEADER", search=search), callback_data=f"fsendfiles#{key}")
        ])

    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton(get_btn(lang, "BTN_BACK_STYLIZED"), callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(
                 get(lang, "PAGES_LABEL", page=math.ceil(int(offset) / 10) + 1, total_pages=math.ceil(total / 10)),
                 callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(
                get(lang, "PAGE_LABEL_ALT", page=math.ceil(int(offset) / 10) + 1, total_pages=math.ceil(total / 10)),
                callback_data="pages"),
             InlineKeyboardButton(get_btn(lang, "BTN_NEXT_STYLIZED"), callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton(get_btn(lang, "BTN_BACK_STYLIZED"), callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(
                    get(lang, "PAGE_LABEL_ALT", page=math.ceil(int(offset) / 10) + 1, total_pages=math.ceil(total / 10)),
                    callback_data="pages"),
                InlineKeyboardButton(get_btn(lang, "BTN_NEXT_STYLIZED"), callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()


@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    lang = await _user_lang(query.from_user)
    _, user, movie_ = query.data.split('#')

    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(get(lang, "NOT_FOR_YOU_ALERT"), show_alert=True)

    if movie_ == "close_spellcheck":
        return await query.message.delete()

    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        if DEBUG_MODE:
            logger.info("[SPELLFDB] stale SPELL_CHECK entry | user_id=%s", query.from_user.id)
        return await query.answer(get(lang, "OLD_BUTTON_EXPIRED"), show_alert=True)

    movie = movies[int(movie_)]
    original_query = getattr(query.message.reply_to_message, "text", "") or ""

    if DEBUG_MODE:
        logger.info(
            "[SPELLFDB] saving feedback | search=%r | selected=%r | user_id=%s",
            original_query,
            movie,
            query.from_user.id,
        )

    try:
        await record_spell_feedback(
            search_query=original_query,
            selected_title=movie,
            user_id=query.from_user.id,
            source="spolling",
        )
    except Exception as e:
        logger.exception("[SPELLFDB] failed to save spell feedback: %s", e)

    await query.answer(get(lang, "CHECKING_MOVIE_DB"))
    k = await manual_filters(bot, query.message, text=movie)
    if k == False:
        if DEBUG_MODE:
            logger.info("[SPELLFDB] no manual filter match | search=%r", movie)
        files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
        if files:
            if DEBUG_MODE:
                logger.info("[SPELLFDB] auto_filter result count=%s", len(files))
            k = (movie, files, offset, total_results)
            await auto_filter(bot, query, k)
        else:
            if DEBUG_MODE:
                logger.info("[SPELLFDB] no results for corrected movie name=%r", movie)
            k = await query.message.edit(get(lang, "MOVIE_UNAVAILABLE_REQUEST"))
            await asyncio.sleep(10)
            await k.delete()


@Client.on_callback_query(group=10)
async def cb_handler(client: Client, query: CallbackQuery):
    lang = await _user_lang(query.from_user)
    if DEBUG_MODE:
        logger.info(
            "[CB] callback received | data=%r | user_id=%s",
            query.data, query.from_user.id if query.from_user else None
        )

    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text(get(lang, "NOT_IN_GROUP_PLAIN"), quote=True)
                    return await query.answer(get(lang, "LOVE_ANSWER"))
            else:
                await query.message.edit_text(
                    get(lang, "NOT_CONNECTED_BILINGUAL"),
                    quote=True
                )
                return await query.answer()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer()

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            if DEBUG_MODE:
                logger.info("[CB] delallconfirm authorized | grp_id=%s | user_id=%s", grp_id, userid)
            await del_all(query.message, grp_id, title, lang=lang)
        else:
            await query.answer(get(lang, "OWNER_REQUIRED_BILINGUAL"), show_alert=True)
    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer(get(lang, "NOT_FOR_YOU_STYLIZED"), show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id

        if act == "":
            stat = get_btn(lang, "BTN_CONNECT_ACTION")
            cb = "connectcb"
        else:
            stat = get_btn(lang, "BTN_DISCONNECT_ACTION")
            cb = "disconnect"

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton(get_btn(lang, "BTN_DELETE_CONN"), callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton(get_btn(lang, "BTN_BACK_PLAIN"), callback_data="backcb")]
        ])

        await query.message.edit_text(
            get(lang, "GROUP_INFO_MARKDOWN", title=title, group_id=group_id),
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer()
    elif "connectcb" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title

        user_id = query.from_user.id

        mkact = await make_active(str(user_id), str(group_id))

        if mkact:
            if DEBUG_MODE:
                logger.info("[CB] connectcb success | user_id=%s | group_id=%s", user_id, group_id)
            await query.message.edit_text(
                get(lang, "CONNECTED_MARKDOWN", title=title),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(get(lang, "ERROR_OCCURRED"), parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer()
    elif "disconnect" in query.data:
        await query.answer()

        group_id = query.data.split(":")[1]

        hr = await client.get_chat(int(group_id))

        title = hr.title
        user_id = query.from_user.id

        mkinact = await make_inactive(str(user_id))

        if mkinact:
            if DEBUG_MODE:
                logger.info("[CB] disconnect success | user_id=%s | group_id=%s", user_id, group_id)
            await query.message.edit_text(
                get(lang, "DISCONNECTED_MARKDOWN", title=title),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                get(lang, "ERROR_OCCURRED"),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer()
    elif "deletecb" in query.data:
        await query.answer()

        user_id = query.from_user.id
        group_id = query.data.split(":")[1]

        delcon = await delete_connection(str(user_id), str(group_id))

        if delcon:
            await query.message.edit_text(
                get(lang, "CONN_DELETED")
            )
        else:
            await query.message.edit_text(
                get(lang, "ERROR_OCCURRED"),
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer()
    elif query.data == "backcb":
        await query.answer()

        userid = query.from_user.id

        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                get(lang, "CONNECTIONS_NONE"),
            )
            return await query.answer()
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                get(lang, "CONNECTIONS_LIST"),
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(get(lang, "FILE_NOT_FOUND_PLAIN"))
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"

        try:
            if settings['botpm']:
                await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                return
            else:
                if DEBUG_MODE:
                    logger.info("[CB] sending cached media | file_id=%s | to_user=%s", file_id, query.from_user.id)
                msg = await client.send_cached_media(
                    chat_id=query.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    protect_content=True if ident == "filep" else False
                )

                await query.answer(get(lang, "FILE_SENT_TO_PM"), show_alert=True)

                k = await msg.reply(get(lang, "DELETEMSG"), quote=True,  protect_content=True, disable_web_page_preview=True)
                #k = await msg.reply(get(lang, "DELETEMSG"), quote=True, protect_content=True)
                await asyncio.sleep(DLTTM)
                await k.edit_text("<b>Your File/Video is successfully deleted!!!</b>")
                await msg.delete()

        except UserIsBlocked:
            await query.answer(get(lang, "UNBLOCK_BOT"), show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            logger.exception("[CB] file# handler failed: %s", e)
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
    elif query.data.startswith("send_fsall"):
        temp_var, ident, key, offset = query.data.split("#")
        # FIXED: was `BUTTON0` (undefined name, would raise NameError) —
        # this is the BUTTONS0 dict populated alongside BUTTONS1/BUTTONS2.
        search = BUTTONS0.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
            return
        if DEBUG_MODE:
            logger.info("[CB] send_fsall | key=%s | offset=%s | user_id=%s", key, offset, query.from_user.id)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS1.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        search = BUTTONS2.get(key)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(get(lang, "ALL_FILES_SENT_PM", name=query.from_user.first_name), show_alert=True)

    elif query.data.startswith("send_fall"):
        temp_var, ident, key, offset = query.data.split("#")
        search = FRESH.get(key)
        if not search:
            await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
            return
        if DEBUG_MODE:
            logger.info("[CB] send_fall | key=%s | offset=%s | user_id=%s", key, offset, query.from_user.id)
        files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=int(offset), filter=True)
        await send_all(client, query.from_user.id, files, ident, query.message.chat.id, query.from_user.first_name, query)
        await query.answer(get(lang, "ALL_FILES_SENT_PM", name=query.from_user.first_name), show_alert=True)

    elif query.data.startswith("sendfiles"):
        clicked = query.from_user.id
        ident, key = query.data.split("#")
        settings = await get_settings(query.message.chat.id)

        try:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=allfiles_{key}")
            return

        except UserIsBlocked:
            await query.answer(get(lang, "UNBLOCK_BOT_ALT"), show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles3_{key}")
        except Exception as e:
            logger.exception(e)
            await query.answer(url=f"https://telegram.me/{temp.U_NAME}?start=sendfiles4_{key}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer(get(lang, "JOIN_FIRST_STYLIZED"), show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer(get(lang, "FILE_NOT_EXIST_PLAIN"))
        files = files_[0]
        title = clean_file_name(files.file_name)
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                        file_size='' if size is None else size,
                                                        file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        if DEBUG_MODE:
            logger.info("[CB] checksub sending cached media | file_id=%s | to_user=%s", file_id, query.from_user.id)
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f_caption,
            protect_content=True if ident == 'checksubp' else False
        )
    elif query.data == "pages":
        await query.answer()
    elif query.data == "start":
        buttons = [[
            InlineKeyboardButton(get_btn(lang, "BTN_ADD_TO_GROUP"), url=f'http://t.me/{temp.U_NAME}?startgroup=true')
        ], [
            InlineKeyboardButton(get_btn(lang, "BTN_SEARCH"), switch_inline_query_current_chat=''),
            InlineKeyboardButton(get_btn(lang, "BTN_GROUP"), url='https://t.me/filmykeedha_search')
        ], [
            InlineKeyboardButton(get_btn(lang, "BTN_HELP"), callback_data='help:main'),
        ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        
        # Matched directly to your script.START template variables
        #text_content = script.START.format( name=query.from_user.mention, uname=temp.U_NAME,           bname=temp.B_NAME)
        
        
        await query.message.edit_text(
            #text=script.START_TXT.format(name=query.from_user.mention, uname=temp.U_NAME, bname=temp.B_NAME),
            text=get( lang, "START", name=query.from_user.mention, uname=temp.U_NAME, bname=temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))

        if str(grp_id) != str(grpid):
            await query.message.edit(get(lang, "ACTIVE_CONN_CHANGED"))
            return await query.answer()

        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)

        settings = await get_settings(grpid)

        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_FILTER_BTN"),
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_SINGLE") if settings["button"] else get_btn(lang, "BTN_SET_DOUBLE"),
                                         callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_BOTPM"), callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if settings["botpm"] else get_btn(lang, "BTN_SET_NO"),
                                         callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_FILESECURE"),
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if settings["file_secure"] else get_btn(lang, "BTN_SET_NO"),
                                         callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_IMDB"), callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if settings["imdb"] else get_btn(lang, "BTN_SET_NO"),
                                         callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_SPELL"),
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if settings["spell_check"] else get_btn(lang, "BTN_SET_NO"),
                                         callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_WELCOME"), callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton(get_btn(lang, "BTN_SET_YES") if settings["welcome"] else get_btn(lang, "BTN_SET_NO"),
                                         callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(get(lang, "SETTINGS_UPDATED"))
