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

    START_GROUP = (
        "<b><blockquote>👋 Hello <i>{name}</i>!</blockquote>\n\n"
        "I'm <a href='https://t.me/{uname}'><b>{bname}</b></a> — your File Sharing Bot!\n"
        "Use me in private to find and get files.</b>"
    )

    FORCE_SUB_MSG = "<b>⚠️ Please join my Updates Channel to use this bot!</b>"

    VERIFY_REQUIRED = "<b>🔐 You are not verified!\nKindly verify to continue.</b>"
    VERIFY_SUCCESS = (
        "<b>🎉 Hey {name}, you are successfully verified!\n"
        "You now have unlimited access for all movies till today midnight.\n\n"
        "Enjoy! 🤩</b>"
    )
    VERIFY_INVALID_LINK = "<b>❌ Invalid or Expired verification link!</b>"

    # ── Grouped Similar Text Variables ──────────────────────────────────────
    FILE_WAIT            = "<b>⏳ Please wait...</b>"
    FILE_NOT_FOUND       = "<b>❌ No such file exists.</b>"
    FILE_NOT_FOUND_PLAIN = "No such file exists."
    FILE_NOT_EXIST_PLAIN = "No such file exist."
    FILE_DELETED_OK      = "<b>✅ Your file/video has been successfully deleted!</b>"
    ALL_DELETED_OK       = "<b>✅ All your files/videos have been successfully deleted!</b>"
    FILE_DEL_DB_OK       = "<b>✅ File successfully deleted from database.</b>"
    FILE_NOT_IN_DB       = "<b>❌ File not found in database.</b>"
    FILE_SENT_TO_PM      = "Check Your Private message, I have sent files in pm \nCheck @Rashmika_mandanana_bot"
    ALL_FILES_SENT_PM    = "Hey {name}, All files on this page has been sent successfully to your PM !"

    NOT_IN_GROUP         = "<b>Make sure I'm present in your group!</b>"
    NOT_IN_GROUP_PLAIN   = "Make sure I'm present in your group!!"
    
    NOT_CONNECTED           = "<b>I'm not connected to any groups!</b>"
    NOT_CONNECTED_PLAIN     = "I'm not connected to any groups!"
    NOT_CONNECTED_BILINGUAL = "I'm not connected to any groups!\nCheck /connections or connect to any groups"
    
    GIVE_CHAT_ID              = "Give Me A Chat ID"
    GIVE_CHAT_ID_HI           = "Give Me A Chat ID"
    GIVE_VALID_CHAT_ID        = "Give Me A Valid Chat ID"
    GIVE_VALID_CHAT_ID_HI     = "Give Me A Valid Chat ID"
    GIVE_VALID_CHAT_ID_PLAIN  = "Give Me A Valid Chat ID!"
    GIVE_VALID_CHAT_ID_PLAIN2 = "Give Me A Valid Chat ID!"
    
    CHAT_NOT_FOUND_DB      = "Chat Not Found In DB"
    CHAT_NOT_FOUND_DB_HI   = "Chat Not Found In DB !"
    CHAT_ALREADY_DISABLED  = "This chat is already disabled:\nReason-<code> {reason} </code>"
    CHAT_DISABLED_OK       = "Chat Successfully Disabled"
    CHAT_NOT_DISABLED_YET  = "This chat is not yet disabled."
    CHAT_RE_ENABLED_OK     = "Chat Successfully re-enabled"
    
    GIVE_USER_ID       = "Give Me A User Id / Username"
    GIVE_USER_ID_PLAIN = "Give Me A User Id / Username"
    
    ANON_ADMIN_MSG      = "<b>You are an anonymous admin. Use /connect {chat_id} in PM.</b>"
    ANON_ADMIN_CONNECT  = "You are anonymous admin. Use /connect {chat_id} in PM"
    PMFILTER_ANON_ADMIN = "<b>You are an anonymous admin. I can't process your request. Please disable 'Remain Anonymous' in admin rights to continue.</b>"

    DELETEMSG = (
        "\n<pre><b>⏳ Deleting in {minutes} Minutes 🗑️</b></pre>\n"
        "<pre>To save your files, do one of the following 👇🏻\n"
        "├── 📤 Forward to your friends\n"
        "├── 📲 Forward to saved messages\n"
        "└── 👥 Forward to our group</pre>\n"
        "<a href='https://t.me/Filmykeedha/306'>👉🏻 Join our Group 👈🏻</a>"
    )

    BATCH_NOT_FOUND     = "<b>❌ Invalid or expired batch link.</b>"
    BATCH_NO_FILES      = "<b>⚠️ No files found in this batch.</b>"
    BATCH_INVALID_DATA  = "<b>⚠️ Invalid file data in this batch.</b>"
    BATCH_INFO          = "<b>📦 Batch:</b> {name}\n<b>📝 Note:</b> {msg}\nProcessing <b>{count}</b> files..."
    BATCH_PROCESSING    = "<b>⏳ Please wait, processing files...</b>"
    BATCH_USAGE             = "Use correct format.\nExample: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`."
    BATCH_INVALID_LINKS     = "Invalid link(s) provided."
    BATCH_DIFFERENT_CHATS   = "All links must belong to the same chat."
    BATCH_CHAT_ACCESS_ERROR = "Error accessing chat. Ensure the bot has admin access."
    BATCH_ASK_NAME          = "Provide a name for this batch."
    BATCH_ASK_OPTIONAL_MSG  = "Now, provide an optional message (or type 'pass' to skip)."
    BATCH_CREATED           = "Batch created successfully!\nBatch Name: {name}\nContains `{count}` files.\nLink: {link}"

    BOT_RESTARTING  = "<b>🔄 Processes stopped. Bot is restarting...</b>"
    BOT_RESTARTED   = "<b>✅ Bot is restarted. Now you can use me.</b>"
    PROCESSING      = "<b>⏳ Processing...</b>"
    REPLY_TO_FILE   = "<b>↩️ Reply to a file with /delete to remove it.</b>"
    UNSUPPORTED_FMT = "<b>❌ This file format is not supported.</b>"

    DELETE_ALL_CONFIRM = "<b>⚠️ This will delete ALL indexed files.\nDo you want to continue?</b>"
    DELETE_ALL_DONE    = "<b>✅ Successfully deleted all indexed files.</b>"
    DELETE_THANK       = "♥️ Thank You Filmykeedha ♥️"

    SETTINGS_TITLE = "<b>⚙️ Change settings for {title}</b>"
    TEMPLATE_SAVED = "<b>✅ Template for {title} changed to:\n\n{template}</b>"
    NO_INPUT       = "<b>⚠️ No input provided!</b>"
    INVALID_FORMAT = "<b>❌ Invalid format!</b>"

    BROADCAST_ASK      = "<b>You have 120 seconds to send your broadcast message.</b>"
    BROADCAST_ASK_MSG  = "Send your broadcast message (type or forward)."
    BROADCAST_TIMEOUT  = "<b>⏳ Time's up! Broadcast cancelled.</b>"
    BROADCAST_STARTING = "<b>📡 Broadcasting your messages...</b>"
    BROADCAST_PROGRESS = (
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

    SCRUB_USAGE = (
        "<b>⚠️ Invalid Format.</b>\n\n"
        "<b>Usage:</b> <code>/scrub [pattern] [size]</code>\n"
        "<b>Example:</b> <code>/scrub *spider-man* &gt;1GB</code>"
    )
    SCRUB_SCANNING   = "<b>🔍 Scanning database... please wait.</b>"
    SCRUB_NOT_FOUND  = "<b>❌ No files found matching:</b> <code>{pattern}</code>"
    SCRUB_CONFIRM    = (
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
    SCRUB_CANCELLED  = "<b>✅ Purge cancelled. No files were deleted.</b>"
    SCRUB_DONE       = "<b>🗑️ Purge complete!\n\n✅ Deleted: {count} files.</b>"
    SCRUB_EXPIRED    = "This purge request has expired or was already executed."
    SCRUB_ADMIN_ONLY = "This button is strictly for admins."
    SCRUB_ERROR      = "<b>❌ An error occurred: {error}</b>"

    STATUS_TXT = (
        "★ <b>Total Files:</b> <code>{files}</code>\n"
        "★ <b>Total Users:</b> <code>{users}</code>\n"
        "★ <b>Total Chats:</b> <code>{chats}</code>\n"
        "★ <b>Used Storage:</b> <code>{used}</code> MiB\n"
        "★ <b>Free Storage:</b> <code>{free}</code> MiB"
    )

    LOG_TEXT_G = "#NewGroup\nGroup = {title}(<code>{chat_id}</code>)\nTotal Members = <code>{members}</code>\nAdded By — {added_by}"
    LOG_TEXT_P = "#NewUser\nID — <code>{user_id}</code>\nName — {name}"

    CAPTION = (
        "<pre>✨ Name</pre>\n"
        "🎥 <b>@Filmykeedha</b> <a href='https://t.me/Filmykeedha/306'><b>{file_name}</b></a>\n\n"
        "<pre>✨ Size</pre>\n"
        "📂 <b><a href='https://t.me/Filmykeedha/306'>{file_size}</a></b>\n\n"
        "🔗 <b><a href='https://t.me/Filmykeedha'>Join FilmyKeedha 🔥</a></b>\n"
        "🎁 <b><a href='https://t.me/Filmykeedha/306'>💎 Tap for Exclusive Surprise 💎</a></b>\n\n"
        "<pre>💖 Support Us by Donating 🙏🏻</pre>"
    )

    MELCOW_ENG = (
        "<b>👋 Hello {name} 😍\n"
        "Welcome 🤗 to {group}\n\n"
        "Let's get started — the fun begins now 🥳\n"
        "Tap the button below 👇🏻 to find the active group.</b>"
    )

    LANG_SELECT_MSG = "<b>🌐 Please choose your preferred language:\nChoose Language / زبان چنید</b>"
    LANG_SET_OK     = "<b>✅ Language set to: {lang_name}</b>"

    # ── Help menus ────────────────────────────────────────────────────────────
    HELP_MAIN = "<b>🆘 Help Center</b>\n\nChoose a category below to see commands and how to use them 👇"
    
    HELP_CAT_SEARCH    = "<b>🔍 Search & Files</b>\n\n• Tap <b>Search 🔍</b> or just <b>type a movie/series name</b> in a connected group — results appear automatically.\n\n• <code>/index</code> — reply to the last forwarded message from a channel (or a t.me link) to index that channel's files into the database. Non-admin requests are sent to moderators for approval.\n\n• <code>/setskip N</code> — skip the first N messages while indexing a channel. (Bot admins only)"
    HELP_CAT_FILTERS   = "<b>⚙️ Filters</b>\n\nFilters make the bot auto-reply to specific keywords in a group.\n\n• <code>/addfilter keyword</code> (or <code>/addf</code>) — reply to a message to save it as a filter for that keyword.\n\n• <code>/viewfilters</code> (or <code>/filters</code>) — list every filter saved in the current or connected group.\n\n• <code>/delelefilter keyword</code> — remove one filter by keyword.\n\n• <code>/deleteallf</code> — remove every filter in the group. (Owner only)\n\n<b>NOTE:</b> the bot needs admin rights in the group."
    HELP_CAT_CONNECT   = "<b>🔗 Connections</b>\n\nConnect a group to your PM so you can manage it without spamming the group chat.\n\n• <code>/connect group_id</code> (in PM) or <code>/connect</code> (inside the group) — link a group to your account.\n\n• <code>/disconnect</code> — unlink the currently active group.\n\n• <code>/connections</code> — list your connected groups and switch which one is active.\n\n<b>NOTE:</b> only group admins can connect."
    HELP_CAT_EXTRA     = "<b>🎛️ Extra Features</b>\n\n• <code>/id</code> — get the ID of the current chat, or a replied user/channel.\n\n• <code>/info [reply|user_id|username]</code> — show details about a user.\n\n• <code>/imdb title</code> — search IMDb for a movie or series.\n\n• <code>/getfileid</code> (reply to media) — get that file's file_id.\n\n• <code>/alive</code> / <code>/ping</code> — check that the bot is online and measure its response time.\n\n• <code>/stats</code> — show database and storage stats.\n\n• <code>/language</code> — change your bot language.\n\n• <code>/set_template text</code> — set a custom file-caption template for your current/connected group.\n\n• <code>/donate</code> — see how to support the bot.\n\n• <code>/webapp</code> — open the media search Web App directly in Telegram.\n\n• <code>/chelp [m]</code> — alternate help text (add <code>m</code> for HTML mode).\n\n• <code>/wtry</code> / <code>/wtry2</code> — diagnostic pings confirming the webapp/misc handler files are loaded."
    HELP_CAT_POSTING   = "<b>📤 Media Posting</b>\n\n• <code>/cpost channel_id [m]</code> — reply to a message (media or text) to post it into that channel. Add <code>m</code> to parse the caption as Markdown instead of HTML.\n\n• <code>/ppost channel_id [m]</code> — same as <code>/cpost</code>, but the copy is protected from forwarding or saving.\n\n<b>NOTE:</b> you and the bot both need admin rights with post-message permission in that channel."
    HELP_CAT_CONTACT   = "<b>📨 Contact & Feedback</b>\n\n• <code>/feedback</code> (or <code>/report</code>) — reply to a message to send it to the admins as feedback or an issue report.\n\n• <code>/talk secret_code</code> — reply to a message with a code the admin gave you, to send it directly to them."
    HELP_CAT_FSUB      = "<b>🔐 Force Subscribe</b>\n\nForce Subscribe is configured by the bot owner via the <code>AUTH_CHANNEL</code> environment variable (not an in-chat command).\n\nWhen enabled, users must join the configured channel(s) before they can open files or use the bot in PM.\n\n• /id — Get a channel's ID (useful when setting up AUTH_CHANNEL)"
    HELP_CAT_ADMIN     = "<b>🛠 Group Admin</b>\n\n• <code>/leave chat_id</code> — make the bot leave a chat.\n\n• <code>/disable chat_id [reason]</code> — stop the bot from working in a chat.\n\n• <code>/enable chat_id</code> — re-enable a previously disabled chat.\n\n• <code>/invite chat_id</code> — generate an invite link for a chat.\n\n• <code>/ban user_id [reason]</code> / <code>/unban user_id [reason]</code> — ban or unban a user from using the bot.\n\n• <code>/users</code> / <code>/chats</code> — export all stored users or chats to a text file."
    HELP_CAT_ADMIN_BOT = "<b>🤖 Bot Admin</b>\n\n• <code>/settings</code> — open the settings panel for the current/connected group.\n\n• <code>/restart</code> — restart the bot.\n\n• <code>/logs</code> — send the recent log file.\n\n• <code>/channel</code> — list indexed channels/groups.\n\n• <code>/delete</code> (reply to a file) — delete that file's DB record.\n\n• <code>/deleteall</code> — start the flow to delete every indexed file.\n\n• <code>/scrub pattern size</code> — bulk-delete DB entries matching a pattern and size filter.\n\n• <code>/broadcast</code> / <code>/grp_broadcast</code> — broadcast a message to all users, or all groups.\n\n• <code>/batch link1 link2 ...</code> (or <code>/pbatch</code>) — build a batch link from multiple file links.\n\n• <code>/send user_id</code> (reply to your message) — send a copied message to a user without the forward tag.\n\n• <code>/create_code</code> / <code>/delete_code</code> — create or delete a secret code for <code>/talk</code>."
    HELP_CAT_ADMIN_ENV = "<b>🧩 Environment Config</b>\n\n• <code>/add_env config key value</code> — add a key/value pair to a named config.\n\n• <code>/get_envs config</code> — show all variables stored for a config.\n\n• <code>/all_envs</code> — list every stored config.\n\n• <code>/update_env config key new_value</code> — update a key in a config.\n\n• <code>/delete_env config key</code> — delete a key from a config."

    GUIDE_HELP_OPEN       = "💡 Tap a category to explore commands"
    GUIDE_SEARCH_TIP      = "🔍 Type a movie name in your group to search"
    GUIDE_VERIFY_TIP      = "🔐 Join the channel to unlock files 🔓"
    GUIDE_SHORT_QUERY     = "⚠️ Type at least 2 characters to search"
    GUIDE_SAVE_FILE_TIP   = "💾 Forward to Saved Messages to keep your file!"
    GUIDE_INDEX_TIP       = "📂 /index usage:\n\nForward the last message from your channel here, then reply to it with /index. I'll scan all files automatically."
    GUIDE_FILTER_TIP      = "⚙️ /addfilter usage:\n\nReply to any message with /addfilter [keyword] and I will auto-reply whenever that keyword is sent in the group."
    GUIDE_CONNECT_TIP     = "🔗 /connect usage:\n\nSend /connect [group_id] in my PM to manage group filters without going back to the group."

    # ─────────────────────────────────────────────────────────────────────────
    # GROUPED BUTTON LABELS  (prefix: BTN_)
    # ─────────────────────────────────────────────────────────────────────────
    BTN_SHARE                = "➕ Share with Friends ➕"
    
    BTN_SEARCH               = "🔎 Search 🧐"
    BTN_SEARCH_STYLE         = "🧞‍♀️ Search 🧐"
    BTN_SEARCH_AGAIN         = "Search again"
    BTN_SEARCH_GROUP         = "Search Group"
    BTN_SEARCH_GROUP_PLAIN   = "Search Group"
    BTN_SEARCH_GROUP_EMOJI   = "🔍 Search Group"
    BTN_JOIN_SEARCH_GROUP    = "Join Search Group"
    BTN_SEARCH_GOOGLE        = "Search Google"
    
    BTN_GROUP                = "✪ GROUP ✪"
    BTN_GROUP_STYLE          = "✪GROUP✪"
    BTN_REQUEST_GROUP        = "Request Group"
    
    BTN_HELP                 = "🙆🏻 Help 🦾"
    BTN_HELP_STYLE           = "🙆🏻 Help 🦾"
    
    BTN_ABOUT                = "♥️ About ♥️"
    BTN_ABOUT_STYLE          = "♥️ About ♥️"
    
    BTN_ADD_TO_GROUP         = "➕↖️ Add Me To Your Groups↗️➕"
    BTN_ADD_TO_GROUP_STYLE   = "➕↖️ Add Me To Your Groups↗️➕"

    BTN_BACK                 = "◀️ Back"
    BTN_BACK_STYLIZED        = "⬅BACK"
    BTN_BACK_PLAIN           = "BACK"
    
    BTN_NEXT                 = "NEXT➡"
    BTN_NEXT_STYLIZED        = "NEXT➡"
    
    BTN_MAIN_MENU            = "🏠 Main Menu"
    BTN_HOME                 = "🏠 Home"
    
    BTN_CLOSE                = "✖️ Close"
    BTN_CLOSE_DELETE_STYLE   = "⚠️ Close / Delete ⚠️"
    BTN_CLOSE_LOCK           = "🔐 Close"
    BTN_CLOSE_LOCK_STYLE     = "🔐 Close"
    BTN_CLOSE_LOWER          = "close"
    BTN_SPELL_CLOSE          = "Close"
    
    BTN_LANGUAGE             = "🌐 Language"
    
    BTN_SEND_ALL             = "Send All"
    BTN_GET_ALL_FILES        = "Get All Files/Episodes"
    BTN_GET_AGAIN            = "🔁 Get File Again"

    RESULTS_OF_HEADER        = "Results Of👉🏻 {search} 👈🏻"
    BTN_RESULTS_OF           = "Results Of👉🏻 {search} 👈🏻"
    
    PAGES_LABEL              = "📃 Pages {page} / {total_pages}"
    PAGE_LABEL_ALT           = "🗓 {page} / {total_pages}"
    BTN_PAGES_COUNTER        = "\u2060✧✧ 1/{total_pages}"
    BTN_PAGES_SINGLE         = "(\u2060✧ 1/1 ✧"

    BTN_CONNECT_ACTION       = "CONNECT"
    BTN_DISCONNECT_ACTION    = "DISCONNECT"
    BTN_DELETE_CONN          = "DELETE"

    BTN_JOIN_OFFER           = "Join Our Offer Zone 🤑"
    BTN_OFFER_CHANNEL        = "📢 Offer Channel"
    BTN_DONATE               = "💳 Donate"
    BTN_DONATE_MONEY         = "💰 Donate"
    BTN_DONATE_US            = "Donate Us"
    BTN_DONATE_RECEIPT_STYLE = "Send Payment Receipt 🧾"
    BTN_SEND_RECEIPT         = "📧 Send Payment Receipt 🧾"

    BTN_JOIN_CHANNEL         = "⚠️ Join Updates Channel ⚠️"
    BTN_TRY_AGAIN            = "🔄 Try Again"
    BTN_VERIFY               = "✅ Verify"
    BTN_VERIFY_HOW           = "❓ How to Verify"
    
    BTN_SUPPORT              = "💬 Support"
    BTN_SUPPORT_PLAIN        = "Support"
    BTN_SUPPORT_GROUP        = "Support Group"
    BTN_SUPPORT_STYLE        = "Support"
    
    BTN_YES                  = "✅ YES"
    BTN_YES_PLAIN            = "YES"
    BTN_YES_INDEX            = "Yes"
    BTN_CANCEL               = "❌ CANCEL"
    BTN_CANCEL_PLAIN         = "CANCEL"
    BTN_CANCEL_INDEX         = "Cancel"
    BTN_DELETE_ALL_DB        = "🗑️ YES, DELETE ALL"
    
    BTN_UPDATES              = "🔔 Updates 🤖"
    BTN_UPDATES_CHANNEL      = "Updates Channel"
    BTN_BOT_OWNER            = "Bot Owner"
    
    BTN_MAIN_CHANNEL_EMOJI   = "🏠 Main Channel"
    BTN_MAIN_CHANNEL_PLAIN   = "Main Channel"

    BTN_ACCEPT_INDEX         = "Accept Index"
    BTN_REJECT_INDEX         = "Reject Index"
    BTN_OPEN_WEBAPP_SEARCH   = "🔎 Open Media Search"

    BTN_CAT_SEARCH           = "🔍 Search & Files"
    BTN_CAT_FILTERS          = "⚙️ Filters"
    BTN_CAT_CONNECT          = "🔗 Connections"
    BTN_CAT_EXTRA            = "🎛️ Extra Features"
    BTN_CAT_POSTING          = "📤 Media Posting"
    BTN_CAT_CONTACT          = "📨 Contact & Feedback"
    BTN_CAT_FSUB             = "🔐 Force Subscribe"
    BTN_CAT_ADMIN            = "🛠 Group Admin"
    BTN_CAT_ADMIN_BOT        = "🤖 Bot Admin"
    BTN_CAT_ADMIN_ENV        = "🧩 Env Config"

    BTN_SET_FILTER_BTN       = "Filter Button"
    BTN_SET_BOTPM            = "Bot PM"
    BTN_SET_FILESECURE       = "File Secure"
    BTN_SET_IMDB             = "IMDB"
    BTN_SET_SPELL            = "Spell Check"
    BTN_SET_WELCOME          = "Welcome"
    BTN_SET_SINGLE           = "Single"
    BTN_SET_DOUBLE           = "Double"
    BTN_SET_YES              = "✅ Yes"
    BTN_SET_NO               = "❌ No"

    # ── Connections (plugins/connection.py) ──────────────────────────────────
    CONNECT_USAGE = (
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
    FILTERMDB_DELETED        = "'`{text}`' deleted. I'll not respond to that filter anymore."
    FILTERMDB_NOT_FOUND      = "Couldn't find that filter!"
    FILTERMDB_DELALL_NOTHING = "Nothing to remove in {title}!"
    FILTERMDB_DELALL_SUCCESS = "All filters from {title} have been removed."
    FILTERMDB_DELALL_FAIL    = "Couldn't remove all filters from group!"

    # ── Misc (plugins/misc.py) ────────────────────────────────────────────────
    NOT_FORWARDED_FROM_CHANNEL = "This message is not forwarded from a channel."
    IMDB_SEARCHING          = "Searching ImDB"
    IMDB_NO_RESULTS         = "No results Found"
    IMDB_FOUND              = "Here is what i found on IMDb"
    IMDB_GIVE_NAME          = "Give me a movie / series Name"
    IMDB_NO_RESULTS_CAPTION = "No Results"

    # ── plugins/pm_filter_callbacks.py ───────────────────────────────────────
    NOT_FOR_YOU_ALERT = "This Message is not for you dear. Don't worry you can send new one !"
    NOT_FOR_YOU_STYLIZED = "That's not for you sona!"
    OLD_BUTTON_RESEND = "You are using one of my old messages, please send the request again."
    OLD_BUTTON_EXPIRED = "You are clicking on an old button which is expired."
    CHECKING_MOVIE_DB = "Checking for Movie in database..."
    
    MOVIE_UNAVAILABLE_REQUEST = (
        "Currently unavailable!\nWe are really sorry for the inconvenience!\n\n"
        "Please send this Movie or Webseries name in #Request Topic or send using "
        "\"#Request Movie Name & Release Year.\nExample: <code> #Request Mirzapur Season 1 2018 </code>\n"
        "Our great admins will upload it as soon as possible!"
    )
    
    LOVE_ANSWER = "♥️ Love @Filmykeedha ♥️"
    SETTINGS_UPDATED = "✅ Updated"
    OWNER_REQUIRED_BILINGUAL = "You need to be Group Owner or an Auth User to do that!\n"
    GROUP_INFO_MARKDOWN = "Group Name : **{title}**\nGroup ID : `{group_id}`"
    CONNECTED_MARKDOWN = "Connected to **{title}**"
    DISCONNECTED_MARKDOWN = "Disconnected from **{title}**"
    ERROR_OCCURRED = "Some error occurred!!"
    CONN_DELETED = "Successfully deleted connection"
    UNBLOCK_BOT = "Unblock the Bot!"
    UNBLOCK_BOT_ALT = "Unblock the bot mahn !"
    JOIN_FIRST_STYLIZED = "Join this first ✋🏻"
    ACTIVE_CONN_CHANGED = "Your Active Connection Has Been Changed. Go To /settings."

    # ── plugins/p_ttishow.py ─────────────────────────────────────────────────
    CHAT_NOT_ALLOWED = (
        "<b>CHAT NOT ALLOWED 🐞\n\nMy admins have restricted me from working here! "
        "If you want to know more about it, contact support.</b>"
    )
    THANKS_FOR_ADDING = (
        "<b>Thank you for adding me to {title} ❣️\n\n"
        "If you have any questions or doubts about using me, contact support.</b>"
    )
    
    LEAVE_NOTICE_BILINGUAL = "<b>Hello Friends, \nMy Admin Has Told Me To Leave From Group, If You Wanna Add Me Again Contact My Support Group.</b> "
    LEAVE_NOTICE_WITH_REASON = "<b>Hello Friends, \nMy Admin Has Told Me To Leave From Group, If You Wanna Add Me Again Contact My Support Group.</b>Reason : <code>{reason}</code>"
    LEFT_CHAT_CONFIRM = "left the chat `{chat}`"
    GENERIC_ERROR = "Error - {error}"
    NO_REASON_PROVIDED = "No Reason Provided"
    
    FETCHING_STATS = "Fetching stats.."
    INVITE_FAILED = "Invite Link Generation Failed, I am Not Having Sufficient Rights. "
    INVITE_LINK_RESULT = "Here Is Your Invite Link {link}"
    INVALID_USER_NOT_MET = "This Is An Invalid User, Make Sure I Have Met Him Before. "
    INVALID_USER_MIGHT_BE_CHANNEL = "This might be a channel, make sure its a user. "
    USER_ALREADY_BANNED = "{mention} Is Already Banned \nReason : {reason}"
    USER_BANNED_OK = "{mention} Banned Successfully!"
    USER_NOT_BANNED_YET = "{mention} is not yet banned."
    USER_UNBANNED_OK = "{mention} Unbanned Successfully"
    FETCHING_USERS_LIST = "Getting List Of Users"
    USERS_LIST_CAPTION = "List Of Users"
    FETCHING_CHATS_LIST = "Getting List Of Chats"
    CHATS_LIST_CAPTION = "List Of Chats"
    FILE_ID_RESULT = "**File ID:** `{file_id}`\n**File Type:** {file_type}\n**File Size:** {file_size} bytes"
    GETFILEID_NO_MEDIA_REPLY = "Please reply to a media file (video, photo, document, etc.) to get its file ID."
    GETFILEID_NO_MEDIA = "Please reply to a media file or send a media message directly to get its file ID."

    # ── Filters (plugins/filters.py) ──────────────────────────────────────────
    FILTER_CMD_INCOMPLETE = "Command Incomplete :("
    FILTER_ADDF_NO_CONTENT = "Add some content to save your filter!"
    FILTER_ADDF_BTN_ALONE = "You cannot have buttons alone, give some text to go with it!"
    FILTER_ADDF_SUCCESS   = "Filter for  `{text}`  added in  **{title}**"
    FILTER_LIST_HEADER    = "Total number of filters in **{title}** : {count}\n\n"
    FILTER_LIST_ITEM      = " ×  `{name}`\n"
    FILTER_LIST_EMPTY     = "There are no active filters in **{title}**"
    FILTER_DEL_USAGE = (
        "<i>Mention the filtername which you wanna delete!</i>\n\n"
        "<code>/del filtername</code>\n\n"
        "Use /viewfilters to view all available filters"
    )
    FILTER_DELALL_CONFIRM = "This will delete all filters from '{title}'.\nDo you want to continue??"

    # ── Index (plugins/index.py) ──────────────────────────────────────────────
    INDEX_CANCELLING       = "Cancelling Indexing"
    INDEX_REJECTED_NOTICE  = (
        "<b>Your Submission for indexing {chat} has been declined by our moderators.\n"
        "This is may be because your channel not have media file\n\n"
        "If you have anything to tell admin \ntype message and reply that message by /feedback<b>"
    )
    INDEX_WAIT_PROCESS     = "Wait until previous process completes."
    INDEX_PROCESSING       = "Processing...⏳"
    INDEX_ACCEPTED_NOTICE  = "Your Submission for indexing {chat} has been accepted by our moderators and will be added soon."
    INDEX_STARTING         = "Starting Indexing"

    INDEX_CMD_NO_REPLY      = "Please reply to a forwarded message to use the /index command."
    INDEX_LINK_CANT_JOIN    = "<b>This is link but i can't join by this.\n\nplease add me in channel and send me any media file then reply /index</b>"
    INDEX_UNSUPPORTED_TYPE  = "<b>Unsupported message type. Please reply to a valid forwarded message or link.</b>"
    INDEX_PRIVATE_CHANNEL   = "<b>This may be a private channel/group. Make me an admin over there to index the files.</b>"
    INDEX_INVALID_LINK      = "Invalid Link specified."
    INDEX_GENERIC_ERROR     = "Errors - {e}"
    INDEX_ADMIN_CHECK_FAIL  = "<b>Make sure I am an admin in the channel, if the channel is private.</b>"
    INDEX_NOT_ADMIN_GROUP   = "<b> I am not an admin of the group.</b>"
    INDEX_CONFIRM_PROMPT    = "<b>Do you want to index this Channel/Group?\n\nChat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code></b>"
    INDEX_INVITE_LINK_FAIL  = "<b>Make sure I am an admin in the chat and have permission to invite users.</b>"
    INDEX_LOG_REQUEST = (
        "#IndexRequest\n\nBy: {mention} (<code>{user_id}</code>)\n"
        "Chat ID/Username: <code>{chat_id}</code>\nLast Message ID: <code>{last_msg_id}</code>\n"
        "InviteLink: {link}"
    )
    INDEX_THANKS_CONTRIBUTION = "<b>Thank you for the contribution. Wait for my moderators to verify the files.</b>"
    INDEX_CMD_INVALID_REPLY   = "<b>Please reply to a forwarded message or a valid link to use the /index command.</b>"

    SETSKIP_NOT_INT = "Skip number should be an integer."
    SETSKIP_SUCCESS = "Successfully set SKIP number as {skip}"
    SETSKIP_USAGE   = "Give me a skip number."

    INDEX_PROGRESS_START = "Starting to save files. Click 'Cancel' to stop."
    INDEX_PROGRESS_CANCELLED = (
        "Successfully Cancelled!!\n\nSaved <code>{total_files}</code> files to dataBase!\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )
    INDEX_PROGRESS_UPDATE = (
        "Total messages fetched: <code>{current}</code>\nTotal messages saved: <code>{total_files}</code>\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\nDeleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )
    INDEX_ERROR = "Error: {e}"
    INDEX_PROGRESS_DONE = (
        "Successfully saved <code>{total_files}</code> to dataBase!\n"
        "Duplicate Files Skipped: <code>{duplicate}</code>\n"
        "Deleted Messages Skipped: <code>{deleted}</code>\n"
        "Non-Media messages skipped: <code>{no_media_total}</code> (Unsupported Media - `<code>{unsupported}</code>`)\n"
        "Errors Occurred: <code>{errors}</code>\n"
        "Elapsed Time: <code>{formatted_time}</code>"
    )

    # ── Search (plugins/pm_filter_search.py) ──────────────────────────────────
    SEARCH_INVALID_QUERY = (
        "<b>⚠️ Invalid Search Query!</b>\n\n"
        "• Please type at least <b>3 characters</b> of the movie/series name.\n"
        "• Avoid sending only special characters or symbols (like <code>*, !, ?, @, #</code>)."
    )
    SEARCH_NO_IMDB_CAPTION = "Sir! I found something {search}\n\n"
    SPELL_NOT_FOUND        = "I couldn't find any movies related to **{query}**. Try searching on Google or in the request group."
    SPELL_GENERIC_ERROR    = "An error occurred while processing your request. Please try again or check the request group."
    SPELL_NO_VALID_TITLES  = "No valid movie titles found for **{query}**. Try searching on Google or in the request group."
    SPELL_NO_CLOSE_MATCHES = "<b>No close matches found for **{query}**.</b>\n\n<b>Here are some suggestions:</b>"

    # ── Contact (plugins/Extra/contact.py) ────────────────────────────────────
    CONTACT_NO_REPLY      = "Please reply to a message with your feedback or issue."
    CONTACT_FEEDBACK_SENT = "Your feedback has been sent to the admin. Please be patient, the admin will reply soon."

    TALK_USAGE        = "Please provide a secret code after the /talk command. Example: `/talk secretcode123`"
    TALK_INVALID_CODE = "Invalid secret code. Please try again."
    TALK_NO_REPLY = (
        "Please reply to a message with your secret code to send it to the admin. \n"
        "example: <code> /talk abc123 </code>"
    )
    TALK_MESSAGE_SENT = "Your message has been delivered to the admin. Please be patient, the admin will reply soon."

    SECRETCODE_CREATE_UNAUTHORIZED = "You are not authorized to create a secret code."
    SECRETCODE_CREATE_PROMPT       = "Please provide the name for the new secret code."
    SECRETCODE_ALREADY_EXISTS      = "This secret code already exists."
    SECRETCODE_CREATED             = "New secret code has been created successfully:\n\n`{new_code}`"

    SECRETCODE_DELETE_UNAUTHORIZED = "You are not authorized to delete a secret code."
    SECRETCODE_DELETE_PROMPT       = "Please provide the secret code you want to delete."
    SECRETCODE_NOT_FOUND           = "This secret code does not exist."
    SECRETCODE_DELETED             = "Secret code '{code}' has been deleted successfully!"

    SEND_USAGE            = "<b>Usage: /send <target_user_id></b>"
    SEND_USERS_HEADER     = "Users Saved In DB Are:\n\n"
    SEND_SUCCESS          = "<b>Your message has been successfully sent to {mention}.</b>"
    SEND_USER_NOT_STARTED = "<b>This user hasn't started the bot yet!</b>"
    SEND_ERROR            = "<b>Error: {e}</b>"
    SEND_NO_REPLY         = "<b>Use this command as a reply to a message, specifying the target user ID.</b>"

    # ── Check-alive (plugins/Extra/check_alive.py) ────────────────────────────
    ALIVE_MSG        = "**You are very lucky 🤞 I am alive ❤️ Press /start to use me**"
    PING_PLACEHOLDER = "..."
    PING_RESULT      = "Pong!\n{time_taken} ms"

    # ── Envs (plugins/envscommand.py) ─────────────────────────────────────────
    ENV_ADD_USAGE      = "Usage: /add_env {config_name} {key} {value}"
    ENV_ADD_SUCCESS    = "Environment variable <pre> {key} = {value} </pre> added to {config_name}."
    ENV_GET_USAGE      = "Usage: /get_envs {config_name}"
    ENV_GET_EMPTY      = "No environment variables found for {config_name}."
    ENV_GET_LIST       = "Current environment variables for {config_name}:\n<pre>{env_str}</pre>"
    ENV_ALL_HEADER     = "Current Environment Configurations:\n\n"
    ENV_ALL_ITEM       = "<b>{config_name}</b>:\n<pre>{details}</pre>\n\n"
    ENV_ALL_EMPTY      = "No environment configurations found."
    ENV_ALL_ERROR      = "An error occurred while fetching configurations: {error}"
    ENV_UPDATE_USAGE   = "Usage: /update_env {config_name} {key} {value}"
    ENV_UPDATE_SUCCESS = "Environment variable {key} updated to {value} in {config_name}."
    ENV_UPDATE_FAIL    = "Failed to update environment variable {key} in {config_name}."
    ENV_DELETE_USAGE   = "Usage: /delete_env {config_name} {key}"
    ENV_DELETE_SUCCESS = "Environment variable <pre>{key}</pre> deleted from {config_name}."
    ENV_DELETE_FAIL    = "Failed to delete <pre>{key}</pre> from {config_name}. It might not exist."

    # ── Banned (plugins/banned.py) ────────────────────────────────────────────
    BANNED_USER_REPLY = "Sorry Dude, You are Banned to use Me...\nBan Reason: {ban_reason}"
    GRP_DISABLED_NOTICE_BILINGUAL = (
        "CHAT NOT ALLOWED 🐞\n\n"
        "My admins has restricted me from working here ! If you want to know more about it contact support.\n"
        "Reason : <code>{reason}</code>."
    )

    # ── WebApp buttons (plugins/cmd_weappb.py) ────────────────────────────────
    WTRY_ALIVE = "✅ <b>wtry reached this file and the handler is alive.</b>\n\n<b>Source:</b> <code>{source}</code>"
    WEBAPP_NOT_CONFIGURED = (
        "<b>Web App URL is not configured.</b>\n"
        "Set the <code>BASE_URL</code> environment variable to your server URL."
    )
    WEBAPP_MARKUP_ERROR = "<b>❌ Could not build Web App button:</b>\n<code>{error}</code>"
    WEBAPP_SUCCESS = (
        "<b>🎬 AutoFile Media Search</b>\n\n"
        "Tap the button below to open the media search app directly in Telegram.\n\n"
        "<b>Path:</b> <code>{source}</code>"
    )
    WEBAPP_SEND_ERROR = "<b>❌ Failed to send WebApp message:</b>\n<code>{error}</code>"
    WEBAPP_CRASH = "<b>❌ /webapp crashed:</b>\n<code>{error}</code>"

    # ── PM Filter entry point (plugins/pm_filter.py) ──────────────────────────
    PMFILTER_NOT_SEARCH_GROUP = "<b>This is not the search group. Please join the search group by tapping the button below:</b>"
    PMFILTER_GROUP_BAN_NOTICE = (
        "<b>This Group Ban Anytime so Join Another Private Group.</b>\n"
        "<i>👉🏻Link(1) : https://t.me/+5pa88NB3YAhiNDQ1 </i>\n"
        "<i>👉🏻Link(2) : https://t.me/+13JZ5BMiiSM4ZmE1 </i>\n\n"
        " Wait 10 second Bot is finding Movie"
    )
    PMFILTER_FLOODWAIT         = "<b>FloodWait detected. Please wait {seconds} seconds before trying again.</b>"
    PMFILTER_UNEXPECTED_ERROR  = "<b>An unexpected error occurred. Please try again later.\n\nDetails: {error}</b>"

    # ── Inline search (plugins/inline.py) ─────────────────────────────────────
    INLINE_NOT_SUBSCRIBED = "You must subscribe to use this bot"
    INLINE_EMPTY_QUERY    = "📂 Type any movie or web series name to search."
    INLINE_SEARCH_ERROR   = "Error occurred"
    INLINE_RESULTS_FOUND  = "Results - {total_results}"
    INLINE_RESULTS_SUFFIX = " for '{query}'"
    INLINE_NO_RESULTS     = "No results"


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
    BTN_SHARE        = "➕ दोस्तों के साथ शेयर करें ➕"
    BTN_SEARCH       = "🔎 खोजें 🧐"
    BTN_GROUP        = "✪ ग्रुप ✪"
    BTN_HELP         = "🙆🏻 सहायता 🦾"
    BTN_ABOUT        = "♥️ जानकारी ♥️"
    BTN_ADD_TO_GROUP = "➕ ग्रुप में जोड़ें ➕"
    BTN_BACK         = "◀️ वापस"
    BTN_MAIN_MENU    = "🏠 मुख्य मेनू"
    BTN_CLOSE        = "✖️ बंद करें"
    BTN_LANGUAGE     = "🌐 भाषा"
    BTN_JOIN_CHANNEL = "⚠️ अपडेट चैनल जॉइन करें ⚠️"
    BTN_TRY_AGAIN    = "🔄 फिर कोशिश करें"
    BTN_VERIFY       = "✅ सत्यापित करें"
    BTN_VERIFY_HOW   = "❓ सत्यापन कैसे करें"
    BTN_DONATE       = "💳 दान करें"
    BTN_GET_AGAIN    = "🔁 फ़ाइल फिर से पाएं"
    BTN_SEND_RECEIPT = "📧 भुगतान रसीद भेजें 🧾"
    BTN_YES          = "✅ हाँ"
    BTN_CANCEL       = "❌ रद्द करें"
    BTN_CLOSE_LOCK   = "🔐 बंद करें"
    BTN_GET_ALL_FILES = "सभी फ़ाइलें/एपिसोड पाएं"

    BTN_CAT_SEARCH   = "🔍 खोज और फ़ाइलें"
    BTN_CAT_FILTERS  = "⚙️ फ़िल्टर"
    BTN_CAT_CONNECT  = "🔗 कनेक्शन"
    BTN_CAT_EXTRA    = "🎛️ अतिरिक्त सुविधाएं"
    BTN_CAT_FSUB     = "🔐 बाध्य सदस्यता"
    BTN_CAT_ADMIN    = "🛠 समूह एडमिन"

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
    IMDB_SEARCHING          = "ImDB पर खोज रहे हैं"
    IMDB_NO_RESULTS         = "कोई परिणाम नहीं मिला"
    IMDB_FOUND              = "यह रहा जो मुझे IMDb पर मिला"
    IMDB_GIVE_NAME          = "मुझे मूवी / सीरीज़ का नाम दें"
    IMDB_NO_RESULTS_CAPTION = "कोई परिणाम नहीं"

    BATCH_USAGE             = "सही फॉर्मेट में लिखें।\nउदाहरण: `/batch https://t.me/c/123456789/1 https://t.me/c/123456789/2`।"
    BATCH_INVALID_LINKS     = "अमान्य लिंक दिए गए हैं।"
    BATCH_DIFFERENT_CHATS   = "सभी लिंक एक ही चैट के होने चाहिए।"
    BATCH_CHAT_ACCESS_ERROR = "चैट एक्सेस करने में त्रुटि। सुनिश्चित करें कि बॉट के पास एडमिन एक्सेस है।"
    BATCH_ASK_NAME          = "इस बैच के लिए एक नाम दें।"
    BATCH_ASK_OPTIONAL_MSG  = "अब एक वैकल्पिक संदेश दें (छोड़ने के लिए 'pass' टाइप करें)।"
    BATCH_PROCESSING        = "आपका बैच प्रोसेस किया जा रहा है..."
    BATCH_CREATED           = "बैच सफलतापूर्वक बन गया!\nबैच नाम: {name}\nइसमें `{count}` फ़ाइलें हैं।\nलिंक: {link}"


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
