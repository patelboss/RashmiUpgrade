from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import random
import asyncio
from plugins.Extra.Cscript import TEXTS
from info import ADMINS
# Command to display connection management help
@Client.on_message(filters.command('connection_help'))
async def command_help(client, message: Message):
    help_text = """
<b>🔌 Command Connection Management 🔌</b>
Manage and connect your groups to private messages with these commands:

🔹 <b>/connect [group_id]</b> - <i>Connect your group to your private chat</i>
    ➡️ Use this to link your group with your private chat. Available for both private chats and groups.

🔹 <b>/connections</b> or <b>/connection</b> - <i>Manage connected groups in PM</i>
    ➡️ View or manage the list of connected groups.

🔹 <b>/disconnect</b> - <i>Disconnect a group from your private chat</i>
    ➡️ Stop receiving messages from a connected group.

🔹 <b>/id</b> - <i>Get ID of group, user, or channel</i>
    ➡️ Fetch the ID of a group (in group chat), user (in PM), or channel (from forwarded message).
    
🔹 <b>/settings</b> - <i> to set some settings according to your group</i>
    ➡️ Learn how to change group settings based on your audiance and group members.

✨ Manage your connections easily and stay organized! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

# Command to display filter management help
@Client.on_message(filters.command('filters_help'))
async def filters_help(client, message: Message):
    help_text = """
<b>🎛️ Group Filter Management 🎛️</b>
Manage custom filters for your group with these commands:

🔹 <b>/addf [keyword] [response]</b> - <i>Add a new filter</i>
    ➡️ Set a custom response for a specific keyword.

🔹 <b>/totalf</b> or <b>/viewf</b> - <i>View active filters</i>
    ➡️ See all active filters in your group.

🔹 <b>/delf [keyword]</b> - <i>Delete a specific filter</i>
    ➡️ Remove a filter by its keyword.

🔹 <b>/delallf</b> - <i>Delete all filters in your group</i>
    ➡️ Clear all group filters except global ones.

✨ Efficiently manage your group’s filters! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

# Command to display global filter management help (only for admins)
@Client.on_message(filters.command('Global_Filter_help') & filters.user(ADMINS))
async def global_filter_help(client, message: Message):
    help_text = """
<b>🌟 Global Filter Management 🌟</b>
Manage global filters with these commands:

🔹 <b>/addg [keyword]</b> - Add a new global filter  
🔹 <b>/delg [keyword]</b> - Delete a specific global filter  
🔹 <b>/gfilters</b> - View all active global filters  
🔹 <b>/delallg</b> - Remove all global filters  

✨ Make your bot smarter with global filters! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

# Random sticker function to use in /chelp
def get_random_sticker():
    return random.choice(TEXTS["random_sticker"])

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

# Miscellaneous commands help
@Client.on_message(filters.command('misc'))
async def misc_help(client, message: Message):
    help_text = """
<b>⚙️ Miscellaneous Commands ⚙️</b>
Interact with the bot and gather information using these commands:

🔹 <b>/Info</b> - <i>Get detailed information about yourself</i>
    ➡️ Fetch your user ID, username, and other details.

🔹 <b>/Alive</b> - <i>Check if the bot is online</i>
    ➡️ Verify if the bot is responsive and online.

🔹 <b>/Ping</b> - <i>Check the bot's ping</i>
    ➡️ Measure the bot's connection speed in milliseconds.

🔹 <b>/Telegraph</b> - <i>Get a shareable photo link</i>
    ➡️ Upload a photo to get a Telegraph link.

🔹 <b>/Stickerid</b> - <i>Get the ID of a sticker</i>
    ➡️ Fetch the unique ID of a sticker.

🔹 <b>/Getfileid</b> - <i>Get the file ID of any file</i>
    ➡️ Retrieve the file ID for any media sent to the bot.

✨ Use these commands to interact with the bot and enhance your experience! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

# Command to show contact help (feedback, tokens, etc.)
@Client.on_message(filters.command('contact_help'))
async def contact_help(client, message: Message):
    help_text = """
<b>💬 Contact and Feedback Commands 💬</b>
Here are the commands to report issues, communicate with admins, and manage your tokens:

🔹 <b>/Feedback</b> - <i>Report an issue or give feedback</i>
    ➡️ Send feedback or report issues to the admin by replying to this message.

🔹 <b>/Talk</b> - <i>Initiate a conversation with the admin (requires token)</i>
    ➡️ Use a token provided by the admin to talk directly to them.

🔹 <b>/create_code</b> - <i>Create a talk token (only for admins)</i>
    ➡️ Generate a token that can be shared with users for direct communication.

🔹 <b>/Delete_code</b> - <i>Delete a talk token (only for admins)</i>
    ➡️ Remove an existing talk token to prevent further use.

✨ Use these commands to stay in touch with the admin or report issues! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)


from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('help'))
async def help_command(client, message: Message):
    help_text = """
<b>🆘 Main Help Commands 🆘</b>
Welcome to the bot! Here are the main help commands you can use to explore the bot's features:

🔹 <b>/Index_help</b> - <i>Learn about index-related queries</i>
    ➡️ This command will help you understand how to request files from the bot and manage index settings.

🔹 <b>/Fsub_help</b> - <i>Get help with force subscribe channel</i>
    ➡️ Use this to manage channels that users must subscribe to in order to access your group. Learn how to set, remove, or query the subscription channel.

🔹 <b>/Filter_help</b> - <i>Get help with filters</i>
    ➡️ Learn about how to add, delete, and manage filters in your group or globally.

🔹 <b>/Misc</b> - <i>Access miscellaneous features</i>
    ➡️ Some unique features that may not fit into other categories. This command includes checking the bot's status, user information, and other fun features.

🔹 <b>/Contact_help</b> - <i>Learn how to contact the admin</i>
    ➡️ Know how to report an issue or talk to the admin using tokens, feedback, and more.

🔹 <b>/Chelp</b> - <i>Get help with posting in channels</i>
    ➡️ Learn how to interact with channels and post content through the bot. This will help you post in channels with ease.
    
🔹 <b>/Connection_help</b> - <i>Get help on connecting group to your PM</i>
    ➡️ Learn How to connect Bot to Your PM if you are a admin of any group 

✨ Use these commands to explore the bot's features and enhance your experience! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('Index_help'))
async def index_help(client, message: Message):
    help_text = """
<b>📂 File Indexing Commands 📂</b>
These commands help you manage and request files in the system. Here's how to use them:

🔹 <b>/index</b> - <i>Request a file from the bot</i>
    ➡️ If you have files stored with the bot, you can use this command to request one. The bot will process your request and provide the file you're looking for.

🔹 <b>/Setskip</b> - <i>Set the index skip number</i>
    ➡️ This command allows you to adjust the number of steps the bot will skip when indexing files. You can use this to customize how the bot processes requests and skips files in the indexing system.

✨ Use these commands to manage your files more efficiently and streamline your experience with the bot! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode

@Client.on_message(filters.command('fsub_help'))
async def fsub_help(client, message: Message):
    help_text = """
<b>🔐 Force Subscribe Commands 🔐</b>
These commands allow you to manage force subscription settings for your group:

🔹 <b>/fsub &lt;channel id&gt;</b> - <i>Set a channel to force subscribe users in your group</i>
    ➡️ Use this command to set a channel that users must subscribe to in order to interact with your group. Simply replace `<channel id>` with the actual channel ID.

🔹 <b>/Nofsub</b> - <i>Delete the force subscribe channel</i>
    ➡️ This command removes the currently set forced subscription channel from your group, allowing users to interact without subscribing to a channel.

🔹 <b>/Id</b> - <i>Get your channel's ID</i>
    ➡️ This command returns the ID of the channel you're using, which can be useful when setting or deleting the force subscribe channel.

✨ Use these commands to manage subscriptions and ensure users are following the channels you set! ✨
"""
    await message.reply_text(help_text, parse_mode=ParseMode.HTML)
