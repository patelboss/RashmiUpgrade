"""
plugins/help.py — Unified /help command with 3-level inline navigation.

Flow:
  /help  →  Main menu (category buttons)
         →  User taps category  →  message edits to show commands
         →  User taps a command  →  query.answer() popup with usage guide
         →  Back / Main Menu buttons navigate without new messages

Callback data scheme:
  help:main                — show main category list
  help:cat:<category>      — show commands in a category
  help:guide:<guide_key>   — show popup guide for a specific command
  help:lang                — jump to language selector
"""

import logging
from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from pyrogram.enums import ParseMode
from plugins.Extra.Cscript import TEXTS
from info import ADMINS
from database.users_chats_db import db
from langs.i18n import get, get_btn, LANGUAGE_MENU, LANGUAGES
from debug import dlog

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Category → i18n content key + command list for guide buttons
# ─────────────────────────────────────────────────────────────────────────────
HELP_CATEGORIES = [
    {
        "key":       "search",
        "btn_key":   "BTN_CAT_SEARCH",
        "content":   "HELP_CAT_SEARCH",
        "guides": [
            ("📂 /index",    "GUIDE_INDEX_TIP"),
            ("🔍 Search",    "GUIDE_SEARCH_TIP"),
        ],
        "admin_only": False,
    },
    {
        "key":       "filters",
        "btn_key":   "BTN_CAT_FILTERS",
        "content":   "HELP_CAT_FILTERS",
        "guides": [
            ("➕ /addfilter", "GUIDE_FILTER_TIP"),
        ],
        "admin_only": False,
    },
    {
        "key":       "connect",
        "btn_key":   "BTN_CAT_CONNECT",
        "content":   "HELP_CAT_CONNECT",
        "guides": [
            ("🔗 /connect", "GUIDE_CONNECT_TIP"),
        ],
        "admin_only": False,
    },
    {
        "key":       "extra",
        "btn_key":   "BTN_CAT_EXTRA",
        "content":   "HELP_CAT_EXTRA",
        "guides": [],
        "admin_only": False,
    },
    {
        "key":       "fsub",
        "btn_key":   "BTN_CAT_FSUB",
        "content":   "HELP_CAT_FSUB",
        "guides": [],
        "admin_only": False,
    },
    {
        "key":       "admin",
        "btn_key":   "BTN_CAT_ADMIN",
        "content":   "HELP_CAT_ADMIN",
        "guides": [],
        "admin_only": True,   # only shown to ADMINS
    },
]

# ─────────────────────────────────────────────────────────────────────────────
# Keyboard builders
# ─────────────────────────────────────────────────────────────────────────────

def _main_menu_kb(lang: str, user_id: int) -> InlineKeyboardMarkup:
    """Build the category selection keyboard for the main help menu."""
    rows = []
    row = []
    for cat in HELP_CATEGORIES:
        if cat["admin_only"] and str(user_id) not in [str(a) for a in ADMINS]:
            continue
        btn = InlineKeyboardButton(
            get_btn(lang, cat["btn_key"]),
            callback_data=f"help:cat:{cat['key']}"
        )
        row.append(btn)
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    # Language selector button in last row
    rows.append([
        InlineKeyboardButton(get_btn(lang, "BTN_LANGUAGE"), callback_data="help:lang"),
        InlineKeyboardButton(get_btn(lang, "BTN_CLOSE"),    callback_data="close_data"),
    ])
    return InlineKeyboardMarkup(rows)


def _category_kb(lang: str, cat: dict) -> InlineKeyboardMarkup:
    """Build keyboard for a category page (guide buttons + back navigation)."""
    rows = []
    for label, guide_key in cat.get("guides", []):
        rows.append([
            InlineKeyboardButton(label, callback_data=f"help:guide:{guide_key}")
        ])
    rows.append([
        InlineKeyboardButton(get_btn(lang, "BTN_BACK"),      callback_data="help:main"),
        InlineKeyboardButton(get_btn(lang, "BTN_MAIN_MENU"), callback_data="help:main"),
    ])
    return InlineKeyboardMarkup(rows)


def _lang_kb() -> InlineKeyboardMarkup:
    """Build the language picker keyboard."""
    rows = []
    for entry in LANGUAGE_MENU:
        rows.append([
            InlineKeyboardButton(
                f"{entry['flag']} {entry['name']}",
                callback_data=f"setlang:{entry['code']}"
            )
        ])
    rows.append([
        InlineKeyboardButton("◀️ Back", callback_data="help:main")
    ])
    return InlineKeyboardMarkup(rows)


# ─────────────────────────────────────────────────────────────────────────────
# /help command handler
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("help") & filters.incoming)
async def help_command(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    lang = await db.get_user_lang(user_id) if user_id else "en"
    dlog("HELP_OPEN", user_id=user_id)

    await message.reply_text(
        get(lang, "HELP_MAIN"),
        reply_markup=_main_menu_kb(lang, user_id),
        parse_mode=ParseMode.HTML
    )


# ─────────────────────────────────────────────────────────────────────────────
# help:* callback router
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^help:"))
async def help_callback(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    lang = await db.get_user_lang(user_id)
    data = query.data  # e.g. "help:main", "help:cat:search", "help:guide:GUIDE_INDEX_TIP"

    dlog("HELP_CB", user_id=user_id, extra={"data": data})

    # ── Main menu ─────────────────────────────────────────────────────────────
    if data == "help:main":
        await query.answer(get(lang, "GUIDE_HELP_OPEN"), show_alert=False)
        await query.message.edit_text(
            get(lang, "HELP_MAIN"),
            reply_markup=_main_menu_kb(lang, user_id),
            parse_mode=ParseMode.HTML
        )
        return

    # ── Language picker ───────────────────────────────────────────────────────
    if data == "help:lang":
        from langs.i18n import get as i18n_get
        await query.message.edit_text(
            i18n_get(lang, "LANG_SELECT_MSG"),
            reply_markup=_lang_kb(),
            parse_mode=ParseMode.HTML
        )
        return

    # ── Category page ─────────────────────────────────────────────────────────
    if data.startswith("help:cat:"):
        cat_key = data.split("help:cat:", 1)[1]
        cat = next((c for c in HELP_CATEGORIES if c["key"] == cat_key), None)
        if not cat:
            await query.answer("Unknown category.", show_alert=True)
            return
        # Admin-only guard
        if cat["admin_only"] and str(user_id) not in [str(a) for a in ADMINS]:
            await query.answer("⛔ Admin only.", show_alert=True)
            return
        await query.message.edit_text(
            get(lang, cat["content"]),
            reply_markup=_category_kb(lang, cat),
            parse_mode=ParseMode.HTML
        )
        return

    # ── Guide popup ───────────────────────────────────────────────────────────
    if data.startswith("help:guide:"):
        guide_key = data.split("help:guide:", 1)[1]
        tip = get(lang, guide_key)
        await query.answer(tip, show_alert=True)
        return

    await query.answer()


# ─────────────────────────────────────────────────────────────────────────────
# Language set callback  (setlang:<code>)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex(r"^setlang:"))
async def set_language(client: Client, query: CallbackQuery):
    user_id = query.from_user.id
    lang_code = query.data.split("setlang:", 1)[1]

    if lang_code not in LANGUAGES:
        await query.answer("Unknown language.", show_alert=True)
        return

    await db.set_user_lang(user_id, lang_code)
    dlog("LANG_SET", user_id=user_id, extra={"lang": lang_code})

    lang_name = next(
        (e["flag"] + " " + e["name"] for e in LANGUAGE_MENU if e["code"] == lang_code),
        lang_code
    )
    await query.answer(get(lang_code, "LANG_SET_OK", lang_name=lang_name), show_alert=False)

    # Refresh main menu in the new language
    await query.message.edit_text(
        get(lang_code, "HELP_MAIN"),
        reply_markup=_main_menu_kb(lang_code, user_id),
        parse_mode=ParseMode.HTML
    )


# ─────────────────────────────────────────────────────────────────────────────
# /language command  (shortcut to picker without opening full help)
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("language") & filters.incoming)
async def language_command(client: Client, message: Message):
    user_id = message.from_user.id if message.from_user else None
    lang = await db.get_user_lang(user_id) if user_id else "en"
    await message.reply_text(
        get(lang, "LANG_SELECT_MSG"),
        reply_markup=_lang_kb(),
        parse_mode=ParseMode.HTML
    )
# Command to show help for /chelp
@Client.on_message(filters.command("chelp"))
async def chelp(client, message: Message):
    # Check if the user added "m" after the command
    command_parts = message.text.split()
    use_html = len(command_parts) > 1 and command_parts[1].lower() == "m"

    # Send the sticker first
    sticker_id = get_random_sticker()
    m = await message.reply_sticker(sticker_id, 'CAACAgIAAxkBAAEWouFnYZdWgByiIdBga-j3bXRMK7sL3QACYgADTlzSKU6iwxhIxCtxHgQ')  # Default sticker ID if missing
    await asyncio.sleep(2)  # Wait for 2 seconds
    await m.delete()  # Delete the sticker message

    if use_html:
        # Send the help text in HTML format
        await message.reply(TEXTS.get("HELP_TEXT", "<b>Help text not available.</b>"), parse_mode=ParseMode.HTML)
    else:
        # Send the available text methods in Markdown format
        await message.reply(TEXTS.get("AVAILABLE_TEXT_METHODS", "**Available methods not found.**"), parse_mode=ParseMode.MARKDOWN)
