"""
plugins/__init__.py – registers aiohttp routes: main routes + API routes.
"""
from aiohttp import web
from .route import routes
from .api import api_routes


async def web_server():
    """Create the aiohttp Application with all registered routes."""
    app = web.Application(client_max_size=30_000_000)
    app.add_routes(routes)
    app.add_routes(api_routes)

    # Serve webapp static files
    import os
    if os.path.isdir("webapp"):
        app.router.add_static("/webapp/", path="webapp", name="webapp")

    return app
