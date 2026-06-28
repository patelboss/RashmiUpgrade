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
        "• Tap <b>Search 🔍</b> in the inline button to search any movie or file.\n"
        "• In any connected group, just <b>type the movie name</b> — results appear automatically.\n"
        "• Use <b>/index</b> (reply to last channel msg) to index a channel's files into the database.\n"
        "• <b>/setskip N</b> — Skip first N messages while indexing."
    )
    HELP_CAT_FILTERS = (
        "<b>⚙️ Filters</b>\n\n"
        "Filters let the bot auto-reply to specific keywords.\n\n"
        "<b>Commands:</b>\n"
        "• /addfilter — Add a keyword filter\n"
        "• /filters — List all filters in a chat\n"
        "• /delete_filter — Remove a specific filter\n"
        "• /delallfilters — Remove all filters (owner only)\n\n"
        "<b>NOTE:</b> Bot must have admin privileges."
    )
    HELP_CAT_CONNECT = (
        "<b>🔗 Connections</b>\n\n"
        "Connect the bot to your group PM so you can manage filters without spamming the group.\n\n"
        "<b>Commands:</b>\n"
        "• /connect [group_id] — Connect group to your PM\n"
        "• /disconnect — Disconnect from a group\n"
        "• /connections — List all your connections\n\n"
        "<b>NOTE:</b> Only group admins can connect."
    )
    HELP_CAT_EXTRA = (
        "<b>🎛️ Extra Features</b>\n\n"
        "• /id — Get ID of a user or channel\n"
        "• /info — Get user details\n"
        "• /imdb — Fetch movie info from IMDB\n"
        "• /cpost — Post in a channel via bot\n"
        "• /ppost — Private post (no copy/forward)\n"
        "• /report — Report an issue to admin\n"
        "• /talk — Talk to admin with a code\n"
        "• /ping — Check bot response speed\n"
        "• /alive — Check if bot is online"
    )
    HELP_CAT_FSUB = (
        "<b>🔐 Force Subscribe</b>\n\n"
        "• /fsub [channel_id] — Force users to join a channel\n"
        "• /nofsub — Remove force subscribe\n"
        "• /id — Get channel ID\n\n"
        "Users must join the set channel before they can use the bot."
    )
    HELP_CAT_ADMIN = (
        "<b>🛠 Admin Commands</b>\n\n"
        "• /stats — Database status\n"
        "• /logs — Get recent error logs\n"
        "• /delete — Delete a file from DB\n"
        "• /deleteall — Delete all indexed files\n"
        "• /users — List all users\n"
        "• /chats — List all chats\n"
        "• /ban — Ban a user\n"
        "• /unban — Unban a user\n"
        "• /leave — Leave a chat\n"
        "• /disable — Disable a chat\n"
        "• /broadcast — Broadcast to all users\n"
        "• /grp_broadcast — Broadcast to all groups\n"
        "• /scrub — Bulk delete DB files by pattern\n"
        "• /channel — List indexed channels\n"
        "• /restart — Restart the bot"
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

    # Help menu category buttons
    BTN_CAT_SEARCH     = "🔍 Search & Files"          # Help menu — category button
    BTN_CAT_FILTERS    = "⚙️ Filters"                # Help menu — category button
    BTN_CAT_CONNECT    = "🔗 Connections"             # Help menu — category button
    BTN_CAT_EXTRA      = "🎛️ Extra Features"          # Help menu — category button
    BTN_CAT_FSUB       = "🔐 Force Subscribe"         # Help menu — category button
    BTN_CAT_ADMIN      = "🛠 Admin"                   # Help menu — category button (admins only)


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

    BTN_CAT_SEARCH   = "🔍 खोज और फ़ाइलें"              # Help — search category
    BTN_CAT_FILTERS  = "⚙️ फ़िल्टर"                     # Help — filters category
    BTN_CAT_CONNECT  = "🔗 कनेक्शन"                     # Help — connections category
    BTN_CAT_EXTRA    = "🎛️ अतिरिक्त सुविधाएं"          # Help — extra category
    BTN_CAT_FSUB     = "🔐 बाध्य सदस्यता"               # Help — fsub category
    BTN_CAT_ADMIN    = "🛠 एडमिन"                        # Help — admin category


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
