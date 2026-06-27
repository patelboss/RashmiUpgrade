"""
subs_cmd.py – Temporary /subs command to inspect a channel or group directly.
It reports the easiest stats the running bot can fetch without touching the DB.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

from pyrogram import Client, filters, enums
from pyrogram.errors import RPCError
from pyrogram.types import Message

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.INFO)
    stdout_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(stdout_handler)

logger.propagate = False

logger.info("=" * 72)
logger.info("Loading plugin module: %s", __file__)
logger.info("=" * 72)


def _normalize_target(raw: str) -> str:
    """
    Accept:
      - @username
      - username
      - -1001234567890
      - https://t.me/username
      - https://t.me/c/1234567890/42  (best effort)
    """
    value = (raw or "").strip()

    if not value:
        return ""

    if value.startswith("https://t.me/"):
        value = value.removeprefix("https://t.me/").strip("/")
    if value.startswith("t.me/"):
        value = value.removeprefix("t.me/").strip("/")

    if value.startswith("@"):
        return value

    return value


def _field(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _fmt_bool(value: Any) -> str:
    if value is True:
        return "Yes"
    if value is False:
        return "No"
    return "Unknown"


async def _fetch_channel_stats(client: Client, target: str) -> dict[str, Any]:
    """
    Fetch channel/group stats directly from Telegram using the live client.
    """
    logger.info("Resolving target: %r", target)

    chat = await client.get_chat(target)
    logger.info(
        "get_chat() succeeded for target=%r | id=%s | title=%r",
        target,
        getattr(chat, "id", None),
        getattr(chat, "title", None),
    )

    stats: dict[str, Any] = {
        "title": _field(chat, "title", ""),
        "id": _field(chat, "id", ""),
        "username": _field(chat, "username", ""),
        "type": _field(chat, "type", ""),
        "description": _field(chat, "description", ""),
        "invite_link": _field(chat, "invite_link", ""),
        "members_count": _field(chat, "members_count", None),
        "is_verified": _field(chat, "is_verified", None),
        "is_restricted": _field(chat, "is_restricted", None),
        "is_scam": _field(chat, "is_scam", None),
        "is_fake": _field(chat, "is_fake", None),
    }

    # Some builds expose members_count through get_chat(); others need a separate call.
    if not stats["members_count"]:
        try:
            if hasattr(client, "get_chat_members_count"):
                stats["members_count"] = await client.get_chat_members_count(target)
                logger.info(
                    "get_chat_members_count() succeeded for target=%r -> %s",
                    target,
                    stats["members_count"],
                )
        except Exception as exc:
            logger.warning("get_chat_members_count failed for %r: %s", target, exc, exc_info=True)

    # Try to fetch the most recent post/message text.
    latest_text = ""
    latest_id = None
    latest_date = None
    try:
        async for msg in client.get_chat_history(target, limit=1):
            latest_id = _field(msg, "id", None)
            latest_date = _field(msg, "date", None)
            latest_text = (msg.text or msg.caption or "").strip()
            break
        logger.info(
            "Latest history fetch succeeded for target=%r | message_id=%r | text_len=%s",
            target,
            latest_id,
            len(latest_text),
        )
    except Exception as exc:
        logger.warning("get_chat_history failed for %r: %s", target, exc, exc_info=True)

    stats["latest_post_id"] = latest_id
    stats["latest_post_date"] = latest_date
    stats["latest_post_text"] = latest_text
    return stats


def _format_stats(stats: dict[str, Any]) -> str:
    title = stats.get("title") or "Unknown"
    chat_id = stats.get("id") or "Unknown"
    username = stats.get("username") or "—"
    chat_type = stats.get("type") or "—"
    members_count = stats.get("members_count")
    description = stats.get("description") or ""
    invite_link = stats.get("invite_link") or "—"
    latest_post_text = stats.get("latest_post_text") or "—"
    latest_post_id = stats.get("latest_post_id") or "—"
    latest_post_date = stats.get("latest_post_date") or "—"

    lines = [
        "<b>📊 Channel Stats</b>",
        "",
        f"<b>Title:</b> <code>{title}</code>",
        f"<b>ID:</b> <code>{chat_id}</code>",
        f"<b>Username:</b> <code>{username}</code>",
        f"<b>Type:</b> <code>{chat_type}</code>",
        f"<b>Members/Subs:</b> <code>{members_count if members_count is not None else 'Unknown'}</code>",
        f"<b>Verified:</b> <code>{_fmt_bool(stats.get('is_verified'))}</code>",
        f"<b>Restricted:</b> <code>{_fmt_bool(stats.get('is_restricted'))}</code>",
        f"<b>Scam:</b> <code>{_fmt_bool(stats.get('is_scam'))}</code>",
        f"<b>Fake:</b> <code>{_fmt_bool(stats.get('is_fake'))}</code>",
        "",
        "<b>Latest Post:</b>",
        f"<b>Post ID:</b> <code>{latest_post_id}</code>",
        f"<b>Date:</b> <code>{latest_post_date}</code>",
        f"<b>Text:</b> <code>{latest_post_text[:700] if latest_post_text != '—' else '—'}</code>",
    ]

    if description:
        lines.extend(["", f"<b>Description:</b> <code>{description[:700]}</code>"])

    if invite_link and invite_link != "—":
        lines.extend(["", f"<b>Invite Link:</b> <code>{invite_link}</code>"])

    return "\n".join(lines)


async def _handle_subs_request(client: Client, message: Message, source: str) -> None:
    """
    Shared implementation used by both the early probe and the normal command handler.
    """
    user_id = message.from_user.id if message.from_user else "Unknown"
    logger.info("Handler path=%s | user_id=%s | text=%r", source, user_id, message.text)

    try:
        raw_text = (message.text or "").strip()

        if not raw_text:
            await message.reply_text(
                "<b>❌ Empty request.</b>",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        parts = raw_text.split(maxsplit=1)
        if len(parts) < 2:
            await message.reply_text(
                "<b>Usage:</b> <code>/subs @channelusername</code>\n"
                "<b>Or:</b> <code>/subs -1001234567890</code>",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        raw_target = parts[1].strip()
        target = _normalize_target(raw_target)

        logger.info(
            "Parsed /subs target | source=%s | raw=%r | normalized=%r",
            source,
            raw_target,
            target,
        )

        if not target:
            await message.reply_text(
                "<b>❌ Invalid target.</b>\nUse a channel username or numeric channel id.",
                parse_mode=enums.ParseMode.HTML,
            )
            return

        status = await message.reply_text(
            f"🔄 Fetching stats for <code>{target}</code> ...",
            parse_mode=enums.ParseMode.HTML,
        )

        try:
            stats = await _fetch_channel_stats(client, target)
            reply = _format_stats(stats)
            logger.info("Stats fetch complete for target=%r via %s", target, source)
            await status.edit_text(reply, parse_mode=enums.ParseMode.HTML)
        except RPCError as rpc_err:
            logger.exception("Pyrogram RPCError while fetching stats for %r", target)
            await status.edit_text(
                f"<b>❌ Telegram error:</b>\n<code>{rpc_err}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception as exc:
            logger.exception("Unexpected error while fetching stats for %r", target)
            await status.edit_text(
                f"<b>❌ Failed to fetch stats:</b>\n<code>{exc}</code>",
                parse_mode=enums.ParseMode.HTML,
            )

    except Exception as outer_exc:
        logger.exception("Fatal /subs handler error for user_id=%s via %s", user_id, source)
        try:
            await message.reply_text(
                f"<b>❌ /subs crashed:</b>\n<code>{outer_exc}</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            pass


# This probe runs very early and should catch /subs even if another handler is being noisy.
@Client.on_message(
    filters.private & filters.incoming & filters.text & filters.regex(r"^/subs(?:@\w+)?(?:\s|$)"),
    group=-10000,
)
async def subs_probe(client: Client, message: Message) -> None:
    logger.info("Early /subs probe matched text=%r", message.text)
    await _handle_subs_request(client, message, source="probe")


@Client.on_message(filters.command("subs") & filters.private)
async def subs_cmd(client: Client, message: Message) -> None:
    logger.info("Normal /subs command handler entered text=%r", message.text)
    await _handle_subs_request(client, message, source="command")
