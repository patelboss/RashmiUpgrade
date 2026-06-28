"""
plugins/broadcast.py — Broadcast commands for users and groups.
All strings via langs/i18n. Debug events via debug.dlog.
"""

import asyncio
import logging
import datetime

from pyrogram import Client, filters
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

from info import ADMINS
from database.users_chats_db import db
from utils import broadcast_messages, broadcast_messages_group
from langs.i18n import get
from debug import dlog

logger = logging.getLogger("broadcast")


@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def pm_broadcast(client, message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.reply_text(get(lang, "BROADCAST_ASK"))
    try:
        b_msg = await asyncio.wait_for(
            client.ask(chat_id=message.from_user.id,
                       text=get(lang, "BROADCAST_ASK_MSG")),
            timeout=120
        )
    except asyncio.TimeoutError:
        return await message.reply_text(get(lang, "BROADCAST_TIMEOUT"))

    forward_msg  = b_msg.forward_from or b_msg.forward_from_chat
    users        = await db.get_all_users()
    sts          = await message.reply_text(get(lang, "BROADCAST_STARTING"))
    total_users  = await db.total_users_count()
    done = blocked = deleted = failed = success = 0
    start_time = datetime.datetime.now()

    async for user in users:
        if "id" not in user:
            continue
        try:
            status, error = await broadcast_messages(
                user_id=int(user["id"]), message=b_msg, forward=bool(forward_msg)
            )
            if status:       success += 1
            elif error == "Blocked":  blocked += 1
            elif error == "Deleted":  deleted += 1
            else:            failed  += 1
        except FloodWait as e:
            logger.warning("FloodWait %ss", e.value)
            await asyncio.sleep(e.value)
        except InputUserDeactivated:
            deleted += 1
        except UserIsBlocked:
            blocked += 1
        except PeerIdInvalid:
            failed += 1
        except Exception as exc:
            logger.error("Broadcast error for user %s: %s", user["id"], exc)
            failed += 1

        done += 1
        if not done % 20:
            await sts.edit(get(lang, "BROADCAST_PROGRESS",
                               total=total_users, done=done, success=success,
                               blocked=blocked, deleted=deleted, failed=failed))
        # Only sleep on FloodWait, not every message
        await asyncio.sleep(0.05)

    time_taken = datetime.datetime.now() - start_time
    await sts.edit(get(lang, "BROADCAST_DONE",
                       time=time_taken, total=total_users, done=done,
                       success=success, blocked=blocked, deleted=deleted, failed=failed))
    dlog("BROADCAST_DONE", user_id=message.from_user.id,
         extra={"sent": success, "total": total_users})


@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS))
async def broadcast_group(bot, message):
    lang = await db.get_user_lang(message.from_user.id)
    await message.reply_text(get(lang, "BROADCAST_ASK"))
    try:
        b_msg = await asyncio.wait_for(
            bot.ask(chat_id=message.from_user.id,
                    text=get(lang, "BROADCAST_ASK_MSG")),
            timeout=120
        )
    except asyncio.TimeoutError:
        return await message.reply_text(get(lang, "BROADCAST_TIMEOUT"))

    forward_msg  = b_msg.forward_from or b_msg.forward_from_chat
    groups       = await db.get_all_chats()
    sts          = await message.reply_text(get(lang, "BROADCAST_STARTING"))
    total_groups = await db.total_chat_count()
    done = failed = success = 0
    start_time = datetime.datetime.now()

    async for group in groups:
        if "id" not in group:
            continue
        try:
            status, _ = await broadcast_messages_group(
                chat_id=int(group["id"]), message=b_msg, forward=bool(forward_msg)
            )
            if status: success += 1
            else:      failed  += 1
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception as exc:
            logger.error("Group broadcast error %s: %s", group["id"], exc)
            failed += 1

        done += 1
        if not done % 20:
            await sts.edit(get(lang, "BROADCAST_PROGRESS",
                               total=total_groups, done=done, success=success,
                               blocked=0, deleted=0, failed=failed))
        await asyncio.sleep(0.05)

    time_taken = datetime.datetime.now() - start_time
    await sts.edit(get(lang, "BROADCAST_DONE",
                       time=time_taken, total=total_groups, done=done,
                       success=success, blocked=0, deleted=0, failed=failed))
    dlog("GRP_BROADCAST_DONE", user_id=message.from_user.id,
         extra={"sent": success, "total": total_groups})
