"""
plugins/__init__.py – registers aiohttp routes: main routes + API routes.
"""
import logging
import os
from aiohttp import web
from .route import routes
from .api import api_routes

logger = logging.getLogger("Rashmibot.init")


# ✅ ADDED: Accept the pyrogram client instance parameter here
async def web_server(bot=None):
    """Create the aiohttp Application with all registered routes."""
    logger.info("Assembling aiohttp core application endpoints...")
    
    app = web.Application(client_max_size=30_000_000)
    
    # ── 🔗 THE MISSING LINK ──
    # Save the running bot instance into aiohttp's global dictionary storage!
    if bot:
        app["bot_client"] = bot
        logger.info("Successfully bound running Pyrogram bot_client reference to server app storage.")
    else:
        logger.warning("web_server was called without a valid Pyrogram bot reference instance!")
    
    # Register your modular routing frameworks
    app.add_routes(routes)
    app.add_routes(api_routes)

    # Let route.py handle serving index.html, app.css, and app.js natively.
    if os.path.isdir("webapp"):
        logger.info("Webapp asset root path verified. Mounting fallback asset directory map.")
        app.router.add_static("/assets/", path="webapp", name="webapp_assets")
    else:
        logger.warning("Critical baseline check failed: 'webapp' folder directory not found locally!")

    return app

