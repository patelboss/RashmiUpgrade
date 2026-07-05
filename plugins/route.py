"""
route.py – aiohttp web routes.
IMPROVED: Flat layout routing logic with explicit FileResponse parameters and diagnostics.
"""
import json
import time
import logging
import os

from aiohttp import web
from utils import temp

logger = logging.getLogger("Route.py")
logger.setLevel(logging.INFO)

routes = web.RouteTableDef()
_start_time = time.time()


@routes.get("/", allow_head=True)
async def root_route_handler(request: web.Request) -> web.Response:
    logger.info("Root endpoint hit from remote IP: %s", request.remote)
    return web.json_response({"status": "ok", "bot": temp.B_NAME or "AutoFileSearch"})


@routes.get("/health", allow_head=True)
async def health_handler(request: web.Request) -> web.Response:
    uptime = int(time.time() - _start_time)
    logger.info("Health request checked. Instance Uptime calculated at: %s seconds", uptime)
    return web.json_response({
        "status":  "ok",
        "uptime_seconds": uptime,
        "bot_id":  temp.ME,
        "username": temp.U_NAME,
    })


@routes.get("/webapp")
async def webapp_handler(request: web.Request) -> web.Response:
    """Serve the Telegram Web App HTML entry point."""
    target_file = "webapp/index.html"
    logger.info("Loading baseline WebApp viewport matrix request pointing to: %s", target_file)
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            html = f.read()
        return web.Response(text=html, content_type="text/html")
    except FileNotFoundError:
        logger.error("Web view mounting crashed: Local asset file target '%s' missing.", target_file)
        return web.Response(text="<h2>Web App Markup Document Not Found</h2>", content_type="text/html", status=404)


# FIX: Explicitly define path= for aiohttp's FileResponse handler
@routes.get("/{filename:app\.css|app\.js}")
@routes.get("/webapp/{filename:app\.css|app\.js}")
async def webapp_flat_assets_handler(request: web.Request) -> web.FileResponse:
    """Safely intercept and map flat layout scripts and styles regardless of context route."""
    filename = request.match_info["filename"]
    full_path = f"webapp/{filename}"
    
    logger.info("Asset routing lookup intercept: Client requested file -> %s", full_path)
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return web.FileResponse(path=full_path)  # Added explicit path= keyword
        
    logger.warning("Requested flat file asset lookup failed verification boundaries: %s", full_path)
    raise web.HTTPNotFound()


# FIX: Explicitly define path= here as well
@routes.get("/webapp/{path:.+}")
async def webapp_legacy_static_handler(request: web.Request) -> web.FileResponse:
    """Fallback directory route handler mapping deep nested folders."""
    path = request.match_info["path"]
    full_path = f"webapp/{path}"
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return web.FileResponse(path=full_path)  # Added explicit path= keyword
    raise web.HTTPNotFound()


async def web_server():
    """Create and return the aiohttp application structure."""
    logger.info("Initializing active standalone web application routing table configuration...")
    app = web.Application()
    app.add_routes(routes)
    return app
