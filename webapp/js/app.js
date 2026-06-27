/* ── AutoFile Search Telegram Web App ─────────────────────────────────────
   Communicates with the bot's aiohttp server endpoints.
   Falls back gracefully when running outside Telegram.
────────────────────────────────────────────────────────────────────────── */

// ── Telegram Web App SDK init ─────────────────────────────────────────────
const tg = window.Telegram?.WebApp;
if (tg) {
  tg.ready();
  tg.expand();
  tg.enableClosingConfirmation?.();
  tg.setHeaderColor?.('bg_color');
}

// ── Base URL of the aiohttp server (same origin as the Web App) ───────────
const BASE_URL = window.location.origin;

// ── State ─────────────────────────────────────────────────────────────────
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

// ── DOM refs ──────────────────────────────────────────────────────────────
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

// ── Utilities ─────────────────────────────────────────────────────────────
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
  return (...args) => { clearTimeout(t); t = setTimeout(() => fn(...args), delay); };
}

function showFeedback(text = '✓') {
  if (tg?.showPopup) return; // use native if available
  // simple toast fallback
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

// ── API helpers ───────────────────────────────────────────────────────────
async function apiFetch(path) {
  const res = await fetch(BASE_URL + path);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

// ── Render a file card ────────────────────────────────────────────────────
function renderCard(file) {
  const type    = (file.file_type || '').toLowerCase().replace('messages.', '');
  const card    = document.createElement('div');
  card.className = 'file-card';
  card.innerHTML = `
    <div class="file-thumb ${thumbClass(type)}">${typeEmoji(type)}</div>
    <div class="file-info">
      <div class="file-name" title="${escHtml(file.file_name || '')}">${escHtml(file.file_name || 'Untitled')}</div>
      <div class="file-meta">
        <span class="file-type-badge ${typeBadgeClass(type)}">${type || 'file'}</span>
        <span class="file-size">${fmt(file.file_size)}</span>
      </div>
      ${file.caption ? `<div class="file-caption">${escHtml(file.caption)}</div>` : ''}
    </div>
    <svg class="file-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
  `;
  card.addEventListener('click', () => openSheet(file));
  return card;
}

function escHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Search ────────────────────────────────────────────────────────────────
async function doSearch(reset = true) {
  if (!state.query.trim()) return;
  if (state.loading) return;

  if (reset) {
    state.offset  = 0;
    state.results = [];
    resultsGrid.innerHTML = '';
    loadMoreBtn.classList.add('hidden');
  }

  state.loading = true;
  idleState.classList.add('hidden');
  emptyState.classList.add('hidden');
  loadMoreBtn.textContent = 'Loading…';

  try {
    const params = new URLSearchParams({
      q:         state.query,
      offset:    state.offset,
      max:       state.pageSize,
    });
    if (state.fileType) params.set('type', state.fileType);

    const data = await apiFetch(`/api/search?${params}`);

    const files = data.files || [];
    state.results = state.results.concat(files);
    state.offset  = typeof data.next_offset === 'number' ? data.next_offset : state.offset + files.length;
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
    console.error('Search error', err);
    searchStatus.textContent = 'Search unavailable – try again';
    searchStatus.classList.remove('hidden');
    loadMoreBtn.classList.add('hidden');
  } finally {
    state.loading = false;
  }
}

const debouncedSearch = debounce(() => {
  if (state.query.trim().length >= 2) doSearch();
}, 380);

// ── Recent files ──────────────────────────────────────────────────────────
async function loadRecent() {
  recentLoader.classList.remove('hidden');
  recentEmpty.classList.add('hidden');
  recentGrid.innerHTML = '';

  try {
    const data = await apiFetch('/api/recent?max=20');
    const files = data.files || [];
    recentCount.textContent = files.length;

    if (files.length === 0) {
      recentEmpty.classList.remove('hidden');
    } else {
      files.forEach(f => recentGrid.appendChild(renderCard(f)));
    }
  } catch {
    recentEmpty.classList.remove('hidden');
  } finally {
    recentLoader.classList.add('hidden');
  }
}

// ── Stats ─────────────────────────────────────────────────────────────────
async function loadStats() {
  try {
    const [health, stats] = await Promise.all([
      apiFetch('/health'),
      apiFetch('/api/stats'),
    ]);

    $('#statFiles').textContent   = (stats.total_files  ?? '–').toLocaleString();
    $('#statUsers').textContent   = (stats.total_users  ?? '–').toLocaleString();
    $('#statChats').textContent   = (stats.total_chats  ?? '–').toLocaleString();
    $('#statFilters').textContent = (stats.total_filters ?? '–').toLocaleString();

    $('#infoBotName').textContent     = health.bot      || '–';
    $('#infoBotUsername').textContent  = health.username ? '@' + health.username : '–';
    $('#infoUptime').textContent      = health.uptime_seconds ? fmtUptime(health.uptime_seconds) : '–';
  } catch {
    ['statFiles', 'statUsers', 'statChats', 'statFilters'].forEach(id => {
      $('#' + id).textContent = '–';
    });
  }
}

// ── Bottom sheet ──────────────────────────────────────────────────────────
function openSheet(file) {
  state.currentFile = file;
  const type = (file.file_type || '').toLowerCase().replace('messages.', '');

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
  bottomSheet.classList.remove('open');
  setTimeout(() => {
    bottomSheet.classList.add('hidden');
    sheetOverlay.classList.add('hidden');
    state.currentFile = null;
  }, 280);
}

function getFile() {
  const file = state.currentFile;
  if (!file) return;

  // Send file_id back to the bot via Telegram Web App sendData
  if (tg?.sendData) {
    tg.sendData(JSON.stringify({ action: 'get_file', file_id: file._id || file.file_id }));
    closeSheet();
    showFeedback('Sending to bot…');
  } else {
    // Fallback: copy file ID to clipboard
    navigator.clipboard?.writeText(file._id || file.file_id || '')
      .then(() => showFeedback('File ID copied!'))
      .catch(() => showFeedback('Use bot to get file'));
    closeSheet();
  }
}

window.getFile  = getFile;
window.closeSheet = closeSheet;

function quickSearch(q) {
  searchInput.value = q;
  state.query = q;
  clearBtn.style.display = '';
  doSearch();
}
window.quickSearch = quickSearch;

// ── Tab switching ─────────────────────────────────────────────────────────
document.querySelectorAll('.tab').forEach(btn => {
  btn.addEventListener('click', () => {
    const tab = btn.dataset.tab;
    if (tab === state.activeTab) return;
    state.activeTab = tab;

    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    $('#tab-' + tab)?.classList.add('active');

    if (tab === 'recent') loadRecent();
    if (tab === 'stats')  loadStats();
  });
});

// ── Filter chips ──────────────────────────────────────────────────────────
document.querySelectorAll('.chip').forEach(chip => {
  chip.addEventListener('click', () => {
    document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
    chip.classList.add('active');
    state.fileType = chip.dataset.type;
    if (state.query.trim()) doSearch();
  });
});

// ── Search input events ───────────────────────────────────────────────────
searchInput.addEventListener('input', () => {
  state.query = searchInput.value;
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

loadMoreBtn.addEventListener('click', () => doSearch(false));

// Overlay click closes sheet
sheetOverlay.addEventListener('click', closeSheet);

// ── Init ──────────────────────────────────────────────────────────────────
clearBtn.style.display = 'none';
idleState.classList.remove('hidden');

// If opened via Telegram startapp with a query param, auto-search
const initData = tg?.initDataUnsafe;
if (initData?.start_param) {
  const q = decodeURIComponent(initData.start_param).replace(/_/g, ' ');
  if (q) {
    searchInput.value = q;
    state.query = q;
    clearBtn.style.display = '';
    idleState.classList.add('hidden');
    setTimeout(() => doSearch(), 300);
  }
}
