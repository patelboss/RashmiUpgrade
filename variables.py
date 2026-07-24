"""
variables.py – dynamic config loaded from MongoDB (with env fallback).
FIXED: removed bare 'except', fixed AUTH_CHANNELS NameError, removed noisy print()s.
"""
import logging
from os import environ
from database.envs import fetch_config
from Script import script

logger = logging.getLogger(__name__)

config_name = "env_config"
try:
    config = fetch_config(config_name)
    if config is None:
        config = {}
    logger.info("Dynamic config loaded from MongoDB (%d keys).", len(config))
except Exception as exc:
    logger.warning("Could not load dynamic config from MongoDB: %s. Falling back to env vars.", exc)
    config = {}


def _cfg(key: str, default=None):
    """Return value from Mongo config first, then env var, then default."""
    return config.get(key) or environ.get(key, default)


def _bool_cfg(key: str, default: bool = False) -> bool:
    val = _cfg(key)
    if val is None:
        return default
    if isinstance(val, bool):
        return val
    return str(val).lower() in ("true", "yes", "1", "enable", "y")


# ── Feature flags ──────────────────────────────────────────────────────────────
VERIFY                  = _bool_cfg("VERIFY", False)
VERIFY_SECOND_SHORTNER  = _bool_cfg("VERIFY_SECOND_SHORTNER", False)

# ── URL shortener ──────────────────────────────────────────────────────────────
VERIFY_SHORTLINK_URL    = _cfg("VERIFY_SHORTLINK_URL", "")
VERIFY_SHORTLINK_API    = _cfg("VERIFY_SHORTLINK_API", "")
VERIFY_SND_SHORTLINK_URL = _cfg("VERIFY_SND_SHORTLINK_URL", "")
VERIFY_SND_SHORTLINK_API = _cfg("VERIFY_SND_SHORTLINK_API", "")
VERIFY_TUTORIAL         = _cfg("VERIFY_TUTORIAL", "https://t.me/Filmykeedha/394")

# ── Auth channels (FIXED: was environ.get(AUTH_CHANNELS) – missing quotes) ────
_raw_auth_channels = _cfg("AUTH_CHANNELS", "")
AUTH_CHANNELS: list = [ch.strip() for ch in _raw_auth_channels.split(",") if ch.strip()] \
    if _raw_auth_channels else []

# ── Timing ─────────────────────────────────────────────────────────────────────
DLTTM = int(_cfg("DLTTM", "4200"))

# ── Media ──────────────────────────────────────────────────────────────────────
WELCOME_VIDEO_ID = _cfg(
    "WELCOME_VIDEO_ID",
    "BAACAgQAAxkBAAEWWw5nXJ_bgRy9MY3ZNxpLzbIaysGuswAC2hoAAuLv4VIyB40_JD42Hh4E"
)

# ── Captions ───────────────────────────────────────────────────────────────────
CUSTOM_FILE_CAPTION = _cfg("CUSTOM_FILE_CAPTION") or str(script.CAPTION)

logger.debug(
    "variables loaded – VERIFY=%s, AUTH_CHANNELS=%s, DLTTM=%d",
    VERIFY, AUTH_CHANNELS, DLTTM,
)
