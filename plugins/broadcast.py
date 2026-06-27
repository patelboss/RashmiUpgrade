import asyncio
import logging
import datetime
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid
from info import ADMINS
from database.users_chats_db import db
from utils import broadcast_messages, broadcast_messages_group
#from plugins.pm_filter import send_error_log
logger = logging.getLogger("broadcast")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(client, message):
    try:
        # Ask admin for broadcast message with a timeout
        await message.reply_text("You have 120 seconds (2 minutes ) to send your broadcast message (type or forward).")
        try:
            b_msg = await asyncio.wait_for(
                client.ask(chat_id=message.from_user.id, text="Send your broadcast message (type or forward)."),
                timeout=120
            )
        except asyncio.TimeoutError:
            await message.reply_text("⏳ Time's up! Broadcast canceled.")
            return

        forward_msg = b_msg.forward_from or b_msg.forward_from_chat
        users = await db.get_all_users()  # Cursor for users
        sts = await message.reply_text('Broadcasting your messages...')
        total_users = await db.total_users_count()
        done, blocked, deleted, failed, success = 0, 0, 0, 0, 0

        start_time = datetime.datetime.now()

        async for user in users:
            if 'id' in user:
                try:
                    if forward_msg:
                        status, error = await broadcast_messages(user_id=int(user['id']), message=b_msg, forward=True)
                    else:
                        status, error = await broadcast_messages(user_id=int(user['id']), message=b_msg, forward=False)

                    if status:
                        success += 1
                    elif error == "Blocked":
                        blocked += 1
                    elif error == "Deleted":
                        deleted += 1
                    else:
                        failed += 1
                except FloodWait as e:
                    logger.warning(f"FloodWait of {e.value} seconds encountered. Waiting...")
                    await asyncio.sleep(e.value)
                #    await send_error_log(client, "broadcast floodwait waiting", e)
                except InputUserDeactivated:
                    logger.warning(f"User {user['id']} is deactivated.")
                    deleted += 1
                except UserIsBlocked:
                    logger.warning(f"User {user['id']} has blocked the bot.")
                    blocked += 1
                except PeerIdInvalid:
                    logger.warning(f"Invalid peer ID for user {user['id']}.")
                    failed += 1
                except Exception as e:
                #    await send_error_log(client, f"Error broadcasting to user {user['id']}", e)
                    logger.error(f"Error broadcasting to user {user['id']}: {e}")
                    failed += 1

                done += 1
                await asyncio.sleep(1)
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Users: {total_users}\nCompleted: {done}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")

        time_taken = datetime.datetime.now() - start_time
        await sts.edit(f"Broadcast Completed:\n\nTime Taken: {time_taken}\n\nTotal Users: {total_users}\nCompleted: {done}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}\nFailed: {failed}")
    except Exception as e:
        logger.error(f"Error in pm_broadcast: {e}")
        await message.reply_text("An error occurred during the PM broadcast.")


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    try:
        # Ask admin for broadcast message with a timeout
        await message.reply_text("You have 120 seconds(2 minutes)to send your broadcast message (type or forward).")
        try:
            b_msg = await asyncio.wait_for(
                client.ask(chat_id=message.from_user.id, text="Send your broadcast message (type or forward)."),
                timeout=120
            )
        except asyncio.TimeoutError:
            await message.reply_text("⏳ Time's up! Broadcast canceled.")
            return

        forward_msg = b_msg.forward_from or b_msg.forward_from_chat
        groups = await db.get_all_chats()  # Cursor for groups
        sts = await message.reply_text('Broadcasting your messages...')
        total_groups = await db.total_chat_count()
        done, failed, success = 0, 0, 0

        start_time = datetime.datetime.now()

        async for group in groups:
            if 'id' in group:
                try:
                    if forward_msg:
                        status, error = await broadcast_messages_group(chat_id=int(group['id']), message=b_msg, forward=True)
                    else:
                        status, error = await broadcast_messages_group(chat_id=int(group['id']), message=b_msg, forward=False)

                    if status:
                        success += 1
                    else:
                        failed += 1
                except FloodWait as e:
                    logger.warning(f"FloodWait of {e.value} seconds encountered. Waiting...")
                    await asyncio.sleep(e.value)
                except Exception as e:
                    logger.error(f"Error broadcasting to group {group['id']}: {e}")
                    failed += 1

                done += 1
                await asyncio.sleep(2)
                if not done % 20:
                    await sts.edit(f"Broadcast in progress:\n\nTotal Groups: {total_groups}\nCompleted: {done}\nSuccess: {success}\nFailed: {failed}")

        time_taken = datetime.datetime.now() - start_time
        await sts.edit(f"Broadcast Completed:\n\nTime Taken: {time_taken}\n\nTotal Groups: {total_groups}\nCompleted: {done}\nSuccess: {success}\nFailed: {failed}")
    except Exception as e:
        logger.error(f"Error in broadcast_group: {e}")
        await message.reply_text("An error occurred during the Group broadcast.")
