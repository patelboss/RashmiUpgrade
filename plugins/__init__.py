"""
plugins/__init__.py – registers aiohttp routes: main routes + API routes.
"""
import logging
import os
from aiohttp import web
from .route import routes
from .api import api_routes

logger = logging.getLogger("Rashmibot.init")

async def web_server():
    """Create the aiohttp Application with all registered routes instantly."""
    logger.info("Assembling aiohttp core application endpoints...")

    app = web.Application(client_max_size=30_000_000)

    # Register your modular routing frameworks
    app.add_routes(routes)
    app.add_routes(api_routes)

    if os.path.isdir("webapp"):
        logger.info("Webapp asset root path verified. Mounting fallback asset directory map.")
        app.router.add_static("/assets/", path="webapp", name="webapp_assets")
    else:
        logger.warning("Critical baseline check failed: 'webapp' folder directory not found locally!")

    return app
