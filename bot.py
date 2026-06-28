"""
bot.py – Main entry point for the Auto-File-Search Telegram Bot.
IMPROVED: robust logging setup with fallback, health endpoint, cleaner structure.
FIXED: Non-blocking aiohttp binding to clear Koyeb health checks seamlessly.
"""
import logging
import logging.config
import os

# ── Logging setup with graceful fallback ──────────────────────────────────────
def _setup_logging() -> None:
    """Apply logging.conf if present, otherwise fall back to basicConfig."""
    if os.path.exists("logging.conf"):
        try:
            logging.config.fileConfig("logging.conf", disable_existing_loggers=False)
            return
        except Exception as exc:
            pass  # fall through to basicConfig
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s – %(message)s",
    )

_setup_logging()
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

from typing import AsyncGenerator, Optional, Union
from aiohttp import web
from pyrogram import Client, __version__, types
from pyrogram.raw.all import layer
from pyromod import listen  # noqa: F401  (registers pyromod handlers)

from database.ia_filterdb import Media
from database.users_chats_db import db
from info import API_HASH, API_ID, BOT_TOKEN, LOG_STR, SESSION
from plugins import web_server
from utils import temp

PORT = int(os.environ.get("PORT", 8080))


class Bot(Client):
    """Pyrogram-based Telegram bot with aiohttp health server."""

    def __init__(self) -> None:
        super().__init__(
            name         = SESSION,
            api_id       = API_ID,
            api_hash     = API_HASH,
            bot_token    = BOT_TOKEN,
            workers      = 50,
            plugins      = {"root": "plugins"},
            sleep_threshold = 5,
        )

    async def start(self) -> None:
        # 1. Fetch startup metadata caching rules from MongoDB
        b_users, b_chats    = await db.get_banned()
        temp.BANNED_USERS   = b_users
        temp.BANNED_CHATS   = b_chats

        # 2. ⚡ INITIALIZE WEB SERVER BLUEPRINT INSTANTLY
        # Assemble the aiohttp configuration blueprint dictionary container map
        web_blueprint = await web_server()
        
        # Inject the core client instance reference (self) directly into memory context
        web_blueprint["bot_client"] = self
        logger.info("Direct async reference injected into running context map successfully.")

        # 3. EXPOSE PORT 8080 IMMEDIATELY TO SATISFY KOYEB HEALTH CHECKS
        app_runner = web.AppRunner(web_blueprint)
        await app_runner.setup()
        await web.TCPSite(app_runner, "0.0.0.0", PORT).start()
        logger.info("Aiohttp server online on port %d. Health check clearance path active.", PORT)

        # 4. NOW SPIN UP RESIDENT BACKGROUND PYROGRAM TASKS SAFELY
        await super().start()
        await Media.ensure_indexes()

        me                  = await self.get_me()
        temp.ME             = me.id
        temp.U_NAME         = me.username
        temp.B_NAME         = me.first_name
        self.username       = "@" + me.username

        logger.info(
            "%s with Pyrogram v%s (Layer %s) started on @%s  [port %d]",
            me.first_name, __version__, layer, me.username, PORT,
        )
        logger.info(LOG_STR)

    async def stop(self, *args) -> None:
        await super().stop()
        logger.info("Bot stopped. Bye.")

    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        """Yield messages from *chat_id* in blocks of 200 between *offset* and *limit*."""
        current = offset
        while True:
            batch = min(200, limit - current)
            if batch <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current + batch + 1)))
            for msg in messages:
                yield msg
                current += 1


app = Bot()
app.run()
