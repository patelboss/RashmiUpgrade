"""
route.py – aiohttp web routes.
IMPROVED: root health check now returns real JSON status instead of bare "F".
          Added /health and /webapp endpoints for Telegram Web App support.
"""
import json
import time
import logging

from aiohttp import web
from utils import temp

logger = logging.getLogger(__name__)
routes = web.RouteTableDef()

_start_time = time.time()


@routes.get("/", allow_head=True)
async def root_route_handler(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok", "bot": temp.B_NAME or "AutoFileSearch"})


@routes.get("/health", allow_head=True)
async def health_handler(request: web.Request) -> web.Response:
    uptime = int(time.time() - _start_time)
    return web.json_response({
        "status":  "ok",
        "uptime_seconds": uptime,
        "bot_id":  temp.ME,
        "username": temp.U_NAME,
    })


@routes.get("/webapp")
async def webapp_handler(request: web.Request) -> web.Response:
    """Serve the Telegram Web App HTML."""
    try:
        with open("webapp/index.html", "r", encoding="utf-8") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")
    except FileNotFoundError:
        return web.Response(text="<h2>Web App not found</h2>", content_type="text/html", status=404)


@routes.get("/webapp/{path:.+}")
async def webapp_static_handler(request: web.Request) -> web.FileResponse:
    """Serve static assets for the Web App."""
    path = request.match_info["path"]
    full = f"webapp/{path}"
    import os
    if os.path.exists(full) and os.path.isfile(full):
        return web.FileResponse(full)
    raise web.HTTPNotFound()


async def web_server():
    """Create and return the aiohttp application."""
    app = web.Application()
    app.add_routes(routes)
    return app
