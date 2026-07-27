
import logging

from pyrogram import Client, filters
from info import ADMINS, DEBUG_MODE  # import the ADMINS list and DEBUG_MODE flag from info
from database.users_chats_db import db #, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
from langs.i18n import get, DEFAULT_LANG

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Define a dictionary to store secret codes (could be persisted in a database if needed)
secret_codes = {}


async def _user_lang(user) -> str:
    """Resolve a user's language, falling back to DEFAULT_LANG for anonymous callers."""
    if not user:
        return DEFAULT_LANG
    return await db.get_user_lang(user.id)


@Client.on_message(filters.command(['feedback', 'report']))
async def feedback(client, message):
    """
    Handle feedback or issue reporting with optional file attachments.
    User should reply to a message to send feedback or issues.
    """
    lang = await _user_lang(message.from_user)
    # Ensure the message contains a feedback message
    if not message.reply_to_message:
        if DEBUG_MODE:
            logger.info("[CONTACT] /feedback: no reply given | user_id=%s", message.from_user.id)
        return await message.reply(get(lang, "CONTACT_NO_REPLY"))

    feedback_message = message.reply_to_message.text
    user_details = f"Feedback from {message.from_user.username} (ID: {message.from_user.id})"

    # Prepare the feedback message to send
    feedback_text = f"{user_details}\n\n{feedback_message}"

    # Check if the user has attached a file (photo, video, document, etc.)
    if message.reply_to_message.document:
        # If the message contains a document (e.g., file), forward it to admin
        document = message.reply_to_message.document
        for admin in ADMINS:
            await client.send_document(admin, document.file_id, caption=feedback_text)
    elif message.reply_to_message.photo:
        # If the message contains a photo, forward it to admin
        photo = message.reply_to_message.photo
        for admin in ADMINS:
            await client.send_photo(admin, photo.file_id, caption=feedback_text)
    elif message.reply_to_message.video:
        # If the message contains a video, forward it to admin
        video = message.reply_to_message.video
        for admin in ADMINS:
            await client.send_video(admin, video.file_id, caption=feedback_text)
    elif message.reply_to_message.audio:
        # If the message contains an audio, forward it to admin
        audio = message.reply_to_message.audio
        for admin in ADMINS:
            await client.send_audio(admin, audio.file_id, caption=feedback_text)
    elif message.reply_to_message.voice:
        # If the message contains a voice message, forward it to admin
        voice = message.reply_to_message.voice
        for admin in ADMINS:
            await client.send_voice(admin, voice.file_id, caption=feedback_text)
    elif message.reply_to_message.sticker:
        # If the message contains a sticker, forward it to admin
        sticker = message.reply_to_message.sticker
        for admin in ADMINS:
            await client.send_sticker(admin, sticker.file_id, caption=feedback_text)
    else:
        # If no file is attached, just send the feedback text
        for admin in ADMINS:
            await client.send_message(admin, feedback_text)

    if DEBUG_MODE:
        logger.info("[CONTACT] /feedback: delivered | user_id=%s", message.from_user.id)

    # Notify the user that their feedback has been delivered
    await message.reply(get(lang, "CONTACT_FEEDBACK_SENT"))

@Client.on_message(filters.command('talk') & filters.private)
async def talk(client, message):
    """
    Command to interact using a secret code or talk to admin.
    User should reply to a message to send the message.
    """
    lang = await _user_lang(message.from_user)
    # Ensure the message contains a secret code
    command_parts = message.text.split()

    if len(command_parts) < 2:
        return await message.reply(get(lang, "TALK_USAGE"))

    secret_code = command_parts[1]

    # Validate the secret code
    if secret_code not in secret_codes:
        if DEBUG_MODE:
            logger.info("[CONTACT] /talk: invalid code | user_id=%s", message.from_user.id)
        return await message.reply(get(lang, "TALK_INVALID_CODE"))

    # Ensure the user is replying to a message
    if not message.reply_to_message:
        return await message.reply(get(lang, "TALK_NO_REPLY"))

    # Get the message that the user replied to
    user_message = message.reply_to_message.text
    user_id = message.from_user.id
    user_details = f"Message from {message.from_user.username} (ID: {user_id})"

    # Prepare the message to be forwarded to the admin(s)
    forwarded_message = f"{user_details}\n\n{user_message}"

    # Check if the user has attached a file (photo, video, document, etc.)
    if message.reply_to_message.document:
        # If the message contains a document (e.g., file), forward it to admin
        document = message.reply_to_message.document
        for admin in ADMINS:
            await client.send_document(admin, document.file_id, caption=forwarded_message)
    elif message.reply_to_message.photo:
        # If the message contains a photo, forward it to admin
        photo = message.reply_to_message.photo
        for admin in ADMINS:
            await client.send_photo(admin, photo.file_id, caption=forwarded_message)
    elif message.reply_to_message.video:
        # If the message contains a video, forward it to admin
        video = message.reply_to_message.video
        for admin in ADMINS:
            await client.send_video(admin, video.file_id, caption=forwarded_message)
    elif message.reply_to_message.audio:
        # If the message contains an audio, forward it to admin
        audio = message.reply_to_message.audio
        for admin in ADMINS:
            await client.send_audio(admin, audio.file_id, caption=forwarded_message)
    elif message.reply_to_message.voice:
        # If the message contains a voice message, forward it to admin
        voice = message.reply_to_message.voice
        for admin in ADMINS:
            await client.send_voice(admin, voice.file_id, caption=forwarded_message)
    elif message.reply_to_message.sticker:
        # If the message contains a sticker, forward it to admin
        sticker = message.reply_to_message.sticker
        for admin in ADMINS:
            await client.send_sticker(admin, sticker.file_id, caption=forwarded_message)
    else:
        # If no file is attached, just send the text message
        for admin in ADMINS:
            await client.send_message(admin, forwarded_message)

    if DEBUG_MODE:
        logger.info("[CONTACT] /talk: delivered | user_id=%s", user_id)

    # Notify the user that their message has been delivered
    await message.reply(get(lang, "TALK_MESSAGE_SENT"))

@Client.on_message(filters.command('create_code') & filters.private & filters.user(ADMINS))
async def create_code(client, message):
    """
    Admin command to create a new secret code.
    """
    lang = await _user_lang(message.from_user)
    if message.from_user.id not in ADMINS:
        return await message.reply(get(lang, "SECRETCODE_CREATE_UNAUTHORIZED"))

    await message.reply(get(lang, "SECRETCODE_CREATE_PROMPT"))
    response = await client.listen(message.chat.id)
    new_code = response.text.strip()

    if new_code in secret_codes:
        return await message.reply(get(lang, "SECRETCODE_ALREADY_EXISTS"))

    # Generate a unique secret code (simple example)
    secret_codes[new_code] = True  # You can also add expiration or validation if needed
    if DEBUG_MODE:
        logger.info("[CONTACT] /create_code: created | admin_id=%s", message.from_user.id)
    await message.reply(get(lang, "SECRETCODE_CREATED", new_code=new_code))  # In monospace text for easy copy

@Client.on_message(filters.command('delete_code') & filters.private & filters.user(ADMINS))
async def delete_code(client, message):
    """
    Admin command to delete a secret code.
    """
    lang = await _user_lang(message.from_user)
    if message.from_user.id not in ADMINS:
        return await message.reply(get(lang, "SECRETCODE_DELETE_UNAUTHORIZED"))

    await message.reply(get(lang, "SECRETCODE_DELETE_PROMPT"))
    response = await client.listen(message.chat.id)
    code_to_delete = response.text.strip()

    if code_to_delete not in secret_codes:
        return await message.reply(get(lang, "SECRETCODE_NOT_FOUND"))

    del secret_codes[code_to_delete]
    if DEBUG_MODE:
        logger.info("[CONTACT] /delete_code: deleted | admin_id=%s", message.from_user.id)
    await message.reply(get(lang, "SECRETCODE_DELETED", code=code_to_delete))

@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(client, message):
    """
    Admin command to send a message to any user who has interacted with the bot.
    The admin must reply to a message and specify the target user ID.
    This handles sending media like photos, videos, documents along with captions,
    without the 'Forwarded from' tag.
    """
    lang = await _user_lang(message.from_user)
    if message.reply_to_message:
        # Extract the target user ID from the command
        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2:
            return await message.reply_text(get(lang, "SEND_USAGE"))

        target_id = command_parts[1]

        # Initialize the response message
        out = get(lang, "SEND_USERS_HEADER")
        success = False

        try:
            # Check if the target user exists
            target_user = await client.get_users(target_id)

            # Fetch all users from the DB
            users_cursor = await db.get_all_users()  # This returns a cursor, not a list
            user_ids_in_db = []

            # Properly iterate through the cursor and collect user IDs
            async for usr in users_cursor:
                user_ids_in_db.append(str(usr['id']))

            # Check if the target user is in the database
            if str(target_user.id) in user_ids_in_db:
                # Forward the admin's reply message to the target user without forward tag
                if message.reply_to_message.photo:
                    # If the message contains a photo
                    await message.reply_to_message.copy(target_user.id, caption=message.reply_to_message.caption)
                elif message.reply_to_message.video:
                    # If the message contains a video
                    await message.reply_to_message.copy(target_user.id, caption=message.reply_to_message.caption)
                elif message.reply_to_message.document:
                    # If the message contains a document
                    await message.reply_to_message.copy(target_user.id, caption=message.reply_to_message.caption)
                else:
                    # If the message does not contain media (text only)
                    await message.reply_to_message.copy(target_user.id)
                success = True
            else:
                success = False

            if success:
                if DEBUG_MODE:
                    logger.info("[CONTACT] /send: delivered | admin_id=%s target_id=%s", message.from_user.id, target_user.id)
                # Inform the admin that the message was successfully sent
                await message.reply_text(get(lang, "SEND_SUCCESS", mention=target_user.mention))
            else:
                # Inform the admin if the user hasn't started the bot yet
                await message.reply_text(get(lang, "SEND_USER_NOT_STARTED"))

        except Exception as e:
            # Handle any errors that occur during the process
            logger.exception(e)
            await message.reply_text(get(lang, "SEND_ERROR", e=e))
    else:
        # Inform the admin if the command is not used with a reply
        await message.reply_text(get(lang, "SEND_NO_REPLY"))
