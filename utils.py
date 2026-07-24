"""
utils.py — thin facade over the split utils_* modules.

utils.py used to be a single 1063-line file mixing IMDb lookups, broadcast
logic, verification tokens, settings caching, subscription checks, and
generic helpers. It has been split into:

    utils_state.py        — temp cache class + shared mutable dicts/constants
    utils_helpers.py       — small, dependency-free helper functions
    utils_imdb.py          — get_poster / get_poster2 (IMDb lookups)
    utils_broadcast.py     — broadcast_messages / broadcast_messages_group / send_all
    utils_settings.py      — get_settings / save_group_settings / search_gagala
    utils_subscription.py  — is_subscribed
    utils_verify.py        — token / verification link helpers

This file re-exports every name the rest of the project already imports via
`from utils import X`, so no call site anywhere else needed to change.
No logic changed during this split — only the file boundaries moved (two
small pre-existing bugs were fixed in utils_broadcast.py; see the notes at
the top of that file).
"""

# Re-export everything so `from utils import X` keeps working unchanged
# everywhere else in the project.
from utils_state import (
    temp, imdb, TOKENS, VERIFIED, BANNED, REQUEST_TO_JOIN_MODE,
    SMART_OPEN, SMART_CLOSE, START_CHAR,
)
from utils_helpers import (
    BTN_URL_REGEX, FILTER_KEYWORDS,
    get_size, split_list, get_file_id, extract_user, list_to_str,
    last_online, remove_escapes, split_quotes, parser, humanbytes,
    clean_file_name,
)
from utils_imdb import get_poster, get_poster2
from utils_broadcast import broadcast_messages, broadcast_messages_group, send_all
from utils_settings import get_settings, save_group_settings, search_gagala
from utils_subscription import is_subscribed
from utils_verify import (
    get_verify_shorted_link, check_token, get_token, verify_user,
    check_verification,
)

__all__ = [
    "temp", "imdb", "TOKENS", "VERIFIED", "BANNED", "REQUEST_TO_JOIN_MODE",
    "SMART_OPEN", "SMART_CLOSE", "START_CHAR",
    "BTN_URL_REGEX", "FILTER_KEYWORDS",
    "get_size", "split_list", "get_file_id", "extract_user", "list_to_str",
    "last_online", "remove_escapes", "split_quotes", "parser", "humanbytes",
    "clean_file_name",
    "get_poster", "get_poster2",
    "broadcast_messages", "broadcast_messages_group", "send_all",
    "get_settings", "save_group_settings", "search_gagala",
    "is_subscribed",
    "get_verify_shorted_link", "check_token", "get_token", "verify_user",
    "check_verification",
]
