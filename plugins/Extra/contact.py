
from pyrogram import Client, filters
from info import ADMINS  # import the ADMINS list from info
from database.users_chats_db import db #, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user

# Define a dictionary to store secret codes (could be persisted in a database if needed)
secret_codes = {}

@Client.on_message(filters.command(['feedback', 'report']))
async def feedback(client, message):
    """
    Handle feedback or issue reporting with optional file attachments.
    User should reply to a message to send feedback or issues.
    """
    # Ensure the message contains a feedback message
    if not message.reply_to_message:
        return await message.reply("Please reply to a message with your feedback or issue.")

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
    
    # Notify the user that their feedback has been delivered
    await message.reply("Your feedback has been sent to the admin. Please be patient, the admin will reply soon.")

@Client.on_message(filters.command('talk') & filters.private)
async def talk(client, message):
    """
    Command to interact using a secret code or talk to admin.
    User should reply to a message to send the message.
    """
    # Ensure the message contains a secret code
    command_parts = message.text.split()
    
    if len(command_parts) < 2:
        return await message.reply("Please provide a secret code after the /talk command. Example: `/talk secretcode123`")
    
    secret_code = command_parts[1]
    
    # Validate the secret code
    if secret_code not in secret_codes:
        return await message.reply("Invalid secret code. Please try again.")
    
    # Ensure the user is replying to a message
    if not message.reply_to_message:
        return await message.reply("Please reply to a message with your secret code to send it to the admin. \nexample: <code> /talk abc123 </code>")
    
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
    
    # Notify the user that their message has been delivered
    await message.reply("Your message has been delivered to the admin. Please be patient, the admin will reply soon.")

@Client.on_message(filters.command('create_code') & filters.private & filters.user(ADMINS))
async def create_code(client, message):
    """
    Admin command to create a new secret code.
    """
    if message.from_user.id not in ADMINS:
        return await message.reply("You are not authorized to create a secret code.")
    
    await message.reply("Please provide the name for the new secret code.")
    response = await client.listen(message.chat.id)
    new_code = response.text.strip()
    
    if new_code in secret_codes:
        return await message.reply("This secret code already exists.")
    
    # Generate a unique secret code (simple example)
    secret_codes[new_code] = True  # You can also add expiration or validation if needed
    await message.reply(f"New secret code has been created successfully:\n\n`{new_code}`")  # In monospace text for easy copy

@Client.on_message(filters.command('delete_code') & filters.private & filters.user(ADMINS))
async def delete_code(client, message):
    """
    Admin command to delete a secret code.
    """
    if message.from_user.id not in ADMINS:
        return await message.reply("You are not authorized to delete a secret code.")
    
    await message.reply("Please provide the secret code you want to delete.")
    response = await client.listen(message.chat.id)
    code_to_delete = response.text.strip()

    if code_to_delete not in secret_codes:
        return await message.reply("This secret code does not exist.")

    del secret_codes[code_to_delete]
    await message.reply(f"Secret code '{code_to_delete}' has been deleted successfully!")

@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(client, message):
    """
    Admin command to send a message to any user who has interacted with the bot.
    The admin must reply to a message and specify the target user ID.
    This handles sending media like photos, videos, documents along with captions,
    without the 'Forwarded from' tag.
    """
    if message.reply_to_message:
        # Extract the target user ID from the command
        command_parts = message.text.split(" ", 1)
        if len(command_parts) < 2:
            return await message.reply_text("<b>Usage: /send <target_user_id></b>")

        target_id = command_parts[1]

        # Initialize the response message
        out = "Users Saved In DB Are:\n\n"
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
                # Inform the admin that the message was successfully sent
                await message.reply_text(f"<b>Your message has been successfully sent to {target_user.mention}.</b>")
            else:
                # Inform the admin if the user hasn't started the bot yet
                await message.reply_text("<b>This user hasn't started the bot yet!</b>")

        except Exception as e:
            # Handle any errors that occur during the process
            await message.reply_text(f"<b>Error: {e}</b>")
    else:
        # Inform the admin if the command is not used with a reply
        await message.reply_text("<b>Use this command as a reply to a message, specifying the target user ID.</b>")
