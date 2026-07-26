"""
langs/i18n.py — Centralised text & button label registry for RashmiUpgrade bot.

HOW TO USE
----------
from langs.i18n import get, get_btn

# Fetch a message string (with optional format kwargs):
text = get(lang, "START", name=user.mention, uname=temp.U_NAME, bname=temp.B_NAME)

# Fetch a button label:
label = get_btn(lang, "BTN_HELP")

HOW TO ADD A NEW LANGUAGE
--------------------------
1. Create a new class that inherits from EN (automatic English fallback for untranslated keys).
2. Override only the strings you have translated.
3. Register it in the LANGUAGES dict at the bottom with its IETF language code.
4. Add its display entry to LANGUAGE_MENU list.

BUTTON KEY NAMING CONVENTION
-----------------------------
All button label keys start with BTN_ so translators know they are button text
(short, must fit on a Telegram button — keep under ~25 chars).
Each BTN_ key has a comment explaining WHERE that button appears in the bot.
"""

# ─────────────────────────────────────────────────────────────────────────────
# ENGLISH  (base / fallback for every other language)
# ─────────────────────────────────────────────────────────────────────────────
class EN:

    # ── /start ──────────────────────────────────────────────────────────────
    START = (
        "<b><blockquote>👋 Hello <i>{name}</i>,\n"
        "✨ My name is <a href='https://t.me/{uname}'><b>{bname}</b></a> ✨</blockquote>\n\n"
        "<b><i>⚡ I am your ultimate File Sharing Bot powered by "
        "<a href='https://t.me/filmykeedha'>@FilmyKeedha</a> ⚡</i></b>\n\n"
        "📚 With the largest media database on Telegram, we've proudly served users "
        "since 2021 and are committed to staying completely <b>FREE</b> in the future!</b>"
    )

    # Shown when bot is added to a group
    START_GROUP = (
        "<b><blockquote>👋 Hello <i>{name}</i>!</blockquote>\n\n"
        "I'm <a href='https://t.me/{uname}'><b>{bname}</b></a> — your File Sharing Bot!\n"
        "Use me in private to find and get files.</b>"
    )

    # ── Subscription gate ────────────────────────────────────────────────────
    FORCE_SUB_MSG = (
        "<b>⚠️ Please join my Updates Channel to use this bot!</b>"
    )

    # ── Verification ─────────────────────────────────────────────────────────
    VERIFY_REQUIRED = (
        "<b>🔐 You are not verified!\nKindly verify to continue.</b>"
    )
    VERIFY_SUCCESS = (
        "<b>🎉 Hey {name}, you are successfully verified!\n"
        "You now have unlimited access for all movies till today midnight.\n\n"
        "Enjoy! 🤩</b>"
    )
    VERIFY_INVALID_LINK = "<b>❌ Invalid or Expired verification link!</b>"

    # ── File delivery ────────────────────────────────────────────────────────
    FILE_WAIT       = "<b>⏳ Please wait...</b>"
    FILE_NOT_FOUND  = "<b>❌ No such file exists.</b>"
    FILE_DELETED_OK = "<b>✅ Your file/video has been successfully deleted!</b>"
    ALL_DELETED_OK  = "<b>✅ All your files/videos have been successfully deleted!</b>"

    DELETEMSG = (
        "\n<pre><b>⏳ Deleting in {minutes} Minutes 🗑️</b></pre>\n"
        "<pre>To save your files, do one of the following 👇🏻\n"
        "├── 📤 Forward to your friends\n"
        "├── 📲 Forward to saved messages\n"
        "└── 👥 Forward to our group</pre>\n"
        "<a href='https://t.me/Filmykeedha/306'>👉🏻 Join our Group 👈🏻</a>"
    )

    # ── Batch delivery ───────────────────────────────────────────────────────
    BATCH_NOT_FOUND     = "<b>❌ Invalid or expired batch link.</b>"
    BATCH_NO_FILES      = "<b>⚠️ No files found in this batch.</b>"
    BATCH_INVALID_DATA  = "<b>⚠️ Invalid file data in this batch.</b>"
    BATCH_INFO          = (
        "<b>📦 Batch:</b> {name}\n"
        "<b>📝 Note:</b> {msg}\n"
        "Processing <b>{count}</b> files..."
    )
    BATCH_PROCESSING = "<b>⏳ Please wait, processing files...</b>"

    # ── Admin commands ───────────────────────────────────────────────────────
    BOT_RESTARTING  = "<b>🔄 Processes stopped. Bot is restarting...</b>"
    BOT_RESTARTED   = "<b>✅ Bot is restarted. Now you can use me.</b>"
    PROCESSING      = "<b>⏳ Processing...</b>"
    REPLY_TO_FILE   = "<b>↩️ Reply to a file with /delete to remove it.</b>"
    UNSUPPORTED_FMT = "<b>❌ This file format is not supported.</b>"
    FILE_DEL_DB_OK  = "<b>✅ File successfully deleted from database.</b>"
    FILE_NOT_IN_DB  = "<b>❌ File not found in database.</b>"

    DELETE_ALL_CONFIRM = (
        "<b>⚠️ This will delete ALL indexed files.\n"
        "Do you want to continue?</b>"
    )
    DELETE_ALL_DONE = "<b>✅ Successfully deleted all indexed files.</b>"
    DELETE_THANK    = "♥️ Thank You Filmykeedha ♥️"

    ANON_ADMIN_MSG  = "<b>You are an anonymous admin. Use /connect {chat_id} in PM.</b>"
    NOT_IN_GROUP    = "<b>Make sure I'm present in your group!</b>"
    NOT_CONNECTED   = "<b>I'm not connected to any groups!</b>"

    SETTINGS_TITLE  = "<b>⚙️ Change settings for {title}</b>"
    TEMPLATE_SAVED  = "<b>✅ Template for {title} changed to:\n\n{template}</b>"
    NO_INPUT        = "<b>⚠️ No input provided!</b>"
    INVALID_FORMAT  = "<b>❌ Invalid format!</b>"

    # ── Broadcast ────────────────────────────────────────────────────────────
    BROADCAST_ASK        = "<b>You have 120 seconds to send your broadcast message.</b>"
    BROADCAST_ASK_MSG    = "Send your broadcast message (type or forward)."
    BROADCAST_TIMEOUT    = "<b>⏳ Time's up! Broadcast cancelled.</b>"
    BROADCAST_STARTING   = "<b>📡 Broadcasting your messages...</b>"
    BROADCAST_PROGRESS   = (
        "📡 <b>Broadcast in progress:</b>\n\n"
        "Total: {total}\nDone: {done}\n"
        "✅ Success: {success}\n🚫 Blocked: {blocked}\n"
        "🗑 Deleted: {deleted}\n❌ Failed: {failed}"
    )
    BROADCAST_DONE = (
        "✅ <b>Broadcast Completed!</b>\n\n"
        "⏱ Time: {time}\n\n"
        "Total: {total}\nDone: {done}\n"
        "✅ Success: {success}\n🚫 Blocked: {blocked}\n"
        "🗑 Deleted: {deleted}\n❌ Failed: {failed}"
    )
    BROADCAST_ERROR = "<b>❌ An error occurred during broadcast.</b>"

    # ── Scrub / DB purge ─────────────────────────────────────────────────────
    SCRUB_USAGE = (
        "<b>⚠️ Invalid Format.</b>\n\n"
        "<b>Usage:</b> <code>/scrub [pattern] [size]</code>\n"
        "<b>Example:</b> <code>/scrub *spider-man* &gt;1GB</code>"
    )
    SCRUB_SCANNING  = "<b>🔍 Scanning database... please wait.</b>"
    SCRUB_NOT_FOUND = "<b>❌ No files found matching:</b> <code>{pattern}</code>"
    SCRUB_CONFIRM   = (
        "<b>⚠️ DATABASE PURGE WARNING</b>\n\n"
        "<b>Pattern:</b> <code>{pattern}</code>\n"
        "<b>Size Filter:</b> <code>{size}</code>\n\n"
        "<b>📊 Scan Results:</b>\n"
        " ├ <b>Total Files:</b> {count}\n"
        " ├ <b>Min Size:</b> {min_size}\n"
        " └ <b>Max Size:</b> {max_size}\n\n"
        "<b>📂 Samples:</b>\n{samples}\n\n"
        "<b>Are you absolutely sure? This cannot be undone.</b>"
    )
    SCRUB_CANCELLED = "<b>✅ Purge cancelled. No files were deleted.</b>"
    SCRUB_DONE      = "<b>🗑️ Purge complete!\n\n✅ Deleted: {count} files.</b>"
    SCRUB_EXPIRED   = "This purge request has expired or was already executed."
    SCRUB_ADMIN_ONLY = "This button is strictly for admins."
    SCRUB_ERROR     = "<b>❌ An error occurred: {error}</b>"

    # ── Logs & status ────────────────────────────────────────────────────────
    STATUS_TXT = (
        "★ <b>Total Files:</b> <code>{files}</code>\n"
        "★ <b>Total Users:</b> <code>{users}</code>\n"
        "★ <b>Total Chats:</b> <code>{chats}</code>\n"
        "★ <b>Used Storage:</b> <code>{used}</code> MiB\n"
        "★ <b>Free Storage:</b> <code>{free}</code> MiB"
    )

    LOG_TEXT_G = (
        "#NewGroup\n"
        "Group = {title}(<code>{chat_id}</code>)\n"
        "Total Members = <code>{members}</code>\n"
        "Added By — {added_by}"
    )
    LOG_TEXT_P = (
        "#NewUser\n"
        "ID — <code>{user_id}</code>\n"
        "Name — {name}"
    )

    # ── About / source ───────────────────────────────────────────────────────
    ABOUT_TXT = (
        "✯ <b>Name:</b> ᏒᏗᏕᏂᎷᎥ\n"
        "✯ <b>Group:</b> <a href='https://www.instagram.com/reel/CzDbEApSkZe'>FilmyKeedha_ask</a>\n"
        "✯ <b>Main Channel:</b> <a href='https://t.me/Filmykeedha'>FilmyKeedha</a>\n"
        "✯ <b>Creator:</b> <a href='https://t.me/pankaj_patel_p'>Pankaj 👮🏼❤️</a>\n"
        "✯ <b>Movie Languages:</b> Hindi, English, Tamil & More\n"
        "✯ <b>Build Status:</b> V1.2.0 [ STABLE ]"
    )

    SOURCE_TXT = (
        "<b>NOTE:</b>\n"
        "— ᏒᏗᏕᏂᎷᎥ is an open-source project.\n\n"
        "<b>Devs:</b>\n"
        "— <a href='https://t.me/pankaj_patel_p'>Pankaj 👮🏼❤️</a>"
    )

    # ── Caption on delivered files ────────────────────────────────────────────
    CAPTION = (
        "<pre>✨ Name</pre>\n"
        "🎥 <b>@Filmykeedha</b> <a href='https://t.me/Filmykeedha/306'><b>{file_name}</b></a>\n\n"
        "<pre>✨ Size</pre>\n"
        "📂 <b><a href='https://t.me/Filmykeedha/306'>{file_size}</a></b>\n\n"
        "🔗 <b><a href='https://t.me/Filmykeedha'>Join FilmyKeedha 🔥</a></b>\n"
        "🎁 <b><a href='https://t.me/Filmykeedha/306'>💎 Tap for Exclusive Surprise 💎</a></b>\n\n"
        "<pre>💖 Support Us by Donating 🙏🏻</pre>"
    )

    # ── Group welcome ─────────────────────────────────────────────────────────
    MELCOW_ENG = (
        "<b>👋 Hello {name} 😍\n"
        "Welcome 🤗 to {group}\n\n"
        "Let's get started — Ab Aayega Maza 🥳\n"
        "Tap the button below 👇🏻 to find the active group.</b>"
    )

    # ── Language selection ────────────────────────────────────────────────────
    LANG_SELECT_MSG = (
        "<b>🌐 Please choose your preferred language:\n"
        "भाषा चुनें / زبان چنید</b>"
    )
    LANG_SET_OK = "<b>✅ Language set to: {lang_name}</b>"

    # ── Help menu ─────────────────────────────────────────────────────────────
    HELP_MAIN = (
        "<b>🆘 Help Center</b>\n\n"
        "Choose a category below to see commands and how to use them 👇"
    )

    # Category descriptions shown when user taps a category button
    HELP_CAT_SEARCH = (
        "<b>🔍 Search & Files</b>\n\n"
        "• Tap <b>Search 🔍</b> or just <b>type a movie/series name</b> in a connected group — results appear automatically.\n\n"
        "• <code>/index</code> — reply to the last forwarded message from a channel (or a t.me link) to index that channel's files into the database. Non-admin requests are sent to moderators for approval.\n\n"
        "• <code>/setskip N</code> — skip the first N messages while indexing a channel. (Bot admins only)"
    )
    HELP_CAT_FILTERS = (
        "<b>⚙️ Filters</b>\n\n"
        "Filters make the bot auto-reply to specific keywords in a group.\n\n"
        "• <code>/addfilter keyword</code> (or <code>/addf</code>) — reply to a message to save it as a filter for that keyword.\n\n"
        "• <code>/viewfilters</code> (or <code>/filters</code>) — list every filter saved in the current or connected group.\n\n"
        "• <code>/delelefilter keyword</code> — remove one filter by keyword.\n\n"
        "• <code>/deleteallf</code> — remove every filter in the group. (Owner only)\n\n"
        "<b>NOTE:</b> the bot needs admin rights in the group."
    )
    HELP_CAT_CONNECT = (
        "<b>🔗 Connections</b>\n\n"
        "Connect a group to your PM so you can manage it without spamming the group chat.\n\n"
        "• <code>/connect group_id</code> (in PM) or <code>/connect</code> (inside the group) — link a group to your account.\n\n"
        "• <code>/disconnect</code> — unlink the currently active group.\n\n"
        "• <code>/connections</code> — list your connected groups and switch which one is active.\n\n"
        "<b>NOTE:</b> only group admins can connect."
    )
    HELP_CAT_EXTRA = (
        "<b>🎛️ Extra Features</b>\n\n"
        "• <code>/id</code> — get the ID of the current chat, or a replied user/channel.\n\n"
        "• <code>/info [reply|user_id|username]</code> — show details about a user.\n\n"
        "• <code>/imdb title</code> — search IMDb for a movie or series.\n\n"
        "• <code>/getfileid</code> (reply to media) — get that file's file_id.\n\n"
        "• <code>/alive</code> / <code>/ping</code> — check that the bot is online and measure its response time.\n\n"
        "• <code>/stats</code> — show database and storage stats.\n\n"
        "• <code>/language</code> — change your bot language.\n\n"
        "• <code>/set_template text</code> — set a custom file-caption template for your current/connected group.\n\n"
        "• <code>/donate</code> — see how to support the bot.\n\n"
        "• <code>/webapp</code> — open the media search Web App directly in Telegram.\n\n"
        "• <code>/chelp [m]</code> — alternate help text (add <code>m</code> for HTML mode).\n\n"
        "• <code>/wtry</code> / <code>/wtry2</code> — diagnostic pings confirming the webapp/misc handler files are loaded."
    )
    HELP_CAT_POSTING = (
        "<b>📤 Media Posting</b>\n\n"
        "• <code>/cpost channel_id [m]</code> — reply to a message (media or text) to post it into that channel. Add <code>m</code> to parse the caption as Markdown instead of HTML.\n\n"
        "• <code>/ppost channel_id [m]</code> — same as <code>/cpost</code>, but the copy is protected from forwarding or saving.\n\n"
        "<b>NOTE:</b> you and the bot both need admin rights with post-message permission in that channel."
    )
    HELP_CAT_CONTACT = (
        "<b>📨 Contact & Feedback</b>\n\n"
        "• <code>/feedback</code> (or <code>/report</code>) — reply to a message to send it to the admins as feedback or an issue report.\n\n"
        "• <code>/talk secret_code</code> — reply to a message with a code the admin gave you, to send it directly to them."
    )
    HELP_CAT_FSUB = (
        "<b>🔐 Force Subscribe</b>\n\n"
        "Force Subscribe is configured by the bot owner via the "
        "<code>AUTH_CHANNEL</code> environment variable (not an in-chat command).\n\n"
        "When enabled, users must join the configured channel(s) before they "
        "can open files or use the bot in PM.\n\n"
        "• /id — Get a channel's ID (useful when setting up AUTH_CHANNEL)"
    )
    HELP_CAT_ADMIN = (
        "<b>🛠 Group Admin</b>\n\n"
        "• <code>/leave chat_id</code> — make the bot leave a chat.\n\n"
        "• <code>/disable chat_id [reason]</code> — stop the bot from working in a chat.\n\n"
        "• <code>/enable chat_id</code> — re-enable a previously disabled chat.\n\n"
        "• <code>/invite chat_id</code> — generate an invite link for a chat.\n\n"
        "• <code>/ban user_id [reason]</code> / <code>/unban user_id [reason]</code> — ban or unban a user from using the bot.\n\n"
        "• <code>/users</code> / <code>/chats</code> — export all stored users or chats to a text file."
    )
    HELP_CAT_ADMIN_BOT = (
        "<b>🤖 Bot Admin</b>\n\n"
        "• <code>/settings</code> — open the settings panel for the current/connected group.\n\n"
        "• <code>/restart</code> — restart the bot.\n\n"
        "• <code>/logs</code> — send the recent log file.\n\n"
        "• <code>/channel</code> — list indexed channels/groups.\n\n"
        "• <code>/delete</code> (reply to a file) — delete that file's DB record.\n\n"
        "• <code>/deleteall</code> — start the flow to delete every indexed file.\n\n"
        "• <code>/scrub pattern size</code> — bulk-delete DB entries matching a pattern and size filter.\n\n"
        "• <code>/broadcast</code> / <code>/grp_broadcast</code> — broadcast a message to all users, or all groups.\n\n"
        "• <code>/batch link1 link2 ...</code> (or <code>/pbatch</code>) — build a batch link from multiple file links.\n\n"
        "• <code>/send user_id</code> (reply to your message) — send a copied message to a user without the forward tag.\n\n"
        "• <code>/create_code</code> / <code>/delete_code</code> — create or delete a secret code for <code>/talk</code>."
    )
    HELP_CAT_ADMIN_ENV = (
        "<b>🧩 Environment Config</b>\n\n"
        "• <code>/add_env config key value</code> — add a key/value pair to a named config.\n\n"
        "• <code>/get_envs config</code> — show all variables stored for a config.\n\n"
        "• <code>/all_envs</code> — list every stored config.\n\n"
        "• <code>/update_env config key new_value</code> — update a key in a config.\n\n"
        "• <code>/delete_env config key</code> — delete a key from a config."
    )

    # ── Guide tooltips (query.answer popups) ─────────────────────────────────
    GUIDE_HELP_OPEN       = "💡 Tap a category to explore commands"
    GUIDE_SEARCH_TIP      = "🔍 Type a movie name in your group to search"
    GUIDE_VERIFY_TIP      = "🔐 Join the channel to unlock files 🔓"
    GUIDE_SHORT_QUERY     = "⚠️ Type at least 2 characters to search"
    GUIDE_SAVE_FILE_TIP   = "💾 Forward to Saved Messages to keep your file!"
    GUIDE_INDEX_TIP       = (
        "📂 /index usage:\n\n"
        "Forward the last message from your channel here, "
        "then reply to it with /index. "
        "I'll scan all files automatically."
    )
    GUIDE_FILTER_TIP      = (
        "⚙️ /addfilter usage:\n\n"
        "Reply to any message with /addfilter [keyword] "
        "and I will auto-reply whenever that keyword is sent in the group."
    )
    GUIDE_CONNECT_TIP     = (
        "🔗 /connect usage:\n\n"
        "Send /connect [group_id] in my PM to manage "
        "group filters without going back to the group."
    )

    # ─────────────────────────────────────────────────────────────────────────
    # BUTTON LABELS  (prefix: BTN_)
    # Each has a comment with WHERE it appears.
    # Keep text short — Telegram buttons have limited display width.
    # ─────────────────────────────────────────────────────────────────────────

    # /start private message buttons
    BTN_SHARE          = "➕ Share with Friends ➕"   # Start msg — share bot link
    BTN_SEARCH         = "🔎 Search 🧐"               # Start msg — inline search trigger
    BTN_GROUP          = "✪ GROUP ✪"                  # Start msg — link to main group
    BTN_HELP           = "🙆🏻 Help 🦾"                # Start msg & callbacks
    BTN_ABOUT          = "♥️ About ♥️"                # Start msg & callbacks
    BTN_ADD_TO_GROUP   = "➕ Add Me to Your Group ➕"  # Start msg after subscribe

    # Navigation / general UI
    BTN_BACK           = "◀️ Back"                    # Help menu — back to category list
    BTN_MAIN_MENU      = "🏠 Main Menu"               # Help menu — back to top
    BTN_CLOSE          = "✖️ Close"                   # Generic close / delete message
    BTN_LANGUAGE       = "🌐 Language"                # Settings or start for new users

    # File delivery buttons (appear below every sent file)
    BTN_JOIN_OFFER     = "Join Our Offer Zone 🤑"     # File msg — link to offer channel
    BTN_DONATE         = "💳 Donate"                  # File msg — callback 'donation'
    BTN_GET_AGAIN      = "🔁 Get File Again"          # Post-delete msg

    # Subscription gate buttons
    BTN_JOIN_CHANNEL   = "⚠️ Join Updates Channel ⚠️" # Force-sub gate
    BTN_TRY_AGAIN      = "🔄 Try Again"               # After joining channel

    # Verification buttons
    BTN_VERIFY         = "✅ Verify"                  # Verify gate — opens verify URL
    BTN_VERIFY_HOW     = "❓ How to Verify"           # Verify gate — tutorial link

    # Donate / payment buttons
    BTN_SEND_RECEIPT   = "📧 Send Payment Receipt 🧾" # Donate msg — link to owner PM
    BTN_SUPPORT        = "💬 Support"                 # Generic support link

    # Admin / confirmation buttons
    BTN_YES            = "✅ YES"                     # Confirm deleteall / scrub
    BTN_CANCEL         = "❌ CANCEL"                  # Cancel deleteall / scrub
    BTN_DELETE_ALL_DB  = "🗑️ YES, DELETE ALL"         # Scrub confirm
    BTN_UPDATES        = "🔔 Updates 🤖"             # Group start msg — bot update channel

    # Settings panel buttons (labels for the setting NAME column)
    BTN_SET_FILTER_BTN = "Filter Button"              # Settings — filter button style toggle
    BTN_SET_BOTPM      = "Bot PM"                     # Settings — send files in PM toggle
    BTN_SET_FILESECURE = "File Secure"                # Settings — protect content toggle
    BTN_SET_IMDB       = "IMDB"                       # Settings — show IMDB info toggle
    BTN_SET_SPELL      = "Spell Check"                # Settings — spell check toggle
    BTN_SET_WELCOME    = "Welcome"                    # Settings — new member welcome toggle
    BTN_SET_SINGLE     = "Single"                     # Settings — single button layout
    BTN_SET_DOUBLE     = "Double"                     # Settings — double button layout
    BTN_SET_YES        = "✅ Yes"                     # Settings — toggle value: enabled
    BTN_SET_NO         = "❌ No"                      # Settings — toggle value: disabled

    # ── Connections (plugins/connection.py) ──────────────────────────────────
    ANON_ADMIN_CONNECT   = "You are anonymous admin. Use /connect {chat_id} in PM"
    CONNECT_USAGE        = (
        "<b>Enter in correct format!</b>\n\n"
        "<code>/connect groupid</code>\n\n"
        "<i>Get your Group id by adding this bot to your group and use  <code>/id</code></i>"
    )
    CONNECT_NOT_ADMIN    = "You should be an admin in Given group!"
    CONNECT_INVALID_ID   = "Invalid Group ID!\n\nIf correct, Make sure I'm present in your group!!"
    CONNECT_SUCCESS_PM   = "Successfully connected to **{title}**\nNow manage your group from my pm !"
    CONNECT_SUCCESS_GRP  = "Connected to **{title}** !"
    CONNECT_ALREADY      = "You're already connected to this chat!"
    CONNECT_ADD_ME_ADMIN = "Add me as an admin in group"
    CONNECT_ERROR        = "Some error occurred! Try again later."
    DISCONNECT_HINT_PM   = "Run /connections to view or disconnect from groups!"
    DISCONNECT_SUCCESS   = "Successfully disconnected from this chat"
    DISCONNECT_NOT_FOUND = "This chat isn't connected to me!\nDo /connect to connect."
    CONNECTIONS_NONE     = "There are no active connections!! Connect to some groups first."
    CONNECTIONS_LIST     = "Your connected group details ;\n\n"

    # ── Filters DB (database/filters_mdb.py) ──────────────────────────────────
    FILTERMDB_DELETED        = "'`{text}`' deleted. I'll not respond to that filter anymore."  # delete_filter — success
    FILTERMDB_NOT_FOUND      = "Couldn't find that filter!"  # delete_filter — no match
    FILTERMDB_DELALL_NOTHING = "Nothing to remove in {title}!"  # del_all — no filter collection for this group
    FILTERMDB_DELALL_SUCCESS = "All filters from {title} have been removed."  # del_all — success
    FILTERMDB_DELALL_FAIL    = "Couldn't remove all filters from group!"  # del_all — drop failed

    # ── Misc (plugins/misc.py) ────────────────────────────────────────────────
    NOT_FORWARDED_FROM_CHANNEL = "This message is not forwarded from a channel."
    IMDB_SEARCHING    = "Searching ImDB"
    IMDB_NO_RESULTS   = "No results Found"
    IMDB_FOUND        = "Here is what i found on IMDb"
    IMDB_GIVE_NAME    = "Give me a movie / series Name"
    IMDB_NO_RESULTS_CAPTION = "No Results"
    BTN_CLOSE_LOCK    = "🔐 Close"                     # /info & /id — close button

    # ── Batch link generation (plugins/genlink.py, admin only) ───────────────
    BATCH_USAGE = "Use correct format.\nExample: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`."
    BATCH_INVALID_LINKS = "Invalid link(s) provided."
    BATCH_DIFFERENT_CHATS = "All links must belong to the same chat."
    BATCH_CHAT_ACCESS_ERROR = "Error accessing chat. Ensure the bot has admin access."
    BATCH_ASK_NAME = "Provide a name for this batch."
    BATCH_ASK_OPTIONAL_MSG = "Now, provide an optional message (or type 'pass' to skip)."
    BATCH_PROCESSING = "Processing your batch..."
    BATCH_CREATED = "Batch created successfully!\nBatch Name: {name}\nContains `{count}` files.\nLink: {link}"
    BTN_GET_ALL_FILES = "Get All Files/Episodes"       # Batch channel post — link button

    # Help menu category buttons
    BTN_CAT_SEARCH     = "🔍 Search & Files"          # Help menu — category button
    BTN_CAT_FILTERS    = "⚙️ Filters"                # Help menu — category button
    BTN_CAT_CONNECT    = "🔗 Connections"             # Help menu — category button
    BTN_CAT_EXTRA      = "🎛️ Extra Features"          # Help menu — category button
    BTN_CAT_POSTING    = "📤 Media Posting"           # Help menu — category button
    BTN_CAT_CONTACT    = "📨 Contact & Feedback"      # Help menu — category button
    BTN_CAT_FSUB       = "🔐 Force Subscribe"         # Help menu — category button
    BTN_CAT_ADMIN      = "🛠 Group Admin"             # Help menu — category button (admins only) — was "Admin", split into 3 admin pages
    BTN_CAT_ADMIN_BOT  = "🤖 Bot Admin"               # Help menu — category button (admins only)
    BTN_CAT_ADMIN_ENV  = "🧩 Env Config"              # Help menu — category button (admins only)

    # ── plugins/pm_filter_callbacks.py — callback dispatcher ─────────────────
    NOT_FOR_YOU_ALERT = "This Message is not for you dear. Don't worry you can send new one !"  # next_page / spell-check guard
    OLD_BUTTON_RESEND = "You are using one of my old messages, please send the request again."  # next_page — stale BUTTONS key
    OLD_BUTTON_EXPIRED = "You are clicking on an old button which is expired."  # spell-check — stale SPELL_CHECK key
    CHECKING_MOVIE_DB = "Checking for Movie in database..."  # spell-check tap feedback
    MOVIE_UNAVAILABLE_REQUEST = (
        " 𝐜𝐮𝐫𝐫𝐞𝐧𝐭𝐥𝐲 𝐮𝐧𝐚𝐯𝐚𝐢𝐥𝐚𝐛𝐥𝐞 ! \n𝐰𝐞 𝐚𝐫𝐞 𝐫𝐞𝐚𝐥𝐥𝐲 𝐬𝐨𝐫𝐫𝐲 𝐟𝐨𝐫 𝐢𝐧𝐜𝐨𝐧𝐯𝐞𝐧𝐢𝐞𝐧𝐜𝐞 !\n\n "
        "𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐭 𝐭𝐡𝐢𝐬 𝐌𝐨𝐯𝐢𝐞 𝐨𝐫 𝐖𝐞𝐛𝐬𝐞𝐫𝐢𝐞𝐬 𝐧𝐚𝐦𝐞 𝐢𝐧 #Request 𝐓𝐨𝐩𝐢𝐜 𝐨𝐫 𝐬𝐞𝐧𝐭 𝐮𝐬𝐢𝐧𝐠 "
        "\"#𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐌𝐨𝐯𝐢𝐞 𝐍𝐚𝐦𝐞 & 𝐑𝐞𝐥𝐞𝐚𝐬𝐞 𝐘𝐞𝐚𝐫.\n example: <code> #Request Mirzapur Season 1 2018 </code>\n "
        "𝐨𝐮𝐫 𝐠𝐫𝐞𝐚𝐭 𝐚𝐝𝐦𝐢𝐧𝐬 𝐰𝐢𝐥𝐥 𝐮𝐩𝐥𝐨𝐚𝐝 𝐢𝐭 𝐚𝐬 𝐬𝐨𝐨𝐧 𝐚𝐬 𝐩𝐨𝐬𝐬𝐢𝐛𝐥𝐞 !"
    )
    NOT_IN_GROUP_PLAIN = "Make sure I'm present in your group!!"  # delallconfirm — plain-text variant of NOT_IN_GROUP
    LOVE_ANSWER = "♥️ Love @Filmykeedha ♥️"  # delallconfirm — group-not-found popup
    THANK_YOU_ANSWER = "♥️ 𝚃𝚑𝚊𝚗𝚔 𝚈𝚘𝚞  @Filmykeedha ♥️"  # cb_handler — recurring closing popup across many branches
    NOT_CONNECTED_BILINGUAL = (
        "I'm not connected to any groups!\n"
        "मैं आपके किसी भी ग्रुप से कनेक्ट या जुड़ी नही हूं।\n"
        "Check /connections or connect to any groups"
    )
    OWNER_REQUIRED_BILINGUAL = (
        "You need to be Group Owner or an Auth User to do that!\n"
        "ऐसा करने के लिए आपको समूह का owner या admin होना चाहिए!"
    )
    NOT_FOR_YOU_STYLIZED = "𝐓𝐡𝐚𝐭'𝐬 𝐧𝐨𝐭 𝐟𝐨𝐫 𝐲𝐨𝐮 𝐬𝐨𝐧𝐚!\n यह तुम्हारे लिए नहीं है!"  # delallcancel guard
    GROUP_INFO_MARKDOWN = "Group Name : **{title}**\nGroup ID : `{group_id}`"  # groupcb
    CONNECTED_MARKDOWN = "Connected to **{title}**"  # connectcb
    DISCONNECTED_MARKDOWN = "Disconnected from **{title}**"  # disconnect callback
    ERROR_OCCURRED = "Some error occurred!!"  # connectcb / disconnect / deletecb failure
    CONN_DELETED = "Successfully deleted connection"  # deletecb success
    FILE_NOT_FOUND_PLAIN = "No such file exists."  # file# handler — plain-text variant of FILE_NOT_FOUND
    FILE_NOT_EXIST_PLAIN = "No such file exist."  # checksub handler — plain-text, distinct wording preserved
    FILE_SENT_TO_PM = (
        "𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦 \n"
        "Check @Rashmika_mandanana_bot"
    )
    UNBLOCK_BOT = "𝐔𝐧𝐛𝐥𝐨𝐜𝐤 𝐭𝐡𝐞 𝐁𝐨𝐭!"  # file# handler — UserIsBlocked
    UNBLOCK_BOT_ALT = "Uɴʙʟᴏᴄᴋ ᴛʜᴇ ʙᴏᴛ ᴍᴀʜɴ !"  # sendfiles handler — UserIsBlocked
    ALL_FILES_SENT_PM = "Hey {name}, All files on this page has been sent successfully to your PM !"  # send_fsall/send_fall
    JOIN_FIRST_STYLIZED = "𝐈𝐬𝐤𝐨 𝐉𝐨𝐢𝐧 𝐊𝐚𝐫 𝐏𝐡𝐥𝐞 ✋🏻"  # checksub — force-sub gate
    ACTIVE_CONN_CHANGED = "Your Active Connection Has Been Changed. Go To /settings."  # setgs — stale connection guard
    FETCHING_DB = "Fetching MongoDb DataBase"  # rfrsh tap feedback

    # Button labels used only inside pm_filter_callbacks.py (exact styling preserved)
    BTN_DONATE_RECEIPT_STYLE = "ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ʀᴇᴄᴇɪᴘᴛ 🧾"       # donation_callback
    BTN_CLOSE_DELETE_STYLE   = "⚠️ ᴄʟᴏsᴇ / ᴅᴇʟᴇᴛᴇ ⚠️"           # donation_callback
    BTN_SEND_ALL             = "𝐒𝐞𝐧𝐝 𝐀𝐥𝐥"                       # next_page — send-all-files button
    RESULTS_OF_HEADER        = "Results Of👉🏻 {search} 👈🏻"      # next_page — search results header button
    BTN_BACK_STYLIZED        = "⬅𝐁𝐀𝐂𝐊"                          # next_page & several cb_handler menus
    PAGES_LABEL              = "📃 Pages {page} / {total_pages}"  # next_page — page counter (at start)
    PAGE_LABEL_ALT           = "🗓 {page} / {total_pages}"        # next_page — page counter (mid/end)
    BTN_NEXT_STYLIZED        = "𝐍𝐄𝐗𝐓➡"                          # next_page — next-page button
    BTN_CONNECT_ACTION       = "CONNECT"                          # groupcb — connect action label
    BTN_DISCONNECT_ACTION    = "DISCONNECT"                       # groupcb — disconnect action label
    BTN_DELETE_CONN          = "DELETE"                           # groupcb — delete connection
    BTN_BACK_PLAIN           = "BACK"                             # groupcb — back to connections list
    BTN_MANUAL_FILTER        = "𝗠𝗮𝗻𝘂𝗮𝗹 𝗙𝗶𝗹𝘁𝗲𝗿"                  # help menu
    BTN_AUTO_FILTER          = "𝗔𝘂𝘁𝗼 𝗙𝗶𝗹𝘁𝗲𝗿"                    # help menu
    BTN_CONNECTION_MENU      = "𝗖𝗼𝗻𝗻𝗲𝗰𝘁𝗶𝗼𝗻"                     # help menu
    BTN_EXTRA_MODS           = "𝗘𝘅𝘁𝗿𝗮 𝗠𝗼𝗱𝘀"                     # help menu
    BTN_HOME                 = "🏠 𝗛𝗼𝗺𝗲"                         # help/about menus
    BTN_STATUS               = "🦠 𝗦𝘁𝗮𝘁𝘂𝘀"                       # help menu
    BTN_BUTTONS_LABEL        = "◉⁠𝐁𝐮𝐭𝐭𝐨𝐧𝐬"                       # manuelfilter menu
    BTN_ADMIN_MENU           = "♚ 𝗔𝗱𝗺𝗶𝗻"                         # extra menu
    BTN_REFRESH_ICON         = "↺"                                # stats menu — refresh
    BTN_SOURCE               = "♥️ 𝗦𝗼𝘂𝗿𝗰𝗲"                       # about menu
    BTN_GROUP_LINK_STYLE     = "⁠✪𝙂𝙍𝙊𝙐𝙋✪ "                       # about menu — group link
    BTN_CLOSE_LOCK_STYLE     = "🔐 𝗖𝗹𝗼𝘀𝗲"                        # about menu — close/delete
    BTN_ADD_TO_GROUP_STYLE   = "➕↖️ 𝗔𝗱𝗱 𝗠𝗲 𝗧𝗼 𝗬𝗼𝘂𝗿 𝗚𝗿𝗼𝘂𝗽𝘀\nमुझे GROUP में add करे। ↗️➕"  # start callback
    BTN_SEARCH_STYLE         = "🧞‍♀️ 𝗦𝗲𝗮𝗿𝗰𝗵 🧐"                  # start callback
    BTN_GROUP_STYLE          = "✪𝙂𝙍𝙊𝙐𝙋✪"                         # start callback
    BTN_HELP_STYLE           = "🙆🏻 𝗛𝗲𝗹𝗽 🦾"                     # start callback
    BTN_ABOUT_STYLE          = "♥️ 𝗔𝗯𝗼𝘂𝘁 ♥️"                     # start callback

    # ── plugins/p_ttishow.py — group events & admin moderation commands ──────
    CHAT_NOT_ALLOWED = (
        "<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! "
        "If you want to know more about it, contact support.</b>"
    )
    THANKS_FOR_ADDING = (
        "<b>Thank you for adding me to {title} ❣️\n\n"
        "If you have any questions or doubts about using me, contact support.</b>"
    )
    GIVE_CHAT_ID = "𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐂𝐡𝐚𝐭 𝐈𝐃"  # /leave, /disable — missing chat id argument
    GIVE_CHAT_ID_HI = "𝗚𝗶𝘃𝗲 𝗠𝗲 𝗔 𝗖𝗵𝗮𝘁 𝗜𝗗 मुझे Chat ID दीजिए"  # /enable — bilingual variant
    LEAVE_NOTICE_BILINGUAL = (
        "<b>𝐇𝐞𝐥𝐥𝐨 𝐅𝐫𝐢𝐞𝐧𝐝𝐬, \n𝐌𝐲 𝐀𝐝𝐦𝐢𝐧 𝐇𝐚𝐬 𝐓𝐨𝐥𝐝 𝐌𝐞 𝐓𝐨 𝐋𝐞𝐚𝐯𝐞 𝐅𝐫𝐨𝐦 𝐆𝐫𝐨𝐮𝐩 , "
        "𝐈𝐟 𝐘𝐨𝐮 𝐖𝐚𝐧𝐧𝐚 𝐀𝐝𝐝 𝐌𝐞 𝐀𝐠𝐚𝐢𝐧 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐌𝐲 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝐆𝐫𝐨𝐮𝐩."
        "मेरे एडमिन ने मुझे यहाँ काम करने से रोक दिया है! खतम टाटा बाई बाय! "
        "यदि आप इसके बारे में अधिक जानना चाहते हैं तो 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें</b> "
    )
    LEAVE_NOTICE_WITH_REASON = (
        "<b>𝐇𝐞𝐥𝐥𝐨 𝐅𝐫𝐢𝐞𝐧𝐝𝐬, \n𝐌𝐲 𝐀𝐝𝐦𝐢𝐧 𝐇𝐚𝐬 𝐓𝐨𝐥𝐝 𝐌𝐞 𝐓𝐨 𝐋𝐞𝐚𝐯𝐞 𝐅𝐫𝐨𝐦 𝐆𝐫𝐨𝐮𝐩 , "
        "𝐈𝐟 𝐘𝐨𝐮 𝐖𝐚𝐧𝐧𝐚 𝐀𝐝𝐝 𝐌𝐞 𝐀𝐠𝐚𝐢𝐧 𝐂𝐨𝐧𝐭𝐚𝐜𝐭 𝐌𝐲 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 𝐆𝐫𝐨𝐮𝐩."
        "मेरे एडमिन ने मुझे यहाँ काम करने से रोक दिया है! खतम टाटा बाई बाय! "
        "यदि आप इसके बारे में अधिक जानना चाहते हैं तो 𝗦𝘂𝗽𝗽𝗼𝗿𝘁 पर संपर्क करें</b> \n"
        "𝐑𝐞𝐚𝐬𝐨𝐧 : <code>{reason}</code>"
    )
    LEFT_CHAT_CONFIRM = "left the chat `{chat}`"
    GENERIC_ERROR = "Error - {error}"
    NO_REASON_PROVIDED = "𝐍𝐨 𝐑𝐞𝐚𝐬𝐨𝐧 𝐏𝐫𝐨𝐯𝐢𝐝𝐞𝐝"
    GIVE_VALID_CHAT_ID = "𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐂𝐡𝐚𝐭 𝐈𝐃"
    GIVE_VALID_CHAT_ID_HI = "𝗚𝗶𝘃𝗲 𝗠𝗲 𝗔 𝗩𝗮𝗹𝗶𝗱 𝗖𝗵𝗮𝘁 𝗜𝗗 कृपया मुझे सही chat id दे"
    CHAT_NOT_FOUND_DB = "𝐂𝐡𝐚𝐭 𝐍𝐨𝐭 𝐅𝐨𝐮𝐧𝐝 𝐈𝐧 𝐃𝐁"
    CHAT_ALREADY_DISABLED = "𝗧𝗵𝗶𝘀 𝗰𝗵𝗮𝘁 𝗶𝘀 𝗮𝗹𝗿𝗲𝗮𝗱𝘆 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱:\nReason-<code> {reason} </code>"
    CHAT_DISABLED_OK = "𝗖𝗵𝗮𝘁 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗗𝗶𝘀𝗮𝗯𝗹𝗲𝗱"
    CHAT_NOT_FOUND_DB_HI = "𝗖𝗵𝗮𝘁 𝗡𝗼𝘁 𝗙𝗼𝘂𝗻𝗱 𝗜𝗻 𝗗𝗕 यह 𝗰𝗵𝗮𝘁 हमारे दस्तावेजों में नहीं है !"
    CHAT_NOT_DISABLED_YET = "𝗧𝗵𝗶𝘀 𝗰𝗵𝗮𝘁 𝗶𝘀 𝗻𝗼𝘁 𝘆𝗲𝘁 𝗱𝗶𝘀𝗮𝗯𝗹𝗲𝗱. यह 𝗰𝗵𝗮𝘁 अभी बंद नहीं किया गया"
    CHAT_RE_ENABLED_OK = "Chat Successfully re-enabled"
    FETCHING_STATS = "Fetching stats.."
    GIVE_VALID_CHAT_ID_PLAIN = "𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐕𝐚𝐥𝐢𝐝 𝐂𝐡𝐚𝐭 𝐈𝐃 \nमुझे सही chat id दे"
    GIVE_VALID_CHAT_ID_PLAIN2 = "Give Me A Valid Chat ID  कृपया मुझे सही chat id दे !"
    INVITE_FAILED = (
        "𝐈𝐧𝐯𝐢𝐭𝐞 𝐋𝐢𝐧𝐤 𝐆𝐞𝐧𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐅𝐚𝐢𝐥𝐞𝐝, 𝐈 𝐚𝐦 𝐍𝐨𝐭 𝐇𝐚𝐯𝐢𝐧𝐠 𝐒𝐮𝐟𝐟𝐢𝐜𝐢𝐞𝐧𝐭 𝐑𝐢𝐠𝐡𝐭𝐬. "
        "आमंत्रण लिंक बनाने में असमर्थ, शायद मुझे पर्याप्त अधिकार प्राप्त नहीं है"
    )
    INVITE_LINK_RESULT = "𝐇𝐞𝐫𝐞 𝐈𝐬 𝐘𝐨𝐮𝐫 𝐈𝐧𝐯𝐢𝐭𝐞 𝐋𝐢𝐧𝐤 {link}"
    GIVE_USER_ID = "𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐔𝐬𝐞𝐫 𝐈𝐝 / 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞\nमुझे यूजर id या यूजरनेम दीजिए"
    GIVE_USER_ID_PLAIN = "𝐆𝐢𝐯𝐞 𝐌𝐞 𝐀 𝐔𝐬𝐞𝐫 𝐈𝐝 / 𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞"
    INVALID_USER_NOT_MET = (
        "𝐓𝐡𝐢𝐬 𝐈𝐬 𝐀𝐧 𝐈𝐧𝐯𝐚𝐥𝐢𝐝 𝐔𝐬𝐞𝐫, 𝐌𝐚𝐤𝐞 𝐒𝐮𝐫𝐞 𝐈 𝐇𝐚𝐯𝐞 𝐌𝐞𝐭 𝐇𝐢𝐦 𝐁𝐞𝐟𝐨𝐫𝐞. "
        "यह id गलत है क्योंकि यह उनमें से नही है जिनसे मेने संपर्क किया है।"
    )
    INVALID_USER_MIGHT_BE_CHANNEL = (
        "𝐓𝐡𝐢𝐬 𝐦𝐢𝐠𝐡𝐭 𝐛𝐞 𝐚 𝐜𝐡𝐚𝐧𝐧𝐞𝐥, 𝐦𝐚𝐤𝐞 𝐬𝐮𝐫𝐞 𝐢𝐭𝐬 𝐚 𝐮𝐬𝐞𝐫. "
        "आप पहले प्रमाणित करे की यह एक यूजर है। मुझे लगता है की यह किसी चैनल की id है"
    )
    USER_ALREADY_BANNED = "{mention} 𝐈𝐬 𝐀𝐥𝐫𝐞𝐚𝐝𝐲 𝐁𝐚𝐧𝐧𝐞𝐝 पहले से ही प्रतिबंधित है\n𝐑𝐞𝐚𝐬𝐨𝐧 (कारण): {reason}"
    USER_BANNED_OK = "𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐁𝐚𝐧𝐧𝐞𝐝 ! सुधर जाओ तो फिर आ जाना {mention}"
    USER_NOT_BANNED_YET = "{mention} 𝐢𝐬 𝐧𝐨𝐭 𝐲𝐞𝐭 𝐛𝐚𝐧𝐧𝐞𝐝. अभी बैन नही हुआ"
    USER_UNBANNED_OK = "𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐔𝐧𝐛𝐚𝐧𝐧𝐞𝐝 ! सुबह का भूला अगर शाम को घर आ जाए तो उसे भुला नहीं कहते। {mention}"
    FETCHING_USERS_LIST = "Getting List Of Users"
    USERS_LIST_CAPTION = "List Of Users"
    FETCHING_CHATS_LIST = "Getting List Of Chats"
    CHATS_LIST_CAPTION = "List Of Chats"
    FILE_ID_RESULT = "**File ID:** `{file_id}`\n**File Type:** {file_type}\n**File Size:** {file_size} bytes"
    GETFILEID_NO_MEDIA_REPLY = "Please reply to a media file (video, photo, document, etc.) to get its file ID."
    GETFILEID_NO_MEDIA = "Please reply to a media file or send a media message directly to get its file ID."

    BTN_SUPPORT_PLAIN = "Support"          # save_group — banned-chat / added-to-group notices
    BTN_SEARCH_GROUP = "Search Gʀᴏᴜᴘ"       # save_group — added-to-group notice
    BTN_UPDATES_CHANNEL = "Uᴘᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ"  # save_group — added-to-group / welcome notices
    BTN_SUPPORT_GROUP = "Sᴜᴘᴘᴏʀᴛ Gʀᴏᴜᴘ"      # save_group — welcome notice
    BTN_BOT_OWNER = "Bᴏᴛ Oᴡɴᴇʀ"              # save_group — welcome notice
    BTN_SUPPORT_STYLE = "𝗦𝘂𝗽𝗽𝗼𝗿𝘁"             # /leave, /disable notices

    # ── Filters (plugins/filters.py) ──────────────────────────────────────────
    NOT_CONNECTED_PLAIN   = "I'm not connected to any groups!"  # filters.py — plain-text variant of NOT_CONNECTED
    FILTER_CMD_INCOMPLETE = "Command Incomplete :("             # /addfilter — missing args
    FILTER_ADDF_NO_CONTENT = "Add some content to save your filter!"  # /addfilter — no reply content given
    FILTER_ADDF_BTN_ALONE = "You cannot have buttons alone, give some text to go with it!"  # /addfilter — buttons with no text
    FILTER_ADDF_SUCCESS   = "Filter for  `{text}`  added in  **{title}**"  # /addfilter — success (double spaces preserved verbatim from original)
    FILTER_LIST_HEADER    = "Total number of filters in **{title}** : {count}\n\n"  # /viewfilters — list header
    FILTER_LIST_ITEM      = " ×  `{name}`\n"                    # /viewfilters — one row per filter (double space preserved verbatim)
    FILTER_LIST_EMPTY     = "There are no active filters in **{title}**"  # /viewfilters — no filters in chat
    FILTER_DEL_USAGE = (
        "<i>Mention the filtername which you wanna delete!</i>\n\n"
        "<code>/del filtername</code>\n\n"
        "Use /viewfilters to view all available filters"
    )  # /delelefilter — missing filter name argument
    FILTER_DELALL_CONFIRM = "This will delete all filters from '{title}'.\nDo you want to continue??"  # /deleteallf — confirmation prompt

    BTN_YES_PLAIN    = "YES"     # /deleteallf confirm — plain-text variant of BTN_YES
    BTN_CANCEL_PLAIN = "CANCEL"  # /deleteallf confirm — plain-text variant of BTN_CANCEL

    # ── Index (plugins/index.py) ──────────────────────────────────────────────
    INDEX_CANCELLING       = "Cancelling Indexing"  # index_files callback — index_cancel answer
    INDEX_REJECTED_NOTICE  = (
        "<b>Your Submission for indexing {chat} has been declined by our moderators.\n"
        "This is may be because your channel not have media file\n\n"
        "If you have anything to tell admin \ntype message and reply that message by /feedback<b>"
    )  # index_files — reject branch DM (closing tag preserved verbatim from original, incl. the malformed <b>)
    INDEX_WAIT_PROCESS     = "Wait until previous process completes."  # index_files — lock already held
    INDEX_PROCESSING       = "Processing...⏳"  # index_files — answer on accept
    INDEX_ACCEPTED_NOTICE  = "Your Submission for indexing {chat} has been accepted by our moderators and will be added soon."  # index_files — accept branch DM
    INDEX_STARTING         = "Starting Indexing"  # index_files — initial msg.edit

    INDEX_CMD_NO_REPLY      = "Please reply to a forwarded message to use the /index command."  # /index — no reply
    INDEX_LINK_CANT_JOIN    = "<b>This is link but i can't join by this.\n\nplease add me in channel and send me any media file then reply /index</b>"  # /index — link match failed
    INDEX_UNSUPPORTED_TYPE  = "<b>Unsupported message type. Please reply to a valid forwarded message or link.</b>"  # /index — neither forward nor link
    INDEX_PRIVATE_CHANNEL   = "<b>This may be a private channel/group. Make me an admin over there to index the files.</b>"  # /index — ChannelInvalid
    INDEX_INVALID_LINK      = "Invalid Link specified."  # /index — UsernameInvalid/UsernameNotModified
    INDEX_GENERIC_ERROR     = "Errors - {e}"  # /index — unexpected exception on get_chat
    INDEX_ADMIN_CHECK_FAIL  = "<b>Make sure I am an admin in the channel, if the channel is private.</b>"  # /index — get_messages failed
    INDEX_NOT_ADMIN_GROUP   = "<b> I am not an admin of the group.</b>"  # /index — empty message (leading space preserved verbatim)
    INDEX_CONFIRM_PROMPT    = "<b>Do you want to index this Channel/Group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code></b>"  # /index — admin confirm prompt
    INDEX_INVITE_LINK_FAIL  = "<b>Make sure I am an admin in the chat and have permission to invite users.</b>"  # /index — ChatAdminRequired on invite-link creation
    INDEX_LOG_REQUEST = (
        "#IndexRequest\n\nBy: {mention} (<code>{user_id}</code>)\n"
        "Chat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\n"
        "InviteLink: {link}"
    )  # /index — moderator LOG_CHANNEL post (always English — moderator-facing, not the requester's language)
    INDEX_THANKS_CONTRIBUTION = "<b>Thank you for the contribution. Wait for my moderators to verify the files.</b>"  # /index — non-admin submission accepted for review
    INDEX_CMD_INVALID_REPLY   = "<b>Please reply to a forwarded message or a valid link to use the /index command.</b>"  # /index — fallback else branch

    SETSKIP_NOT_INT = "Skip number should be an integer."  # /setskip — non-integer arg
    SETSKIP_SUCCESS = "Successfully set SKIP number as {skip}"  # /setskip — success
    SETSKIP_USAGE   = "Give me a skip number."  # /setskip — missing arg

    INDEX_PROGRESS_START = "Starting to save files. Click 'Cancel' to stop."  # index_files_to_db — initial msg.edit
    INDEX_PROGRESS_CANCELLED = (
        "Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )  # index_files_to_db — user cancelled mid-run
    INDEX_PROGRESS_UPDATE = (
        "Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )  # index_files_to_db — every 100-message progress tick
    INDEX_ERROR = "Error: {e}"  # index_files_to_db — unhandled exception
    INDEX_PROGRESS_DONE = (
        "Successfully saved <code>{total_files}</code> to dataBase!\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\n"
        "Deleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )  # index_files_to_db — completed successfully

    BTN_CANCEL_INDEX  = "Cancel"        # index_files / index_files_to_db — cancel-indexing button (plain variant)
    BTN_YES_INDEX     = "Yes"           # /index confirm prompt — plain variant
    BTN_CLOSE_LOWER   = "close"         # /index confirm prompt — plain lowercase variant of BTN_CLOSE
    BTN_ACCEPT_INDEX  = "Accept Index"  # /index moderator-review buttons
    BTN_REJECT_INDEX  = "Reject Index"  # /index moderator-review buttons

    # ── Search (plugins/pm_filter_search.py) ──────────────────────────────────
    SEARCH_INVALID_QUERY = (
        "<b>⚠️ Invalid Search Query!</b>\n\n"
        "• Please type at least <b>3 characters</b> of the movie/series name.\n"
        "• Avoid sending only special characters or symbols (like <code>*, !, ?, @, #</code>)."
    )  # auto_filter — cleaned query too short
    SEARCH_NO_IMDB_CAPTION = "𝐒𝐚𝐡𝐞𝐛! 𝐌𝐮𝐣𝐡𝐞 𝐊𝐮𝐜𝐡 𝐌𝐢𝐥𝐚 𝐇𝐚𝐢 {search}\n\n"  # auto_filter — caption fallback when IMDb lookup has no result
    SPELL_NOT_FOUND        = "I couldn't find any movies related to **{query}**. Try searching on Google or in the request group."  # advantage_spell_chok — no movies from feedback/mongo/imdb
    SPELL_GENERIC_ERROR    = "An error occurred while processing your request. Please try again or check the request group."  # advantage_spell_chok — exception fallback (used in two except blocks)
    SPELL_NO_VALID_TITLES  = "No valid movie titles found for **{query}**. Try searching on Google or in the request group."  # advantage_spell_chok — movies had no usable titles
    SPELL_NO_CLOSE_MATCHES = "<b>No close matches found for **{query}**.</b>\n\n<b>Here are some suggestions:</b>"  # advantage_spell_chok — fuzzy match below threshold

    BTN_SEND_ALL      = "𝐒𝐞𝐧𝐝 𝐀𝐥𝐥"                      # auto_filter — send-all-results button
    BTN_RESULTS_OF    = "Results Of👉🏻 {search} 👈🏻"        # auto_filter — results header button
    BTN_PAGES_COUNTER = "\u2060✧✧ 1/{total_pages}"       # auto_filter — page counter, multi-page (word-joiner preserved verbatim)
    BTN_NEXT          = "𝐍𝐄𝐗𝐓➡"                          # auto_filter — next-page button
    BTN_PAGES_SINGLE  = "(\u2060✧ 1/1 ✧"                 # auto_filter — page counter, single page (word-joiner + asymmetric paren preserved verbatim)
    BTN_SEARCH_GOOGLE = "Search Google"                  # advantage_spell_chok — fallback link button
    BTN_REQUEST_GROUP = "Request Group"                  # advantage_spell_chok — fallback link button
    BTN_SPELL_CLOSE   = "Close"                          # advantage_spell_chok — close-suggestions button

    # ── Contact (plugins/Extra/contact.py) ────────────────────────────────────
    CONTACT_NO_REPLY      = "Please reply to a message with your feedback or issue."  # /feedback, /report — no reply given
    CONTACT_FEEDBACK_SENT = "Your feedback has been sent to the admin. Please be patient, the admin will reply soon."  # /feedback, /report — delivered

    TALK_USAGE        = "Please provide a secret code after the /talk command. Example: `/talk secretcode123`"  # /talk — missing code arg
    TALK_INVALID_CODE = "Invalid secret code. Please try again."  # /talk — code not recognized
    TALK_NO_REPLY = (
        "Please reply to a message with your secret code to send it to the admin. \n"
        "example: <code> /talk abc123 </code>"
    )  # /talk — no reply given
    TALK_MESSAGE_SENT = "Your message has been delivered to the admin. Please be patient, the admin will reply soon."  # /talk — delivered

    SECRETCODE_CREATE_UNAUTHORIZED = "You are not authorized to create a secret code."  # /create_code — non-admin
    SECRETCODE_CREATE_PROMPT       = "Please provide the name for the new secret code."  # /create_code — ask for name
    SECRETCODE_ALREADY_EXISTS      = "This secret code already exists."                 # /create_code — duplicate
    SECRETCODE_CREATED             = "New secret code has been created successfully:\n\n`{new_code}`"  # /create_code — success

    SECRETCODE_DELETE_UNAUTHORIZED = "You are not authorized to delete a secret code."  # /delete_code — non-admin
    SECRETCODE_DELETE_PROMPT       = "Please provide the secret code you want to delete."  # /delete_code — ask for code
    SECRETCODE_NOT_FOUND           = "This secret code does not exist."                 # /delete_code — code missing
    SECRETCODE_DELETED             = "Secret code '{code}' has been deleted successfully!"  # /delete_code — success

    SEND_USAGE            = "<b>Usage: /send <target_user_id></b>"  # /send — missing target id
    SEND_USERS_HEADER      = "Users Saved In DB Are:\n\n"  # /send — header text (unused/dead in current logic; converted verbatim, not wired up)
    SEND_SUCCESS           = "<b>Your message has been successfully sent to {mention}.</b>"  # /send — delivered
    SEND_USER_NOT_STARTED  = "<b>This user hasn't started the bot yet!</b>"  # /send — target not in DB
    SEND_ERROR             = "<b>Error: {e}</b>"  # /send — exception
    SEND_NO_REPLY          = "<b>Use this command as a reply to a message, specifying the target user ID.</b>"  # /send — no reply given

    # ── Check-alive (plugins/Extra/check_alive.py) ────────────────────────────
    ALIVE_MSG        = "**You are very lucky 🤞 I am alive ❤️ Press /start to use me**"  # /alive
    PING_PLACEHOLDER = "..."                              # /ping — initial placeholder before edit
    PING_RESULT      = "Pong!\n{time_taken} ms"           # /ping — round-trip time

    # ── Envs (plugins/envscommand.py) ─────────────────────────────────────────
    ENV_ADD_USAGE      = "Usage: /add_env {config_name} {key} {value}"  # /add_env — missing args
    ENV_ADD_SUCCESS    = "Environment variable <pre> {key} = {value} </pre> added to {config_name}."  # /add_env — success
    ENV_GET_USAGE      = "Usage: /get_envs {config_name}"  # /get_envs — missing arg
    ENV_GET_EMPTY      = "No environment variables found for {config_name}."  # /get_envs — no data
    ENV_GET_LIST       = "Current environment variables for {config_name}:\n<pre>{env_str}</pre>"  # /get_envs — success
    ENV_ALL_HEADER     = "Current Environment Configurations:\n\n"  # /all_envs — response header
    ENV_ALL_ITEM       = "<b>{config_name}</b>:\n<pre>{details}</pre>\n\n"  # /all_envs — one config block
    ENV_ALL_EMPTY      = "No environment configurations found."  # /all_envs — no configs
    ENV_ALL_ERROR      = "An error occurred while fetching configurations: {error}"  # /all_envs — exception
    ENV_UPDATE_USAGE   = "Usage: /update_env {config_name} {key} {value}"  # /update_env — missing args
    ENV_UPDATE_SUCCESS = "Environment variable {key} updated to {value} in {config_name}."  # /update_env — success
    ENV_UPDATE_FAIL    = "Failed to update environment variable {key} in {config_name}."  # /update_env — failure
    ENV_DELETE_USAGE   = "Usage: /delete_env {config_name} {key}"  # /delete_env — missing args
    ENV_DELETE_SUCCESS = "Environment variable <pre>{key}</pre> deleted from {config_name}."  # /delete_env — success
    ENV_DELETE_FAIL    = "Failed to delete <pre>{key}</pre> from {config_name}. It might not exist."  # /delete_env — failure

    # ── Banned (plugins/banned.py) ────────────────────────────────────────────
    BANNED_USER_REPLY = "Sorry Dude, You are Banned to use Me... आप प्रतिबंधित है।\nBan Reason (कारण): {ban_reason}"  # ban_reply — banned user tries to use bot in PM
    GRP_DISABLED_NOTICE_BILINGUAL = (
        "CHAT NOT ALLOWED 🐞\n\n"
        "My admins has restricted me from working here ! If you want to know more about it contact support.\n"
        "मेरे एडमिन ने मुझे यहाँ काम करने से प्रतिबंधित कर दिया है! यदि आप इसके बारे में अधिक जानना चाहते हैं तो Support पर संपर्क करें.\n"
        "Reason : <code>{reason}</code>."
    )  # grp_bd — bot leaves a disabled group (distinct from CHAT_NOT_ALLOWED: bilingual + reason, not <b>-wrapped)

    # ── WebApp buttons (plugins/cmd_weappb.py) ────────────────────────────────
    BTN_OPEN_WEBAPP_SEARCH = "🔎 Open Media Search"  # /webapp — WebApp launch button
    WTRY_ALIVE = "✅ <b>wtry reached this file and the handler is alive.</b>\n\n<b>Source:</b> <code>{source}</code>"  # /wtry — diagnostic ping
    WEBAPP_NOT_CONFIGURED = (
        "<b>Web App URL is not configured.</b>\n"
        "Set the <code>BASE_URL</code> environment variable to your server URL."
    )  # /webapp — BASE_URL missing/invalid
    WEBAPP_MARKUP_ERROR = "<b>❌ Could not build Web App button:</b>\n<code>{error}</code>"  # /webapp — markup build failed
    WEBAPP_SUCCESS = (
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.\n\n"
        "<b>Path:</b> <code>{source}</code>"
    )  # /webapp — success
    WEBAPP_SEND_ERROR = "<b>❌ Failed to send WebApp message:</b>\n<code>{error}</code>"  # /webapp — reply send failed
    WEBAPP_CRASH = "<b>❌ /webapp crashed:</b>\n<code>{error}</code>"  # /webapp — unexpected exception

    # ── PM Filter entry point (plugins/pm_filter.py) ──────────────────────────
    PMFILTER_ANON_ADMIN = (
        "<b>You are an anonymous admin. I can't process your request. "
        "Please disable 'Remain Anonymous' in admin rights to continue.</b>"
    )  # give_filter — anonymous admin sent a group message
    BTN_JOIN_SEARCH_GROUP = "Join Search Group"  # give_filter — support-chat redirect button
    PMFILTER_NOT_SEARCH_GROUP = "<b>This is not the search group. Please join the search group by tapping the button below:</b>"  # give_filter — message sent in support chat
    PMFILTER_GROUP_BAN_NOTICE = (
        "<b>This Group Ban Anytime so Join Another Private Group.</b>"
        "<i>👉🏻Link(1) : https://t.me/+5pa88NB3YAhiNDQ1 </i>\n"
        "<i>👉🏻Link(2) : https://t.me/+13JZ5BMiiSM4ZmE1 </i>\n\n"
        " Wait 10 second Bot is finding Movie"
    )  # give_filter — sent before running manual/auto-filter in a normal group
    PMFILTER_FLOODWAIT         = "<b>FloodWait detected. Please wait {seconds} seconds before trying again.</b>"  # give_filter — FloodWait caught
    PMFILTER_UNEXPECTED_ERROR  = "<b>An unexpected error occurred. Please try again later.\n\nDetails: {error}</b>"  # give_filter — generic exception

    BTN_SEARCH_GROUP_EMOJI = "🔍 Search Group"    # get_butto1ns — private-chat redirect keyboard (currently disabled/unused caller)
    BTN_OFFER_CHANNEL      = "📢 Offer Channel"   # get_butto1ns
    BTN_DONATE_MONEY       = "💰 Donate"          # get_butto1ns — distinct emoji from BTN_DONATE (💳)
    BTN_MAIN_CHANNEL_EMOJI = "🏠 Main Channel"    # get_butto1ns

    # ── Inline search (plugins/inline.py) ─────────────────────────────────────
    INLINE_NOT_SUBSCRIBED = "You must subscribe to use this bot"  # answer — AUTH_CHANNEL gate, switch_pm_text
    INLINE_EMPTY_QUERY     = "📂 Type any movie or web series name to search."  # answer — empty query, switch_pm_text
    INLINE_SEARCH_ERROR    = "Error occurred"  # answer — get_search_results exception, switch_pm_text
    INLINE_RESULTS_FOUND   = "Results - {total_results}"  # answer — results found (emoji.FILE_FOLDER prepended in code)
    INLINE_RESULTS_SUFFIX  = " for '{query}'"  # answer — appended to both the found/no-results switch_pm_text when a query string was given
    INLINE_NO_RESULTS      = "No results"  # answer — no results found (emoji.CROSS_MARK prepended in code)

    BTN_SEARCH_AGAIN     = "Search again"    # get_reply_markup / get_reply_markup1 — switch_inline_query_current_chat button
    BTN_SEARCH_GROUP_PLAIN = "Search Group"  # get_reply_markup — plain variant, distinct from stylized BTN_SEARCH_GROUP
    BTN_MAIN_CHANNEL_PLAIN = "Main Channel"  # get_reply_markup — plain variant, distinct from BTN_MAIN_CHANNEL_EMOJI
    BTN_DONATE_US           = "Donate Us"    # get_reply_markup — donation callback button


# ─────────────────────────────────────────────────────────────────────────────
# HINDI  (हिंदी)
# Only override keys you have translated. All others fall back to EN automatically.
# ─────────────────────────────────────────────────────────────────────────────
class HI(EN):

    START = (
        "<b><blockquote>👋 नमस्ते <i>{name}</i>,\n"
        "✨ मेरा नाम <a href='https://t.me/{uname}'><b>{bname}</b></a> है ✨</blockquote>\n\n"
        "<b><i>⚡ मैं <a href='https://t.me/filmykeedha'>@FilmyKeedha</a> द्वारा "
        "संचालित आपका अल्टीमेट फ़ाइल शेयरिंग बॉट हूँ ⚡</i></b>\n\n"
        "📚 टेलीग्राम पर सबसे बड़े मीडिया डेटाबेस के साथ, हम 2021 से "
        "उपयोगकर्ताओं को निःशुल्क सेवा दे रहे हैं और भविष्य में भी <b>मुफ़्त</b> रहेंगे!</b>"
    )

    FORCE_SUB_MSG = "<b>⚠️ इस बॉट का उपयोग करने के लिए कृपया मेरे अपडेट चैनल से जुड़ें!</b>"

    VERIFY_REQUIRED = "<b>🔐 आप सत्यापित नहीं हैं!\nजारी रखने के लिए कृपया सत्यापन करें।</b>"
    VERIFY_SUCCESS  = (
        "<b>🎉 अरे {name}, आपने सफलतापूर्वक सत्यापन कर लिया!\n"
        "आज आधी रात तक सभी मूवीज़ के लिए असीमित एक्सेस मिल गई।\n\n"
        "मज़े करें! 🤩</b>"
    )
    VERIFY_INVALID_LINK = "<b>❌ लिंक अमान्य या समाप्त हो गया है!</b>"

    FILE_WAIT       = "<b>⏳ कृपया प्रतीक्षा करें...</b>"
    FILE_NOT_FOUND  = "<b>❌ ऐसी कोई फ़ाइल मौजूद नहीं है।</b>"
    FILE_DELETED_OK = "<b>✅ आपकी फ़ाइल/वीडियो सफलतापूर्वक डिलीट हो गई!</b>"
    ALL_DELETED_OK  = "<b>✅ आपकी सभी फ़ाइलें/वीडियो सफलतापूर्वक डिलीट हो गई!</b>"

    DELETEMSG = (
        "\n<pre><b>⏳ {minutes} मिनट में डिलीट होगा 🗑️</b></pre>\n"
        "<pre>अपनी फ़ाइलें बचाने के लिए यह करें 👇🏻\n"
        "├── 📤 दोस्तों को फ़ॉरवर्ड करें\n"
        "├── 📲 Saved Messages में फ़ॉरवर्ड करें\n"
        "└── 👥 हमारे ग्रुप में फ़ॉरवर्ड करें</pre>\n"
        "<a href='https://t.me/Filmykeedha/306'>👉🏻 ग्रुप जॉइन करें 👈🏻</a>"
    )

    LANG_SELECT_MSG = "<b>🌐 कृपया अपनी पसंदीदा भाषा चुनें:</b>"
    LANG_SET_OK     = "<b>✅ भाषा सेट हो गई: {lang_name}</b>"

    HELP_MAIN = (
        "<b>🆘 सहायता केंद्र</b>\n\n"
        "कमांड देखने के लिए नीचे कोई श्रेणी चुनें 👇"
    )

    GUIDE_SEARCH_TIP    = "🔍 मूवी का नाम ग्रुप में टाइप करें"
    GUIDE_VERIFY_TIP    = "🔐 फ़ाइलें अनलॉक करने के लिए चैनल जॉइन करें 🔓"
    GUIDE_SHORT_QUERY   = "⚠️ कम से कम 2 अक्षर टाइप करें"
    GUIDE_SAVE_FILE_TIP = "💾 फ़ाइल रखने के लिए Saved Messages में फ़ॉरवर्ड करें!"

    # ── Button labels ─────────────────────────────────────────────────────────
    BTN_SHARE        = "➕ दोस्तों के साथ शेयर करें ➕"  # Start msg — share bot link
    BTN_SEARCH       = "🔎 खोजें 🧐"                     # Start msg — inline search trigger
    BTN_GROUP        = "✪ ग्रुप ✪"                       # Start msg — main group link
    BTN_HELP         = "🙆🏻 सहायता 🦾"                   # Start msg & callbacks
    BTN_ABOUT        = "♥️ जानकारी ♥️"                   # Start msg & callbacks
    BTN_ADD_TO_GROUP = "➕ ग्रुप में जोड़ें ➕"            # Start msg after subscribe
    BTN_BACK         = "◀️ वापस"                         # Help menu — back
    BTN_MAIN_MENU    = "🏠 मुख्य मेनू"                   # Help menu — main menu
    BTN_CLOSE        = "✖️ बंद करें"                     # Generic close
    BTN_LANGUAGE     = "🌐 भाषा"                         # Language selector
    BTN_JOIN_CHANNEL = "⚠️ अपडेट चैनल जॉइन करें ⚠️"    # Force-sub gate
    BTN_TRY_AGAIN   = "🔄 फिर कोशिश करें"               # After joining channel
    BTN_VERIFY       = "✅ सत्यापित करें"                # Verify gate
    BTN_VERIFY_HOW   = "❓ सत्यापन कैसे करें"            # Verify tutorial
    BTN_DONATE       = "💳 दान करें"                     # File msg — donation
    BTN_GET_AGAIN    = "🔁 फ़ाइल फिर से पाएं"            # Post-delete
    BTN_SEND_RECEIPT = "📧 भुगतान रसीद भेजें 🧾"        # Donate
    BTN_YES          = "✅ हाँ"                           # Confirm deleteall
    BTN_CANCEL       = "❌ रद्द करें"                    # Cancel

    ANON_ADMIN_CONNECT   = "आप अनाम एडमिन हैं। PM में /connect {chat_id} का उपयोग करें"
    CONNECT_USAGE        = (
        "<b>सही फॉर्मेट में लिखें!</b>\n\n"
        "<code>/connect groupid</code>\n\n"
        "<i>अपने ग्रुप का ID पाने के लिए बॉट को ग्रुप में जोड़ें और <code>/id</code> का उपयोग करें</i>"
    )
    CONNECT_NOT_ADMIN    = "आपको दिए गए ग्रुप में एडमिन होना चाहिए!"
    CONNECT_INVALID_ID   = "अमान्य ग्रुप ID!\n\nअगर सही है, तो सुनिश्चित करें कि मैं आपके ग्रुप में मौजूद हूँ!!"
    CONNECT_SUCCESS_PM   = "**{title}** से सफलतापूर्वक जुड़ गए\nअब अपने ग्रुप को मेरी PM से मैनेज करें !"
    CONNECT_SUCCESS_GRP  = "**{title}** से जुड़ गए !"
    CONNECT_ALREADY      = "आप पहले से इस चैट से जुड़े हुए हैं!"
    CONNECT_ADD_ME_ADMIN = "मुझे ग्रुप में एडमिन बनाएं"
    CONNECT_ERROR        = "कुछ गड़बड़ी हुई! बाद में फिर कोशिश करें।"
    DISCONNECT_HINT_PM   = "ग्रुप देखने या डिस्कनेक्ट करने के लिए /connections चलाएं!"
    DISCONNECT_SUCCESS   = "इस चैट से सफलतापूर्वक डिस्कनेक्ट हो गए"
    DISCONNECT_NOT_FOUND = "यह चैट मुझसे जुड़ी नहीं है!\nजुड़ने के लिए /connect करें।"
    CONNECTIONS_NONE     = "कोई सक्रिय कनेक्शन नहीं है!! पहले किसी ग्रुप से जुड़ें।"
    CONNECTIONS_LIST     = "आपके जुड़े हुए ग्रुप की जानकारी ;\n\n"

    NOT_FORWARDED_FROM_CHANNEL = "यह मैसेज किसी चैनल से फॉरवर्ड नहीं किया गया है।"
    IMDB_SEARCHING    = "ImDB पर खोज रहे हैं"
    IMDB_NO_RESULTS   = "कोई परिणाम नहीं मिला"
    IMDB_FOUND        = "यह रहा जो मुझे IMDb पर मिला"
    IMDB_GIVE_NAME    = "मुझे मूवी / सीरीज़ का नाम दें"
    IMDB_NO_RESULTS_CAPTION = "कोई परिणाम नहीं"
    BTN_CLOSE_LOCK    = "🔐 बंद करें"

    BATCH_USAGE = "सही फॉर्मेट में लिखें।\nउदाहरण: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`।"
    BATCH_INVALID_LINKS = "अमान्य लिंक दिए गए हैं।"
    BATCH_DIFFERENT_CHATS = "सभी लिंक एक ही चैट के होने चाहिए।"
    BATCH_CHAT_ACCESS_ERROR = "चैट एक्सेस करने में त्रुटि। सुनिश्चित करें कि बॉट के पास एडमिन एक्सेस है।"
    BATCH_ASK_NAME = "इस बैच के लिए एक नाम दें।"
    BATCH_ASK_OPTIONAL_MSG = "अब एक वैकल्पिक संदेश दें (छोड़ने के लिए 'pass' टाइप करें)।"
    BATCH_PROCESSING = "आपका बैच प्रोसेस किया जा रहा है..."
    BATCH_CREATED = "बैच सफलतापूर्वक बन गया!\nबैच नाम: {name}\nइसमें `{count}` फ़ाइलें हैं।\nलिंक: {link}"
    BTN_GET_ALL_FILES = "सभी फ़ाइलें/एपिसोड पाएं"

    BTN_CAT_SEARCH   = "🔍 खोज और फ़ाइलें"              # Help — search category
    BTN_CAT_FILTERS  = "⚙️ फ़िल्टर"                     # Help — filters category
    BTN_CAT_CONNECT  = "🔗 कनेक्शन"                     # Help — connections category
    BTN_CAT_EXTRA    = "🎛️ अतिरिक्त सुविधाएं"          # Help — extra category
    BTN_CAT_FSUB     = "🔐 बाध्य सदस्यता"               # Help — fsub category
    BTN_CAT_ADMIN    = "🛠 समूह एडमिन"                    # Help — admin category (renamed to Group Admin, matches EN)


# ─────────────────────────────────────────────────────────────────────────────
# TAMIL stub — add translations when contributor is ready
# Every key falls back to EN until translated.
# ─────────────────────────────────────────────────────────────────────────────
class TA(EN):
    # TODO: Add Tamil translations here
    # BTN_HELP = "உதவி 🦾"
    pass


# ─────────────────────────────────────────────────────────────────────────────
# Registry & helpers
# ─────────────────────────────────────────────────────────────────────────────

# Map IETF code → class
LANGUAGES: dict[str, type] = {
    "en": EN,
    "hi": HI,
    "ta": TA,
}

# Shown in the /language picker UI
LANGUAGE_MENU = [
    {"code": "en", "flag": "🇬🇧", "name": "English"},
    {"code": "hi", "flag": "🇮🇳", "name": "हिंदी (Hindi)"},
    {"code": "ta", "flag": "🇮🇳", "name": "தமிழ் (Tamil)"},
]

DEFAULT_LANG = "en"


def _cls(lang_code: str) -> type:
    """Return the language class for a code, falling back to EN."""
    return LANGUAGES.get(lang_code, EN)


def get(lang_code: str, key: str, **kwargs) -> str:
    """
    Fetch a message string by key for the given language.
    Falls back to English if the key is not translated or the language is unknown.
    Applies .format(**kwargs) if kwargs are provided.

    Example:
        get("hi", "START", name=user.mention, uname="bot", bname="Rashmi")
    """
    cls = _cls(lang_code)
    # Prefer the translated class; fall back to EN if key missing
    text = getattr(cls, key, None) or getattr(EN, key, f"[MISSING:{key}]")
    return text.format(**kwargs) if kwargs else text


def get_btn(lang_code: str, key: str) -> str:
    """
    Fetch a button label by key for the given language.
    Same fallback logic as get().

    Example:
        get_btn("hi", "BTN_HELP")  →  "🙆🏻 सहायता 🦾"
    """
    return get(lang_code, key)
