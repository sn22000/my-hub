/**
 * Travel Hub - News Dashboard
 */
const DATA_URL = '../data/travel-news.json';
const state = { articles: [], filtered: [], activeFilter: 'all', activeLang: 'all', searchQuery: '' };
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

function timeAgo(isoDate) {
  const now = new Date(), date = new Date(isoDate), diffMs = now - date;
  const mins = Math.floor(diffMs / 60000), hours = Math.floor(diffMs / 3600000), days = Math.floor(diffMs / 86400000);
  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
}

function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }

function renderStats() {
  $('#stat-total').textContent = state.articles.length;
  $('#stat-en').textContent = state.articles.filter(a => a.lang === 'en').length;
  $('#stat-ja').textContent = state.articles.filter(a => a.lang === 'ja').length;
  $('#stat-sources').textContent = new Set(state.articles.map(a => a.source)).size;
}

function renderArticles() {
  const grid = $('#news-grid'), articles = state.filtered;
  if (!articles.length) { grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><p>No articles found.</p></div>'; return; }
  grid.innerHTML = articles.map(a => `
    <article class="news-card">
      <div class="news-card-header">
        <span class="news-source">${escapeHtml(a.source)}</span>
        <span class="news-lang lang-${a.lang}">${a.lang}</span>
        <span>${timeAgo(a.published)}</span>
      </div>
      <h3 class="news-title"><a href="${escapeHtml(a.url)}" target="_blank" rel="noopener">${escapeHtml(a.title)}</a></h3>
      ${a.description ? `<p class="news-desc">${escapeHtml(a.description)}</p>` : ''}
      <div class="news-meta"><span class="news-category">${escapeHtml(a.category)}</span></div>
    </article>
  `).join('');
}

function applyFilters() {
  let r = [...state.articles];
  if (state.activeFilter !== 'all') r = r.filter(a => a.category === state.activeFilter);
  if (state.activeLang !== 'all') r = r.filter(a => a.lang === state.activeLang);
  if (state.searchQuery) { const q = state.searchQuery.toLowerCase(); r = r.filter(a => a.title.toLowerCase().includes(q) || (a.description||'').toLowerCase().includes(q) || a.source.toLowerCase().includes(q)); }
  state.filtered = r; renderArticles();
}

function setupFilters() {
  $$('.filter-btn[data-category]').forEach(b => b.addEventListener('click', () => { $$('.filter-btn[data-category]').forEach(x => x.classList.remove('active')); b.classList.add('active'); state.activeFilter = b.dataset.category; applyFilters(); }));
  $$('.filter-btn[data-lang]').forEach(b => b.addEventListener('click', () => { $$('.filter-btn[data-lang]').forEach(x => x.classList.remove('active')); b.classList.add('active'); state.activeLang = b.dataset.lang; applyFilters(); }));
  const s = $('#search-box'); if (s) { let d; s.addEventListener('input', e => { clearTimeout(d); d = setTimeout(() => { state.searchQuery = e.target.value; applyFilters(); }, 200); }); }
}

async function init() {
  const grid = $('#news-grid');
  grid.innerHTML = '<div class="loading" style="grid-column:1/-1"><div class="loading-spinner"></div><p>loading travel news...</p></div>';
  try {
    const resp = await fetch(DATA_URL); if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    state.articles = data.articles || []; state.filtered = [...state.articles];
    if (data.updated_at) { $('#update-time').textContent = `Updated: ${new Date(data.updated_at).toLocaleString('ja-JP')}`; }
    renderStats(); renderArticles(); setupFilters();
  } catch (err) {
    console.error('Failed:', err);
    grid.innerHTML = '<div class="empty-state" style="grid-column:1/-1"><p>Failed to load travel data.</p></div>';
  }
}
document.addEventListener('DOMContentLoaded', init);
