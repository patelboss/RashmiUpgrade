# Continue: RashmiUpgrade i18n / debug-logging / cleanup refactor

I'm continuing a multi-session refactor of a Pyrogram Telegram bot
(RashmiUpgrade / FilmyKeedha). Read this whole prompt before touching any
code.

## The original plan (still the source of truth)

1. Audit every user-facing string and button label across the codebase.
2. Centralize them in `langs/i18n.py` — `EN` base class, `HI` (Hindi)
   overrides, `TA` (Tamil) stub. `get(lang, key, **kwargs)` and
   `get_btn(lang, key)` fetch strings, falling back to English if a
   translation is missing.
3. Refactor every plugin handler to call `get()`/`get_btn()` instead of
   hard-coding text. Don't change logic or remove functionality while doing
   this sweep.
4. `/help` must cover every real command, correctly, in the user's language.
5. Debug logging: `if DEBUG_MODE: logger.info(...)` at each significant
   step in every handler. Never bare `print()`. No logging when
   `DEBUG_MODE` is off.
6. Code cleanup: PEP 8, no trailing whitespace, no multi-statement lines,
   break up very long functions where reasonable — without changing behavior.
7. README: document the i18n system, how to add a language, `DEBUG_MODE`,
   code style, project layout.

## Standing audit rule (don't repeat an earlier mistake)

Any audit of "every command" or "every hardcoded string" must recursively
scan the whole `plugins/` tree (and `database/` — literal strings turned up
there too, not just in plugins), not just the top level. Before declaring
the i18n sweep complete, run:
find . -path ./venv -prune -o -iname "*.py" -print | xargs grep -n "filters.command("
and diff the result against whatever command list `langs/i18n.py`'s
`HELP_CAT_*` strings claim to cover. `/fsub` / `/nofsub` genuinely doesn't
exist as an in-chat command — Force Subscribe is configured via the
`AUTH_CHANNEL` env var — that correction should stay as-is.

Also: the per-file `~msgs`/`~buttons` estimates in earlier queue tables were
consistently undercounted (actual literal-string counts, once grepped file
by file, ran anywhere from 1.3x to 3x the table's estimate). Treat any such
count as a floor, not a ceiling — always grep the actual file rather than
trusting a prior estimate.

## STATUS: the mechanical i18n sweep is now COMPLETE

Every file in `plugins/` and `database/` that contains a genuine hardcoded
user-facing string or button label has been converted to `get()`/`get_btn()`.
Confirmed with a full-repo scan (see verification section) — the only files
without a `langs.i18n` import are ones with zero user-facing text (routes,
API glue, state dicts, `__init__.py`, pure-Mongo helper modules) or the one
deliberately-parked exception below.

### Fully converted (import `langs.i18n`, verified clean)

`plugins/`: `connection.py`, `misc.py`, `genlink.py`, `commands.py`,
`commands_start.py`, `commands_admin.py`, `help.py`, `broadcast.py`,
`pm_filter_callbacks.py`, `p_ttishow.py`, `filters.py`, `index.py`,
`pm_filter_search.py`, `pm_filter.py`, `inline.py`, `envscommand.py`,
`banned.py`, `cmd_weappb.py`, `Extra/contact.py`, `Extra/check_alive.py`.

`database/`: `filters_mdb.py`.

### This session's work (in order)

- **filters.py** (11→~14 literals): `/addfilter`, `/viewfilters`,
  `/delelefilter`, `/deleteallf`. Reused `ANON_ADMIN_CONNECT` /
  `NOT_IN_GROUP_PLAIN` where text matched exactly; new plain-text button
  variants (`BTN_YES_PLAIN`/`BTN_CANCEL_PLAIN`) since the existing
  `BTN_YES`/`BTN_CANCEL` are emoji-styled.
- **index.py** (~28 literals, table said 7/5): `/index` request+approval
  flow, `/setskip`, `index_files_to_db` progress messages. Moderator
  `LOG_CHANNEL` post and its Accept/Reject buttons always render in
  `DEFAULT_LANG` (addressed to moderators, not the requester). Removed two
  bare `print()` calls in the never-called `retry_on_floodwait()` (dead
  code, but still a bare-print violation). `index_files_to_db()` gained an
  optional `lang` param.
- **pm_filter_search.py** (table said 0 msgs/13 buttons — actually 6
  messages + 8 button variants): `auto_filter`, `advantage_spell_chok`,
  `manual_filters`, `mongo_spell_fallback`. This file already had *partial*
  `DEBUG_MODE`/`[SPELL]` logging from an earlier pass but
  `logger.setLevel(logging.ERROR)` was silently dropping it — bumped to
  INFO. Also gated several unconditional `logger.info(f"Processed
  query...")` traces that predated the `DEBUG_MODE` convention.
- **Extra/contact.py** (15→20 literals): `/feedback`, `/report`, `/talk`,
  `/create_code`, `/delete_code`, `/send`. Added `logger.exception(e)` in
  `/send`'s except block — file had zero error logging before. Flagged
  (not fixed): `SEND_USERS_HEADER` is built but never actually sent in the
  original `send_msg()` — dead local variable, pre-existing, left as-is.
- **Extra/check_alive.py** (2 literals): `/alive`, `/ping` incl. the "..."
  placeholder.
- **envscommand.py** (13→15 literals): `/add_env`, `/get_envs`,
  `/all_envs`, `/update_env`, `/delete_env`. Left the module-level
  `logging.basicConfig(...)` untouched (affects the root logger app-wide,
  out of scope) but added the standard `logger.setLevel(INFO)` alongside it
  for consistency. Added `logger.exception(e)` in `/all_envs`'s except
  block — previously unlogged.
- **banned.py** (1 msg + 1 button): `ban_reply`, `grp_bd`. Reused
  `BTN_SUPPORT_PLAIN`. The disabled-group notice looks like the existing
  `CHAT_NOT_ALLOWED` key but isn't identical (bilingual, has a Reason line,
  not `<b>`-wrapped) — got its own key `GRP_DISABLED_NOTICE_BILINGUAL`
  rather than merging.
- **cmd_weappb.py** (table said 1 button — actually 6 msgs + 1 button):
  `/wtry` (diagnostic ping handler), `/webapp`. This file has its own
  custom logging setup (dedicated stdout `StreamHandler`,
  `propagate=False`, unconditional import-time banner logs) — left that
  untouched since it's not per-request and not a string issue, but gated
  the per-request tracing inside the four functions behind `DEBUG_MODE`.
  `_build_webapp_markup()` gained a `lang` param.
- **pm_filter.py** (table said 1 msg/5 buttons — actually 6 msgs + 5
  buttons): `give_filter()` fully converted; `get_butto1ns()` also
  converted even though it's dead code (only caller is the
  docstring-disabled `private_message_handler`, left untouched/inert as
  before).
- **inline.py** (table said 6 buttons — actually 6 msgs + 4 buttons):
  `answer()` (the inline-query handler), `get_reply_markup()` /
  `get_reply_markup1()` (latter is dead code, converted anyway for
  consistency, both gained `lang=DEFAULT_LANG`). Several commented-out
  `#logger.info(...)` leftovers were turned into real `DEBUG_MODE`-gated
  `[INLINE]` logs instead of staying as dead comments.
- **connection.py** (8 literals): `/connect`, `/disconnect`,
  `/connections`. Every key this file needed *already existed* in
  `langs/i18n.py` from an earlier session (a full `# ── Connections ──`
  block, unused until now) — no new keys needed, just wired up. Logger
  level bumped ERROR→INFO (same recurring bug as several other files).
- **database/filters_mdb.py** (4→5 literals): `delete_filter()` and
  `del_all()`. These are DB-layer functions called from `plugins/filters.py`
  and `plugins/pm_filter_callbacks.py` respectively — both gained an
  optional `lang=DEFAULT_LANG` param, and **both call sites were updated**
  to pass the already-resolved `lang` through (`plugins/filters.py` line
  ~287, `plugins/pm_filter_callbacks.py` line ~283). Logger level bumped
  WARNING→INFO.

Full verification checklist (see below) run clean after every single file
above — only the already-known dormant-bug F821s ever show up, never
anything new.

## Confirmed NOT needing conversion (checked, not just assumed)

- `plugins/api.py`, `plugins/channel.py`, `plugins/route.py`,
  `plugins/subs_cmd.py` (main handler is dead code, wrapped in a
  docstring), `plugins/pm_filter_state.py`, `plugins/__init__.py` — zero
  user-facing literals, confirmed by grep.
- `database/batch_filedb.py`, `database/ia_filterdb.py`,
  `database/connections_mdb.py`, `database/spell_feedback_mdb.py`,
  `database/users_chats_db.py`, `database/envs.py`, `database/verified.py`
  — zero user-facing literals, confirmed by grep.

## Still deliberately parked — one item, unchanged from before

`plugins/Extra/postc.py` + `plugins/Extra/Cscript.py` use their own
`TEXTS` dict template system (same pattern as the legacy `Script.py` used
by `pm_filter_callbacks.py`'s `cb_handler` — help/about/source/etc. still
render via `script.XXX_TXT.format(...)`, also untouched). Re-checked this
session: `postc.py`'s only literal-looking match is
`f"<b>{result['error']}</b>"`, which just wraps dynamic content — nothing
to convert there. Migrating the `TEXTS`/`Script.py` systems into
`langs/i18n.py` is a bigger structural call (retire them entirely, or keep
both?) and still needs a product decision before anyone touches it
mechanically.

## What's left overall (nothing string-related)

1. **The Script.py/Cscript.py decision above** — needs a call from the
   person, not a mechanical sweep.
2. **Code cleanup**: long-function breakup / general PEP 8 pass is still
   only a side effect of the earlier module splits. `cb_handler` in
   `pm_filter_callbacks.py` is still one big ~500-line if/elif dispatcher
   — left intentionally verbatim in structure (the file's own docstring
   says so); splitting it is a structural decision, not part of the i18n
   sweep.
3. **HI/TA translation coverage**: every new key added across all sessions
   went into the `EN` class only, with a `HI` override added just where an
   earlier session was actively translating. There's now a large surface
   of EN-only keys (everything converted this session) that fall back to
   English for Hindi/Tamil users. Whether to do a full HI translation pass
   is a separate, larger task from the mechanical string-extraction sweep.
4. **README.md**: was written covering i18n usage, project layout,
   DEBUG_MODE, code style, dormant issues, changelog — as of an earlier
   session. Hasn't been updated to list this session's additional
   converted files; worth a refresh pass if the person wants the doc
   current.

## Known dormant bugs (found, documented, NOT fixed — need a product decision)

- send_all() in utils_broadcast.py calls get_shortlink(), which is never
  defined anywhere. Only reachable if a group's is_shortlink setting is
  enabled -- nothing currently turns that on, so it's dormant.
- database/verified.py isn't imported anywhere and mixes synchronous
  pymongo.MongoClient with await on its calls. Needs a decision (swap to
  Motor? drop the awaits?) before it's wired back in.
- database/users_chats_db.py uses datetime in a few places (lines
  ~165-195) without importing it.
- plugins/p_ttishow.py (save_group(), auto_delete branch) references
  asyncio without importing it -- confirmed still present, still
  unreachable (nothing sets auto_delete), left alone every session so far.

## Bugs found via a real compile/import/test pass (this session, NOT fixed)

The person asked for a genuine compile-and-test pass rather than more
mechanical sweeps. Did this properly: installed the real dependencies
(pyrogram, pymongo, motor, the exact `git+https://github.com/Joelkb/cinemagoer`
fork requirements.txt pins, etc.) and actually imported all 49
plugin/database modules with dummy env vars, instead of only
py_compile/flake8 (AST-level checks miss runtime import-time crashes).
Found two real, previously-undocumented bugs from this:

- **HIGH SEVERITY -- likely crashes the bot on startup for real
  deployments.** `info.py` line 44: `FILE_DB_URI = environ.get('FILE_DB_URI', "")`
  defaults to an empty string. `database/ia_filterdb.py` line 24 does
  `client = AsyncIOMotorClient(FILE_DB_URI)` at module level with NO
  try/except -- if FILE_DB_URI isn't explicitly set (separately from
  DATABASE_URI), this raises `ConfigurationError: Empty host` immediately
  on import. Verified the blast radius directly: with FILE_DB_URI unset,
  26 of 27 plugin files failed to import (everything touching
  search/filters/media -- inline.py, pm_filter_search.py, channel.py,
  commands_start.py, api.py, p_ttishow.py, commands_admin.py, index.py,
  pm_filter_callbacks.py all import ia_filterdb.py transitively). Once
  FILE_DB_URI is set, all 49 modules import cleanly with zero failures --
  confirmed this is the only real blocker in the entire codebase.
  `info.py` itself has the clue: `#if MULTIPLE_DATABASE else DATABASE_URI`
  is commented out, and `MULTIPLE_DATABASE` isn't defined anywhere in the
  file -- the intended fallback was written and then disabled/abandoned.
- **Same root cause, quieter failure mode.** `database/envs.py` has the
  identical FILE_DB_URI problem, but its MongoClient setup (lines 32-52)
  IS wrapped in try/except -- so instead of crashing, `col`/`db`/`client`
  never get bound at module scope, and every function in the file
  (fetch_config, save_env, get_env, fetch_all_configs, update_config,
  delete_env_from_db) silently returns `{}`/`False` forever via their own
  per-function try/except. Reproduced directly: got
  `ERROR - Error fetching env_config configuration: name 'col' is not
  defined` in the log output during testing. An operator would see
  `/all_envs` say "no configurations found" with zero indication the DB
  connection never worked.
  Both bugs share one fix: restore the FILE_DB_URI-falls-back-to-
  DATABASE_URI logic that's currently commented out. That's an
  architecture call (are file-storage and the main DB meant to be
  genuinely separate, or was this always meant to default to one DB?),
  not a mechanical patch -- needs the person's direction before touching it.
- **Already found and confirmed earlier this session** (before the import
  sweep, via manual inspection): `info.py` lines 69/71 --
  `PUBLIC_FILE_CHANNEL = int(environ.get('PUBLIC_FILE_CHANNEL', ''))` and
  the same pattern for `BATCH_FILE_CHANNEL` -- both crash on `int('')` if
  unset, unlike `LOG_CHANNEL` two lines above which safely defaults to
  `0`. Same category of bug as the FILE_DB_URI issue -- inconsistent
  empty-string vs. safe-numeric defaults across info.py's env var parsing.
- **False alarm, ruled out, noting for the record**: an
  `ArgumentError: Invalid SQLite URL: sqlite://cinemagoer.db` initially
  looked like a real bug in utils_imdb.py/utils_state.py/utils_settings.py/
  utils_verify.py. Traced it fully: it was caused by MY test setup
  installing the wrong `cinemagoer` package (generic PyPI version instead
  of the `git+https://github.com/Joelkb/cinemagoer` fork requirements.txt
  actually pins). Confirmed clean with the correct fork installed --
  not a codebase bug, don't re-investigate this one.

No new dormant bugs were found this session (banned.py, cmd_weappb.py,
connection.py, filters_mdb.py all came back completely clean from
flake8). Flag all of the above clearly rather than silently "fixing"
some -- especially the FILE_DB_URI issue, which needs a real
architecture decision, not a mechanical patch.

## Bugs fixed this session

- **plugins/help.py `/chelp` NameError bug**: `get_random_sticker()` and
  `asyncio.sleep(...)` were called without being imported. Unlike the
  other dormant bugs above, this one had a single unambiguous fix (no
  design decision needed) because `get_random_sticker()` already existed,
  fully implemented, in `plugins/Extra/postc.py` — it just wasn't
  imported into help.py. Added `import asyncio` and
  `from plugins.Extra.postc import get_random_sticker` to help.py's
  import block. No circular import risk (postc.py imports nothing from
  help.py). Verified with flake8 -- both F821s for this file are gone,
  only the two genuinely-still-open dormant bugs above remain in the
  flake8 output.

## Conventions established so far (follow these exactly)

- Every plugin handler that sends user-facing text should start by
  resolving lang = await db.get_user_lang(user_id) (fall back to
  DEFAULT_LANG if there's no from_user, e.g. anonymous admins/callback
  queries) via a local `_user_lang()` helper -- every converted file in
  this project now has its own copy of this helper (not shared/imported)
  -- keep following that pattern.
- New i18n keys go in the EN class in langs/i18n.py with a trailing
  # comment saying where they're used; add a matching HI override only if
  you're actually translating it.
- Button-label keys are prefixed BTN_.
- Debug logging: `if DEBUG_MODE: logger.info("[TAG] message", *args)` --
  bracket tag per feature area, never unconditional logger.info() for
  per-request detail, never print(). Logger level must be INFO (not the
  default ERROR/WARNING) or the DEBUG_MODE guard is pointless -- check
  this on every file touched (it was wrong on nearly every file this
  session: filters.py, index.py, envscommand.py, banned.py, connection.py,
  filters_mdb.py all had it set to ERROR or WARNING).
- Real errors (`logger.exception`, `logger.error` on actual failures)
  stay unconditional -- only per-request tracing gets the DEBUG_MODE gate.
- Don't rename existing commands/handlers even if they have typos (e.g.
  `get_butto1ns` in pm_filter.py stays as-is).
- Before treating any file as "no user-facing strings", actually grep it
  -- the per-file counts in every queue table this project has produced
  were undercounts.
- Before calling anything "dead code" or "unreferenced," grep the WHOLE
  repository, not just the file(s) that define it or the one file you
  happen to be looking at. A confident claim based on a narrow grep is
  worse than no claim -- this session got `TEXTS["HELP_TEXT"]` /
  `TEXTS["AVAILABLE_TEXT_METHODS"]` wrong exactly this way (see the
  correction in the Script.py/Cscript.py section) before the person
  caught it.
- When the same literal string appears with slightly different Unicode
  styling, casing, or emoji in different code paths, give each variant its
  own key rather than merging them -- that preserves the exact current
  rendering. (Many examples: BTN_YES vs BTN_YES_PLAIN vs BTN_YES_INDEX,
  BTN_DONATE vs BTN_DONATE_MONEY vs BTN_DONATE_US, etc.)
- Dead/unused code (never called from anywhere) still gets converted for
  consistency if it's live syntax (not inside a docstring) -- e.g.
  get_butto1ns(), get_reply_markup1(), retry_on_floodwait(). Code disabled
  inside a triple-quoted docstring stays untouched entirely -- don't
  convert strings that aren't actually executing.
- DB-layer functions (in database/*.py) that reply/edit a message directly
  get an optional `lang: str = DEFAULT_LANG` parameter, and the plugin
  call site (which already has `lang` resolved) passes it through
  explicitly -- see database/filters_mdb.py's delete_filter()/del_all()
  this session for the pattern.
- Before converting a message, grep langs/i18n.py for the literal text
  first -- several "new" keys this session turned out to already exist
  from earlier sessions that added keys ahead of wiring up the file
  (connection.py needed zero new keys because of this).

## How to verify your work before reporting done

# 1. Everything still imports/parses
python3 -m py_compile $(find . -name "*.py" -not -path "./venv/*")

# 2. Real errors only (syntax, undefined names) -- ignore SyntaxWarning noise
python3 -m flake8 --select=E9,F821,F822,F823 --max-line-length=200 .

# 3. Every get()/get_btn() call in the repo resolves to a real EN key
python3 -c "
import re, ast, glob
src = open('langs/i18n.py', encoding='utf-8').read()
tree = ast.parse(src)
en = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=='EN')
keys = {t.id for node in en.body if isinstance(node, ast.Assign) for t in node.targets if isinstance(t, ast.Name)}
missing=[]
for f in glob.glob('plugins/**/*.py', recursive=True) + glob.glob('database/**/*.py', recursive=True):
    c=open(f,encoding='utf-8').read()
    for m in re.finditer(r'get(?:_btn)?\([^,]+,\s*[\"\']([A-Z_0-9]+)[\"\']', c):
        if m.group(1) not in keys: missing.append((f,m.group(1)))
print('missing keys:', missing or 'none')
"

# 4. No trailing whitespace
grep -rlP '[ \t]+$' --include="*.py" .

# 5. Full command-vs-help-text cross-check
find . -path ./venv -prune -o -iname "*.py" -print | xargs grep -n "filters.command("

# 6. Confirm no plugin/database file with real user-facing literals was missed
for f in $(find plugins database -name "*.py"); do
  grep -q "langs.i18n" "$f" 2>/dev/null && continue
  msgs=$(grep -oE '\.(reply_text|reply|answer|edit_text|edit|send_message|send_photo|send_document)\(\s*(f?"|f?'"'"')' "$f" | wc -l)
  btns=$(grep -oE 'InlineKeyboardButton\(\s*(text\s*=\s*)?(f?"|f?'"'"')' "$f" | wc -l)
  [ $((msgs+btns)) -gt 0 ] && echo "$f : msgs=$msgs btns=$btns"
done

## Person's decisions on the three open items (this session)

1. **Script.py/Cscript.py**: if the two contain the same content, remove it
   from whichever copy is less centralized / has less of that type of data
   in it, keeping the more centralized version. Investigated before
   filing this: Script.py and Cscript.py aren't really duplicates of each
   other (different features — help/about menus vs channel-posting
   messages).
   **CORRECTION (caught by the person, my earlier claim was wrong):** I
   initially said `TEXTS["HELP_TEXT"]` and `TEXTS["AVAILABLE_TEXT_METHODS"]`
   in Cscript.py were dead/unreferenced — that was false, based on an
   incomplete grep that only checked postc.py and Cscript.py themselves.
   Both keys are actively used in `plugins/help.py`'s `chelp()` handler
   (`TEXTS.get("HELP_TEXT", ...)` / `TEXTS.get("AVAILABLE_TEXT_METHODS", ...)`,
   imported via `from plugins.Extra.Cscript import TEXTS`). Nothing was
   removed during any earlier editing session — retracted. **Lesson:**
   before calling anything "dead code" or "unreferenced," grep the WHOLE
   repo, not just the file(s) that define it.
   The genuine finding that *was* correct: `get_random_sticker()`, called
   in `chelp()`, was undefined *from help.py's point of view* — but it
   turned out to already be implemented in `plugins/Extra/postc.py`
   (`return random.choice(TEXTS["random_sticker"])`), just not imported
   into help.py. **FIXED this session** — see below.

2. **cb_handler breakup**: agreed it can't be broken up wholesale since
   it's a universal fallback catch-all (pyrogram dispatches
   callback_query to the first matching handler in registration order, so
   a true catch-all has to stay last). Approach: extract only branches
   that key off a clean `callback_data.startswith(prefix)` into their own
   `@Client.on_callback_query(filters.regex(...))` handlers registered
   BEFORE cb_handler in the file/import order. Leave genuinely ambiguous
   or fallback-dependent branches inside cb_handler untouched.
3. **Check i18n.py for existing keys before adding new ones**: confirmed
   as standing practice (already saved work once this session on
   connection.py, which needed zero new keys).

## Queue for next few sessions (in order)

1. **Investigate first, execute nothing yet**: full diff of Script.py's
   `XXX_TXT` class attributes against langs/i18n.py's existing
   `HELP_*`/`ABOUT_*`/etc. keys, and Cscript.py's `TEXTS` dict entries
   against the same. `HELP_TEXT`/`AVAILABLE_TEXT_METHODS`/`random_sticker`
   are confirmed live and correctly wired (see correction above) --
   remove them from the "check if dead" list, they're not candidates.
   Focus is now genuinely on: which entries (if any) overlap with content
   already centralized in langs/i18n.py, and which are unique and just
   need migrating. Produce a concrete before/after key-mapping proposal
   for review -- don't touch code yet.
2. **Execute the Script.py/Cscript.py consolidation** based on the
   reviewed mapping from step 1: migrate unique content into
   langs/i18n.py, remove any genuinely-confirmed-dead entries (grep the
   WHOLE repo before calling anything dead -- see the correction above
   for why that matters).
3. **cb_handler graceful breakup**: extract the clean
   `callback_data.startswith(prefix)` branches into their own
   `@Client.on_callback_query(filters.regex(...))` handlers ahead of
   cb_handler, per the approach above. Verify dispatch order is preserved
   (test/trace through a few callback_data values from each extracted
   prefix and a few that should still fall through to the catch-all).
4. **README.md refresh** -- do this last since steps 1-3 will still be
   changing the file layout and templating story; refresh once the dust
   settles rather than twice.
5. **HI translation pass** over the large EN-only key surface added
   across all sessions -- lowest priority, most time-intensive, whenever
   there's bandwidth. Not blocking anything else.

## Immediate next step

**New top priority, ahead of the queue below**: the FILE_DB_URI decision.
Ask the person directly: is `FILE_DB_URI` meant to be a genuinely separate
database from `DATABASE_URI` in real deployments, or should it just
fall back to `DATABASE_URI` when unset (restoring the commented-out
`#if MULTIPLE_DATABASE else DATABASE_URI` logic, minus the undefined
`MULTIPLE_DATABASE` variable)? Once that's answered, the fix is small and
mechanical (one line in info.py) but touches a real crash risk, so get
the direction first. Also worth a one-line fix once confirmed: the
`PUBLIC_FILE_CHANNEL`/`BATCH_FILE_CHANNEL` int('') crash from the same
"empty string vs safe numeric default" pattern.

After that's resolved, the earlier queue (still valid, just now second
priority):
