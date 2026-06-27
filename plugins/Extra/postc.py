from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChatAdminRequired
from plugins.Extra.Cscript import TEXTS
import random
import re
import asyncio
# ------------------------ Command Handler ------------------------
@Client.on_message(filters.command(["cpost", "ppost"]))
async def post_message(client, message):
    command_parts = message.text.split()

    # Default to HTML parse mode
    parse_mode = ParseMode.HTML

    # If 'm' is provided as the first argument, set parse mode to Markdown
    if len(command_parts) > 1 and command_parts[1].lower() == 'm':
        parse_mode = ParseMode.MARKDOWN
        command_parts.pop(1)  # Remove the 'm' argument

    if len(command_parts) < 2 or not message.reply_to_message:
        await message.reply(TEXTS["no_message_to_post"], parse_mode=ParseMode.HTML)
        return

    channel_id = command_parts[1]

    if not channel_id.startswith("-100"):
        await message.reply(TEXTS["invalid_channel_id"], parse_mode=ParseMode.HTML)
        return

    user_id = message.from_user.id
    result = await is_user_admin_or_owner(client, channel_id, user_id)

    if isinstance(result, bool):
        if not result:
            await message.reply(TEXTS["permission_denied"], parse_mode=ParseMode.HTML)
            return
    elif isinstance(result, dict) and "error" in result:
        await message.reply(f"<b>{result['error']}</b>", parse_mode=ParseMode.HTML)
        return

    replied_message = message.reply_to_message
    caption = replied_message.caption or replied_message.text or ""

    inline_buttons = extract_buttons_from_caption(caption)
    caption_without_buttons = remove_button_links(caption)
    reply_markup = InlineKeyboardMarkup(inline_buttons) if inline_buttons else None

    # Determine if `protect_content` should be used
    protect_content = message.command[0] == "ppost"

    # Send the post
    success, error = await send_post(
        client,
        channel_id,
        replied_message,
        caption_without_buttons,
        reply_markup,
        protect_content,
        parse_mode  # Pass the determined parse mode
    )

    if success:
        await message.reply(TEXTS["post_success"].format(channel_id=channel_id), parse_mode=ParseMode.HTML)
    else:
        await message.reply(TEXTS["failed_to_post"].format(error=error), parse_mode=ParseMode.HTML)

async def send_post(client, channel_id, replied_message, caption_without_buttons, reply_markup, protect_content, parse_mode):
    try:
        if replied_message.photo:
            await client.send_photo(
                chat_id=channel_id,
                photo=replied_message.photo.file_id,
                caption=caption_without_buttons,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                protect_content=protect_content,
            )
        elif replied_message.video:
            await client.send_video(
                chat_id=channel_id,
                video=replied_message.video.file_id,
                caption=caption_without_buttons,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                protect_content=protect_content,
            )
        elif replied_message.document:
            await client.send_document(
                chat_id=channel_id,
                document=replied_message.document.file_id,
                caption=caption_without_buttons,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                protect_content=protect_content,
            )
        elif replied_message.text:
            await client.send_message(
                chat_id=channel_id,
                text=caption_without_buttons,
                parse_mode=parse_mode,
                reply_markup=reply_markup,
                protect_content=protect_content,
                disable_web_page_preview=True,  # Disable web preview for text messages
            )
        else:
            return False, "Unsupported media type"
        return True, None
    except Exception as e:
        return False, str(e)

# ------------------------ Button Extraction and Caption Removal ------------------------

def extract_buttons_from_caption(caption: str):
    """
    Extracts buttons in the format: {BUTTON_TEXT}-{URL}
    """
    button_links = []
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    
    # Using re.findall() to find all matches
    matches = re.findall(pattern, caption)
    
    for text, url in matches:
        button_links.append([InlineKeyboardButton(text=text, url=url)])
    
    return button_links


def remove_button_links(caption: str):
    """
    Removes button links in the format: {BUTTON_TEXT}-{URL} from the caption
    """
    pattern = r"\{(.*?)\}\-{(https?:\/\/[^\s]+)}"
    cleaned_caption = re.sub(pattern, "", caption).strip()
    return cleaned_caption

def get_random_sticker():
    return random.choice(TEXTS["random_sticker"])

async def is_user_admin_or_owner(client, chat_id, user_id):
    """
    Check if the given user is an admin or the owner of a chat (channel or group).

    Args:
        client (Client): The Pyrogram client instance.
        chat_id (str): The ID of the chat to check.
        user_id (int): The ID of the user to check.

    Returns:
        bool: True if the user is an admin or the owner, False otherwise.
        dict: Error message if something goes wrong.
    """
    try:
        # Get chat member information
        member = await client.get_chat_member(chat_id, user_id)

        # Check if the user is an admin or the owner
        if member.status in {ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER}:
            return True
        return False
    except UserNotParticipant:
        return {"error": TEXTS["error_messages"]["UserNotParticipant"]}
    except PeerIdInvalid:
        return {"error": TEXTS["error_messages"]["PeerIdInvalid"]}
    except ChatAdminRequired:
        return {"error": TEXTS["error_messages"]["ChatAdminRequired"]}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
