"""
Script.py — COMPATIBILITY SHIM

All text is now centralised in langs/i18n.py.
This file exists only so any third-party plugin that still does
    from Script import script
does not crash. DO NOT add new strings here.
Migrate any remaining usages to:
    from langs.i18n import get, get_btn
"""
from langs.i18n import EN

class script:
    """Thin wrapper exposing EN class attributes for backwards compatibility."""

    # The old positional-format strings are replaced by named-kwarg versions in i18n.
    # We expose the EN text as-is so old callers at least get English text.
    START_TXT        = EN.START
    STATUS_TXT       = EN.STATUS_TXT
    LOG_TEXT_G       = EN.LOG_TEXT_G
    LOG_TEXT_P       = EN.LOG_TEXT_P
   # DELETEMSG        = EN.DELETEMSG
   # MELCOW_ENG       = EN.MELCOW_ENG
    CAPTION          = EN.CAPTION
