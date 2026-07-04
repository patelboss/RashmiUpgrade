/* ── AutoFile Search Telegram Web App ─────────────────────────────────────
   Communicates with the bot's aiohttp server endpoints.
   Passes data directly back to the active chat screen using the WebApp SDK.
────────────────────────────────────────────────────────────────────────── */

console.log("[BOOT] Initializing AutoFile Mini-App Client Layer...");

const tg = window.Telegram?.WebApp;

function clientLog(...args) {
  console.log("[WEBAPP]", ...args);
}

function clientWarn(...args) {
  console.warn("[WEBAPP]", ...args);
}

function clientError(...args) {
  console.error("[WEBAPP]", ...args);
}

function getTelegramIdentity() {
  const nativeUserId = tg?.initDataUnsafe?.user?.id || "";
  const initData = tg?.initData || "";
  return {
    user_id: nativeUserId,
    init_data: initData
  };
}

function logTelegramIdentity(stage) {
  const identity = getTelegramIdentity();
  clientLog(`[იდენტ:${stage}] initData length = ${identity.init_data ? identity.init_data.length : 0}`);
  clientLog(`[იდენტ:${stage}] user_id =`, identity.user_id || "");
  clientLog(`[იდენტ:${stage}] initDataUnsafe.user =`, tg?.initDataUnsafe?.user || undefined);
  clientLog(`[იდენტ:${stage}] initData raw =`, identity.init_data || "");
}

if (tg) {
  clientLog("Telegram Web App Environment detected. Syncing layout parameters...");
  tg.ready();
  tg.expand();
  tg.enableClosingConfirmation?.();
  tg.setHeaderColor?.('bg_color');
  clientLog("SDK state initialized.");
  logTelegramIdentity("BOOT");
} else {
  clientWarn("Running platform layout outside localized Telegram client context.");
}

const BASE_URL = window.location.origin;
clientLog("API endpoint pointer configured to origin root:", BASE_URL);
clientLog("Current page URL:", window.location.href);
clientLog("Document readyState:", document.readyState);

const state = {
  query:      '',
  fileType:   '',
  offset:     0,
  pageSize:   15,
  loading:    false,
  hasMore:    false,
  results:    [],
  activeTab:  'search',
  currentFile: null,
};

const $ = (sel) => document.querySelector(sel);
const searchInput   = $('#searchInput');
const clearBtn      = $('#clearBtn');
const resultsGrid   = $('#resultsGrid');
const loadMoreBtn   = $('#loadMoreBtn');
const searchStatus  = $('#searchStatus');
const emptyState    = $('#emptyState');
const idleState     = $('#idleState');
const recentGrid    = $('#recentGrid');
const recentCount   = $('#recentCount');
const recentLoader  = $('#recentLoader');
const recentEmpty   = $('#recentEmpty');
const sheetOverlay  = $('#sheetOverlay');
const bottomSheet   = $('#bottomSheet');
const sheetContent  = $('#sheetContent');

function fmt(bytes) {
  if (!bytes || bytes === 0) return '–';
  const b = Number(bytes);
  if (b < 1024)       return b + ' B';
  if (b < 1048576)    return (b / 1024).toFixed(1) + ' KB';
  if (b < 1073741824) return (b / 1048576).toFixed(1) + ' MB';
  return (b / 1073741824).toFixed(2) + ' GB';
}

function fmtUptime(s) {
  const d = Math.floor(s / 86400);
  const h = Math.floor((s % 86400) / 3600);
  const m = Math.floor((s % 3600) / 60);
  const parts = [];
  if (d) parts.push(`${d}d`);
  if (h) parts.push(`${h}h`);
  parts.push(`${m}m`);
  return parts.join(' ');
}

function typeEmoji(type) {
  switch (type) {
    case 'video':    return '🎬';
    case 'audio':    return '🎵';
    case 'document': return '📄';
    default:         return '📁';
  }
}

function typeBadgeClass(type) {
  const map = { video: 'badge-video', audio: 'badge-audio', document: 'badge-document' };
  return map[type] || 'badge-default';
}

function thumbClass(type) {
  const map = { video: 'video', audio: 'audio', document: 'document' };
  return map[type] || 'default';
}

function debounce(fn, delay = 400) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), delay);
  };
}

function showFeedback(text = '✓') {
  if (tg?.showPopup) return;
  const el = document.createElement('div');
  el.textContent = text;
  el.style.cssText = `
    position:fixed; bottom:80px; left:50%; transform:translateX(-50%);
    background:var(--accent); color:var(--btn-text);
    padding:8px 18px; border-radius:100px; font-size:.82rem; font-weight:600;
    z-index:999; pointer-events:none; opacity:0; transition:opacity .2s;
  `;
  document.body.appendChild(el);
  requestAnimationFrame(() => { el.style.opacity = '1'; });
  setTimeout(() => {
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 250);
  }, 1800);
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

async function apiFetch(path) {
  clientLog("[FETCH] request path =", path);
  const res = await fetch(BASE_URL + path);
  clientLog("[FETCH] response", { path, status: res.status, ok: res.ok });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

function renderCard(file) {
  const type = (file.file_type || '').toLowerCase().replace('messages.', '');
  const card = document.createElement('div');
  card.className = 'file-card';
  card.innerHTML = `
    <div class="file-thumb ${thumbClass(type)}">${typeEmoji(type)}</div>
    <div class="file-info">
      <div class="file-name" title="${escHtml(file.file_name || '')}">${escHtml(file.file_name || 'Untitled')}</div>
      <div class="file-meta">
        <span class="file-type-badge ${typeBadgeClass(type)}">${type || 'file'}</span>
        <span class="file-size">${fmt(file.file_size)}</span>
      </div>
      <div class="file-caption">${escHtml(file.file_name || 'Untitled')}</div>
    </div>
    <svg class="file-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
  `;
  card.addEventListener('click', () => openSheet(file));
  return card;
}

async function doSearch(reset = true) {
  const trimmedQuery = state.query.trim();
  clientLog("[SEARCH] doSearch invoked", {
    reset,
    query: state.query,
    trimmedQuery,
    fileType: state.fileType,
    offset: state.offset,
    pageSize: state.pageSize,
    loading: state.loading
  });

  logTelegramIdentity("SEARCH-BEFORE");

  if (!trimmedQuery) {
    clientWarn("[SEARCH] skipped: empty query");
    return;
  }
  if (trimmedQuery.length < 3) {
    clientWarn(`[SEARCH] skipped: query too short -> "${trimmedQuery}"`);
    return;
  }
  if (state.loading) {
    clientWarn("[SEARCH] skipped: already loading");
    return;
  }

  if (reset) {
    state.offset = 0;
    state.results = [];
    resultsGrid.innerHTML = '';
    loadMoreBtn.classList.add('hidden');
  }

  state.loading = true;
  idleState.classList.add('hidden');
  emptyState.classList.add('hidden');
  loadMoreBtn.textContent = 'Loading…';

  try {
    const { user_id: nativeUserId, init_data } = getTelegramIdentity();

    const params = new URLSearchParams({
      q: state.query,
      offset: state.offset,
      max: state.pageSize,
      user_id: nativeUserId || "",
      init_data: init_data || ""
    });

    if (state.fileType) params.set('type', state.fileType);

    clientLog("[SEARCH] sending params =", params.toString());
    clientLog("[SEARCH] sending identity snapshot =", {
      user_id: nativeUserId || "",
      init_data_length: init_data ? init_data.length : 0
    });

    const data = await apiFetch(`/api/search?${params}`);
    const files = data.files || [];

    clientLog("[SEARCH] response payload summary =", {
      files_count: files.length,
      total_results: data.total_results,
      next_offset: data.next_offset
    });

    state.results = state.results.concat(files);
    state.offset = typeof data.next_offset === 'number' ? data.next_offset : state.offset + files.length;
    state.hasMore = !!data.next_offset;

    files.forEach(f => resultsGrid.appendChild(renderCard(f)));

    if (state.results.length === 0) {
      emptyState.classList.remove('hidden');
    }

    const total = data.total_results ?? state.results.length;
    searchStatus.textContent = `${total.toLocaleString()} result${total !== 1 ? 's' : ''}`;
    searchStatus.classList.toggle('hidden', state.results.length === 0);

    loadMoreBtn.classList.toggle('hidden', !state.hasMore);
    loadMoreBtn.textContent = 'Load more';
  } catch (err) {
    clientError('[SEARCH] API execution failure context:', err);
    searchStatus.textContent = 'Search unavailable – try again';
    searchStatus.classList.remove('hidden');
    loadMoreBtn.classList.add('hidden');
  } finally {
    state.loading = false;
    clientLog("[SEARCH] doSearch finished. loading =", state.loading);
  }
}

const debouncedSearch = debounce(() => {
  clientLog("[SEARCH] debouncedSearch fired with query =", state.query);
  if (state.query.trim().length >= 3) doSearch();
}, 380);

async function loadRecent() {
  clientLog("[RECENT] loadRecent invoked");
  recentLoader.classList.remove('hidden');
  recentEmpty.classList.add('hidden');
  recentGrid.innerHTML = '';

  try {
    const data = await apiFetch('/api/recent?max=20');
    const files = data.files || [];
    recentCount.textContent = files.length;

    clientLog("[RECENT] response file count =", files.length);

    if (files.length === 0) {
      recentEmpty.classList.remove('hidden');
    } else {
      files.forEach(f => recentGrid.appendChild(renderCard(f)));
    }
  } catch (err) {
    clientError("[RECENT] failed:", err);
    recentEmpty.classList.remove('hidden');
  } finally {
    recentLoader.classList.add('hidden');
  }
}

async function loadStats(forceRefresh = false) {
  clientLog("[STATS] loadStats invoked", { forceRefresh });

  const refreshBtn = $('#refreshStatsBtn');
  if (forceRefresh && refreshBtn) {
    refreshBtn.style.animation = "spin 1s linear infinite";
  }

  try {
    const [health, stats] = await Promise.all([
      apiFetch('/health'),
      apiFetch(`/api/stats${forceRefresh ? '?refresh=true' : ''}`),
    ]);

    clientLog("[STATS] health response =", health);
    clientLog("[STATS] stats response =", stats);

    $('#statFiles').textContent = (stats.total_files ?? '–').toLocaleString();
    $('#statSubs').textContent  = (stats.subscriber_count ?? '–').toLocaleString();

    $('#infoBotName').textContent  = health.bot || '–';
    $('#infoBotAdmin').textContent = health.username ? '@' + health.username : '–';

    $('#infoUsedStorage').textContent = stats.used_storage || '–';
    $('#infoFreeStorage').textContent = stats.free_storage || '–';

    const promoPanel = $('#promoAdPanel');
    if (promoPanel) {
      const promoText = (stats.latest_promo_text || '').trim();
      promoPanel.innerHTML = promoText
        ? promoText
        : '<div class="ad-loading">No promotions at the moment.</div>';
    }
  } catch (err) {
    clientError("[STATS] loading failure:", err);
    ['statFiles', 'statSubs', 'infoUsedStorage', 'infoFreeStorage'].forEach(id => {
      const el = $('#' + id);
      if (el) el.textContent = '–';
    });
    const promoPanel = $('#promoAdPanel');
    if (promoPanel) {
      promoPanel.innerHTML = '<div class="ad-loading">Could not load promotion.</div>';
    }
  } finally {
    if (refreshBtn) {
      refreshBtn.style.animation = "";
    }
  }
}

function openSheet(file) {
  state.currentFile = file;
  const type = (file.file_type || '').toLowerCase().replace('messages.', '');
  clientLog("[SHEET] openSheet for file =", {
    file_id: file._id || file.file_id,
    file_name: file.file_name,
    file_type: file.file_type,
    mime_type: file.mime_type
  });

  sheetContent.innerHTML = `
    <div class="sheet-file-name">${typeEmoji(type)} ${escHtml(file.file_name || 'Untitled')}</div>
    <div class="sheet-meta">
      <div class="sheet-row">
        <span class="sheet-row-key">Type</span>
        <span class="sheet-row-val">${type || 'file'}</span>
      </div>
      <div class="sheet-row">
        <span class="sheet-row-key">Size</span>
        <span class="sheet-row-val">${fmt(file.file_size)}</span>
      </div>
      ${file.mime_type ? `
      <div class="sheet-row">
        <span class="sheet-row-key">MIME</span>
        <span class="sheet-row-val" style="font-size:.72rem">${escHtml(file.mime_type)}</span>
      </div>` : ''}
    </div>
    ${file.caption ? `<div class="sheet-caption">${escHtml(file.caption)}</div>` : ''}
    <div class="sheet-actions">
      <button class="btn-primary" onclick="getFile()">📥 Get File</button>
      <button class="btn-secondary" onclick="closeSheet()">Close</button>
    </div>
  `;

  sheetOverlay.classList.remove('hidden');
  bottomSheet.classList.remove('hidden');
  requestAnimationFrame(() => bottomSheet.classList.add('open'));
}

function closeSheet() {
  clientLog("[SHEET] closeSheet invoked");
  bottomSheet.classList.remove('open');
  setTimeout(() => {
    bottomSheet.classList.add('hidden');
    sheetOverlay.classList.add('hidden');
    state.currentFile = null;
  }, 280);
}

async function getFile(isSendAll = false) {
  let targetId;
  let isProtected = false;

  if (isSendAll) {
    targetId = state.query;
    if (!targetId) {
      clientWarn("[SEND_FILE] skipped: isSendAll but no query available");
      return;
    }
  } else {
    const file = state.currentFile;
    if (!file) {
      clientWarn("[SEND_FILE] skipped: no current file selected");
      return;
    }
    targetId = file._id || file.file_id;
    const cb = document.getElementById('protectContentCb');
    if (cb) isProtected = cb.checked;
  }

  const actionBtn = isSendAll ? document.getElementById('sendAllBtn') : document.querySelector('.btn-primary');
  const originalText = actionBtn ? actionBtn.innerHTML : '📥 Get File';

  clientLog("[SEND_FILE] getFile invoked", {
    isSendAll,
    targetId,
    isProtected
  });

  logTelegramIdentity("SEND-BEFORE");

  if (actionBtn) {
    actionBtn.innerHTML = '🔄 Processing...';
    actionBtn.disabled = true;
    actionBtn.style.opacity = '0.7';
    actionBtn.style.pointerEvents = 'none';
  }

  try {
    const { user_id: nativeUserId, init_data } = getTelegramIdentity();

    clientLog("[SEND_FILE] request body snapshot =", {
      file_id: targetId,
      is_send_all: isSendAll,
      protect: isProtected,
      user_id: nativeUserId || "",
      init_data_length: init_data ? init_data.length : 0
    });

    const response = await fetch(`${BASE_URL}/api/send_file`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_id: targetId,
        is_send_all: isSendAll,
        protect: isProtected,
        user_id: nativeUserId || "",
        init_data: init_data || ""
      })
    });

    const resData = await response.json();

    clientLog("[SEND_FILE] response =", {
      status: response.status,
      ok: response.ok,
      body: resData
    });

    if (response.ok && resData.status === 'direct_sent') {
      clientLog("[SEND_FILE] direct_sent confirmed");
      if (tg && tg.showPopup) {
        tg.showPopup({
          title: "File Dispatched! 🚀",
          message: "𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦.\n\nMinimize or close this window to access your media.",
          buttons: [{ id: "ok", type: "default", text: "OK, Got It!" }]
        });
      } else {
        alert("𝐂𝐡𝐞𝐜𝐤 𝐘𝐨𝐮𝐫 𝐏𝐫𝐢𝐯𝐚𝐭𝐞 𝐦𝐞𝐬𝐬𝐚𝐠𝐞, 𝐈 𝐡𝐚𝐯𝐞 𝐬𝐞𝐧𝐭 𝐟𝐢𝐥𝐞𝐬 𝐢𝐧 𝐩𝐦.");
      }
      if (!isSendAll) closeSheet();
      return;
    }

    if (tg) {
      const prefix = isSendAll ? "allfiles" : "get";
      clientWarn("[SEND_FILE] falling back to Telegram deep-link", { prefix, targetId });
      tg.openTelegramLink(`https://t.me/Rashmi_v2_bot?start=${prefix}_${targetId}`);
      tg.close();
    } else {
      navigator.clipboard?.writeText(`get_${targetId}`).then(() => showFeedback('Query token copied!'));
      if (!isSendAll) closeSheet();
    }
  } catch (err) {
    clientError("[SEND_FILE] pipeline snag. Reverting to safe deep-link:", err);
    if (tg) {
      const prefix = isSendAll ? "allfiles" : "get";
      tg.openTelegramLink(`https://t.me/Rashmi_v2_bot?start=${prefix}_${targetId}`);
    }
  } finally {
    if (actionBtn) {
      actionBtn.innerHTML = originalText;
      actionBtn.disabled = false;
      actionBtn.style.opacity = '1';
      actionBtn.style.pointerEvents = 'auto';
    }
    clientLog("[SEND_FILE] getFile finished");
  }
}

window.getFile = getFile;
window.closeSheet = closeSheet;

function quickSearch(q) {
  clientLog("[SEARCH] quickSearch invoked with =", q);
  searchInput.value = q;
  state.query = q;
  clearBtn.style.display = '';
  doSearch();
}
window.quickSearch = quickSearch;

document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    clientLog("[TAB] clicked =", tab);
    if (tab === state.activeTab) return;
    state.activeTab = tab;

    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    $('#tab-' + tab)?.classList.add('active');

    if (tab === 'recent') loadRecent();
    if (tab === 'stats')  loadStats(false);
  });
});

document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    clientLog("[FILTER] chip selected =", chip.dataset.type);
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.fileType = chip.dataset.type;
    if (state.query.trim()) doSearch();
  });
});

searchInput.addEventListener('input', () => {
  state.query = searchInput.value;
  clientLog("[SEARCH] input changed =", state.query);
  clearBtn.style.display = state.query ? '' : 'none';

  if (!state.query.trim()) {
    state.results = [];
    resultsGrid.innerHTML = '';
    searchStatus.classList.add('hidden');
    emptyState.classList.add('hidden');
    loadMoreBtn.classList.add('hidden');
    idleState.classList.remove('hidden');
    return;
  }
  idleState.classList.add('hidden');
  debouncedSearch();
});

clearBtn.addEventListener('click', () => {
  clientLog("[SEARCH] clear clicked");
  searchInput.value = '';
  state.query = '';
  clearBtn.style.display = 'none';
  resultsGrid.innerHTML = '';
  searchStatus.classList.add('hidden');
  emptyState.classList.add('hidden');
  loadMoreBtn.classList.add('hidden');
  idleState.classList.remove('hidden');
  searchInput.focus();
});

loadMoreBtn.addEventListener('click', () => {
  clientLog("[SEARCH] load more clicked");
  doSearch(false);
});

sheetOverlay.addEventListener('click', closeSheet);

document.getElementById('refreshStatsBtn')?.addEventListener('click', () => {
  clientLog("[STATS] refresh button clicked");
  loadStats(true);
});

clearBtn.style.display = 'none';
idleState.classList.remove('hidden');

const initData = tg?.initDataUnsafe;
clientLog("[BOOT] initDataUnsafe =", initData || {});
clientLog("[BOOT] initData raw =", tg?.initData || "");

if (initData?.start_param) {
  const q = decodeURIComponent(initData.start_param).replace(/_/g, ' ');
  clientLog(`Launch runtime contextual starting search parameter hooked: "${q}"`);
  if (q) {
    searchInput.value = q;
    state.query = q;
    clearBtn.style.display = '';
    idleState.classList.add('hidden');
    setTimeout(() => doSearch(), 300);
  }
}

const themeToggleBtn = document.getElementById('themeToggleBtn');

function initTheme() {
  const savedTheme = localStorage.getItem('user-theme');
  clientLog("[THEME] initTheme", { savedTheme, telegramColorScheme: tg?.colorScheme });

  if (savedTheme) {
    if (savedTheme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
    return;
  }

  if (tg && tg.colorScheme) {
    clientLog(`Telegram client color scheme detected: ${tg.colorScheme}`);
    if (tg.colorScheme === 'light') {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
    return;
  }

  const systemPrefersLight = window.matchMedia('(prefers-color-scheme: light)').matches;
  clientLog(`Fallback system environment configuration light mode profile match: ${systemPrefersLight}`);
  if (systemPrefersLight) {
    document.body.classList.add('light-theme');
  } else {
    document.body.classList.remove('light-theme');
  }
}

if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    const current = document.body.classList.contains('light-theme') ? 'light' : 'dark';
    localStorage.setItem('user-theme', current);
    clientLog("[THEME] toggled to =", current);
  });
}

if (tg) {
  tg.onEvent('themeChanged', () => {
    clientLog("[THEME] Telegram themeChanged event fired");
    if (!localStorage.getItem('user-theme')) {
      initTheme();
    }
  });
}

initTheme();
