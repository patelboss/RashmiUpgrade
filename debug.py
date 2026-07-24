"""
debug.py — Centralised debug logger for RashmiUpgrade bot.

Set DEBUG_MODE=true in your .env / environment to enable verbose logging.
Set DEBUG_MODE=false (or omit it) for production — zero output, zero overhead.

Usage anywhere in handlers:
    from debug import dlog
    dlog("FILE_DELIVERED", user_id=user.id, extra={"file": file_name})
    dlog("SEARCH_QUERY",   user_id=user.id, extra={"q": query, "hits": 12})
    dlog("VERIFY_PASSED",  user_id=user.id)
    dlog("BROADCAST_TICK", extra={"done": 50, "total": 1000})
"""

import logging
import sys
from info import DEBUG_MODE

_logger = logging.getLogger("rashmi.debug")

if DEBUG_MODE:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setLevel(logging.DEBUG)
    _handler.setFormatter(
        logging.Formatter(
            "%(asctime)s  [DEBUG] %(message)s",
            datefmt="%H:%M:%S"
        )
    )
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False


def dlog(action: str, user_id: int = None, extra: dict = None) -> None:
    """
    Emit a single structured debug line — only when DEBUG_MODE is True.

    Parameters
    ----------
    action  : Short uppercase label for the event, e.g. "FILE_DELIVERED"
    user_id : Telegram user ID (optional)
    extra   : Dict of additional key-value data to log (optional)
    """
    if not DEBUG_MODE:
        return

    parts = [f"[{action}]"]
    if user_id is not None:
        parts.append(f"user={user_id}")
    if extra:
        kv = "  ".join(f"{k}={v}" for k, v in extra.items())
        parts.append(kv)

    _logger.debug("  ".join(parts))
