"""
plugins/pm_filter_state.py — Shared in-memory caches used across the pm_filter_*
modules (pm_filter.py, pm_filter_search.py, pm_filter_callbacks.py).

These were originally module-level globals inside a single 1500+ line
pm_filter.py. Since that file has been split into three files for
readability, this module exists so every split file imports the SAME
dict objects instead of each accidentally creating its own empty copy.

Do not rename or re-initialize these elsewhere — always:
    from plugins.pm_filter_state import BUTTONS, FRESH, ...
"""

# Keyed by "{chat_id}-{message_id}" -> last search string (used by next_page
# for pagination lookups).
BUTTON = {}
BUTTONS = {}

# Keyed similarly, used by the send_fsall/send_fall bulk-send callbacks.
# NOTE: the send_fsall branch used to reference a differently-named
# `BUTTON0` (no S), which was a latent NameError bug — it has been fixed
# in plugins/pm_filter_callbacks.py to reference this dict instead.
BUTTONS0 = {}
BUTTONS1 = {}
BUTTONS2 = {}

# Keyed by "{chat_id}-{message_id}" -> last search string (auto_filter results).
FRESH = {}

# Keyed by the triggering message id -> list of candidate movie titles,
# used by the spell-check suggestion buttons (spolling callback).
SPELL_CHECK = {}

AUTO_DELETE = 'False'
