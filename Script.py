class script(object):
    START_TXT = """
<b><blockquote>👋 Hᴇʟʟᴏ <i>{}</i>,  
✨ ᴍʏ ɴᴀᴍᴇ ɪꜱ <a href="https://t.me/{}"><b>{}</b></a> ✨</blockquote>  

<b><i>⚡ I am your ultimate File Sharing Bot powered by <a href="https://t.me/filmykeedha">@FilmyKeedha</a> ⚡</i></b>  
<pre>
📚 With the largest media database on Telegram, we've proudly served users since 2021 and are committed to staying completely FREE in the future!

Hindi:
मैं आपका फ़ाइल शेयरिंग बॉट हूँ।
📚 टेलीग्राम पर सबसे बड़े मीडिया डेटाबेस के साथ, हम 2021 से उपयोगकर्ताओं को निःशुल्क सेवा प्रदान कर रहे हैं और भविष्य में भी पूरी तरह से मुफ़्त रहने की योजना है!
</pre>
"""
    
    HELP_TXT = """ <b>Hᴇʏ {} , What's up?</b>

<pre>
⚫ How to use this bot:  
- I know you're wondering how to use this bot. Do you need a Ph.D. in Telegram Bots? 😆 Just kidding!  
- To use it, simply:  
   • Join the search group.  
   • Type the name of the movie or web series you want.  
That's it! 🎬  

⚫ Important Note:  
If you'd like to support this bot's future operations:  
   • Share it with others.  
   • Click on the "Donate" button or use the /donate command to help financially.
</pre>

<b>Hindi:</b>
<pre>
⚫ बॉट का उपयोग कैसे करें:  
- मुझे पता है कि आप सोच रहे होंगे कि बॉट का उपयोग कैसे करें। क्या टेलीग्राम बॉट्स में पीएचडी करनी होगी? 😆 बस मजाक कर रहा हूँ!  
- उपयोग के लिए:  
   • सर्च ग्रुप में शामिल हों।  
   • जो मूवी या वेब सीरीज देखनी है, उसका नाम टाइप करें।  
बस इतना ही! 🎬  

⚫ एक और खास बात:  
अगर आप इस बोट को भविष्य में भी चलाने में मदद करना चाहते हैं:  
   • इसे दूसरों के साथ शेयर करें।  
   • "Donate" बटन पर क्लिक करें या /donate कमांड का उपयोग करके आर्थिक मदद करें।
</pre>
Use /help for commands 
"""
    ABOUT_TXT = """✯ 𝙼𝚈 𝙽𝙰𝙼𝙴: ᏒᏗᏕᏂᎷᎥ
✯ 𝙂𝙍𝙊𝙐𝙋: <a href=https://www.instagram.com/reel/CzDbEApSkZe>𝐅𝐢𝐥𝐦𝐲𝐤𝐞𝐞𝐝𝐡𝐚_𝐚𝐬𝐤</a>
✯ 𝙈𝘼𝙄𝙉 𝘾𝙃𝘼𝙉𝙉𝙀𝙇: <a href=https://t.me/Filmykeedha>𝐅𝐢𝐥𝐦𝐲𝐤𝐞𝐞𝐝𝐡𝐚</a>
✯ 𝘾𝙍𝙀𝘼𝙏𝙀𝙍: <a href=https://t.me/pankaj_patel_p>Ꭾᥲᥒⲕᥲ၂👮🏼❤️🚔</a>
✯ 𝗠𝗼𝘃𝗶𝗲 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲:𝐇𝐢𝐧𝐝𝐢, 𝐄𝐧𝐠𝐥𝐢𝐬𝐡, 𝐓𝐚𝐦𝐢𝐥 𝐀𝐧𝐝 𝐌𝐚𝐧𝐲 𝐌𝐨𝐫𝐞 𝐌𝐨𝐯𝐢𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞
✯ 𝗕𝗼𝘁 𝗟𝗮𝗻𝗴𝘂𝗮𝗴𝗲: 𝐇𝐢𝐧𝐝𝐢 𝐚𝐧𝐝 𝐄𝐧𝐠𝐥𝐢𝐬𝐡
✯ 𝙱𝚄𝙸𝙻𝙳 𝚂𝚃𝙰𝚃𝚄𝚂: V1.0.1 [ 𝙱𝙴𝚃𝙰 ]"""
    SOURCE_TXT = """<b>NOTE:</b>
- ᏒᏗᏕᏂᎷᎥ is an open source project. 
-   

<b>DEVS:</b>
- <a href=https://www.instagram.com/reel/CzDbEApSkZe>Ꭾᥲᥒⲕᥲ၂👮🏼❤️🚔</a>"""
    MANUELFILTER_TXT = """Help: <b>Filters</b>

- Filter is the feature were users can set automated replies for a particular keyword and ᏒᏗᏕᏂᎷᎥ will respond whenever that keyword hits the message

<b>NOTE:</b>
1. BOT should have admin privillage.
2. Only admins can add filters in a chat.
3. Alert buttons have a limit of 64 characters.

<b>Commands and Usage:</b>
• /addfilter - <code>add a filter in chat</code>
• /filters - <code>list all the filters of a chat</code>
• /delete_filter - <code>delete a specific filter in chat</code>
• /delallfilters - <code>delete the whole filters in a chat (chat owner only)</code>"""
    BUTTON_TXT = """Help: <b>Buttons</b>

- Supports both url and alert inline buttons.

<b>NOTE:</b>
1. Telegram will not allows you to send buttons without any content, so content is mandatory.
2. BOT supports buttons with any telegram media type.
3. Buttons should be properly parsed as markdown format

<b>URL buttons:</b>
<code>[Button Text](buttonurl:https://t.me/Filmykeedha)</code>

<b>Alert buttons:</b>
<code>[Button Text](buttonalert:This is an alert message)</code>"""
    AUTOFILTER_TXT = """Help: <b>Auto Filter</b>

<b>NOTE:</b>
1. Make me the admin of your channel if it's private.
2. Make sure that your channel does not contains camrips, porn and fake files.
3. Forward the last message to me with quotes.
4. Reply That Message With /index Command.
 I'll add all the files in that channel to my db."""
    CONNECTION_TXT = """Help: <b>Connections</b>

- Used to connect bot to PM for managing filters 
- it helps to avoid spamming in groups.

<b>NOTE:</b>
1. Only admins can add a connection.
2. Send <code>/connect</code> for connecting me to ur PM

<b>Commands and Usage:</b>
• /connect  - <code>connect a particular chat to your PM</code>
• /disconnect  - <code>disconnect from a chat</code>
• /connections - <code>list all your connections</code>"""
    EXTRAMOD_TXT = """Help: <b>Extra Modules</b>

<b>NOTE:</b>
these are the extra features of ᏒᏗᏕᏂᎷᎥ

<b>Commands and Usage:</b>
• /id - <pre>get id of a specified user or channel (if you reply to a channel post).</pre>
• /info  - <pre>get information about a user.</pre>
• /imdb  - <pre>get the film information from various sources.</pre>
• /cpost - <pre>Post in channel via bot. </pre>
• /ppost - <pre>Post in Channel private post (can't copy or forward) </pre>
• /report - <pre>Reply to any message you want to report or inform Admin about that. </pre>
• /talk - <pre>Talk to Admin with a special code. it can deliver Admin if you report any issue.</pre>
• <b>Yaad Nahi Aa Raha Hai 😛😄</b>"""
    ADMIN_TXT = """Help: <b>Admin mods</b>

<b>NOTE:</b>
This module only works for my admins

<b>Commands and Usage:</b>
• /logs - <code>to get the rescent errors</code>
• /stats - <code>to get status of files in db.</code>
• /delete - <code>to delete a specific file from db.</code>
• /users - <code>to get list of my users and ids.</code>
• /chats - <code>to get list of the my chats and ids </code>
• /leave  - <code>to leave from a chat.</code>
• /disable  -  <code>do disable a chat.</code>
• /ban  - <code>to ban a user.</code>
• /unban  - <code>to unban a user.</code>
• /channel - <code>to get list of total connected channels</code>
• /broadcast - <code>to broadcast a message to all users</code>
• /send - send anything to users
• /create_code - Create talk code
• /delete_code - Delete talk code"""
    STATUS_TXT = """★ 𝚃𝙾𝚃𝙰𝙻 𝙵𝙸𝙻𝙴𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝚄𝚂𝙴𝚁𝚂: <code>{}</code>
★ 𝚃𝙾𝚃𝙰𝙻 𝙲𝙷𝙰𝚃𝚂: <code>{}</code>
★ 𝚄𝚂𝙴𝙳 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> 𝙼𝚒𝙱
★ 𝙵𝚁𝙴𝙴 𝚂𝚃𝙾𝚁𝙰𝙶𝙴: <code>{}</code> 𝙼𝚒𝙱"""
    LOG_TEXT_G = """#NewGroup
Group = {}(<code>{}</code>)
Total Members = <code>{}</code>
Added By - {}
"""
    LOG_TEXT_P = """#NewUser
ID - <code>{}</code>
Name - {}
"""
    DELETEMSG = """
<pre><b>⏳Deleting In 60 Minutes 🗑️</b></pre>
<pre>To save your files, do one of the following 👇🏻
├── 📤 Forward to your friends
├── 📲 Forward to saved message
├── 👥 Forward to our dumb group</pre>
<a href="https://t.me/Filmykeedha/306">👉🏻ᴅᴜᴍʙ ɢʀᴏᴜᴘ👈🏻</a>"""
    MELCOW_ENG = """
<b>Hᴇʟʟᴏ {} 😍 
Welcome 🤗 to <pre> {} </pre>
Chaliye shuru karte hai 
Ab Aayega Majaa 🥳. 
Tap Button Below 👇🏻 To Find Active Group</b>"""

    CAPTION = """
<pre>✨ 𝗡𝗮𝗺𝗲</pre>
🎥 <b>@Filmykeedha</b> <a href='https://t.me/Filmykeedha/306'><b>{file_name}</b></a>

<pre>✨ 𝗦𝗶𝘇𝗲</pre>
📂 <b><a href='https://t.me/Filmykeedha/306'>{file_size}</a></b>

🔗 <b><a href='https://t.me/Filmykeedha'>𝗝𝗼𝗶𝗻 𝐅𝐢𝐥𝐦𝐲𝐤𝐞𝐞𝐝𝐡𝐚 🔥</a></b>  
🎁 <b><a href='https://t.me/Filmykeedha/306'>💎 Tap Here for an Exclusive Surprise 💎</a></b>  

<pre>💖 Support Us by Donating 🙏🏻</pre>"""
