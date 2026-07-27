"""
plugins-independent shared state for the split utils_* modules.

utils.py used to be a single 1063-line file. It has been split into:

    utils_state.py       (this file) — the `temp` cache class + module-level
                          mutable dicts/constants shared by the other pieces
    utils_helpers.py      — small, dependency-free helper functions
    utils_imdb.py         — get_poster / get_poster2 (IMDb lookups)
    utils_broadcast.py    — broadcast_messages / broadcast_messages_group / send_all
    utils_settings.py     — get_settings / save_group_settings / search_gagala
    utils_subscription.py — is_subscribed
    utils_verify.py       — token / verification link helpers
    utils.py              — thin facade that re-exports everything above, so
                             every existing `from utils import X` elsewhere in
                             the project keeps working unchanged.

This file has NO imports from any other utils_* module, so it can safely be
imported by all of them without any circular-import risk.
"""

import os
from imdb import Cinemagoer

imdb = Cinemagoer()

# temp db for banned
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    GETALL = {}
    SHORT = {}
    SETTINGS = {}


# Verification token bookkeeping (utils_verify.py)
TOKENS = {}
VERIFIED = {}

# NOTE: BANNED and REQUEST_TO_JOIN_MODE below were present in the original
# utils.py but are not referenced anywhere in the codebase (dead state) —
# kept here only for parity with the original file in case anything
# external relies on `from utils import BANNED`.
BANNED = {}
REQUEST_TO_JOIN_MODE = 'False'

SMART_OPEN = '\u201c'
SMART_CLOSE = '\u201d'
START_CHAR = ('\'', '"', SMART_OPEN)
