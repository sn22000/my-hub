/**
 * AI Hub - News Dashboard
 */

const DATA_URL = '../data/ai-news.json';

const state = {
  articles: [],
  filtered: [],
  activeFilter: 'all',
  activeLang: 'all',
  searchQuery: '',
};

// --- DOM ---
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

// --- Helpers ---
function timeAgo(isoDate) {
  const now = new Date();
  const date = new Date(isoDate);
  const diffMs = now - date;
  const mins = Math.floor(diffMs / 60000);
  const hours = Math.floor(diffMs / 3600000);
  const days = Math.floor(diffMs / 86400000);

  if (mins < 1) return 'just now';
  if (mins < 60) return `${mins}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString('ja-JP', { month: 'short', day: 'numeric' });
}

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

// --- Rendering ---
function renderStats() {
  const total = state.articles.length;
  const en = state.articles.filter(a => a.lang === 'en').length;
  const ja = state.articles.filter(a => a.lang === 'ja').length;
  const sources = new Set(state.articles.map(a => a.source)).size;

  $('#stat-total').textContent = total;
  $('#stat-en').textContent = en;
  $('#stat-ja').textContent = ja;
  $('#stat-sources').textContent = sources;
}

function renderArticles() {
  const grid = $('#news-grid');
  const articles = state.filtered;

  if (articles.length === 0) {
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <p>No articles found matching your filters.</p>
      </div>
    `;
    return;
  }

  grid.innerHTML = articles.map(article => {
    const hnStats = article.hn_points
      ? `<span class="hn-stats">▲${article.hn_points} · ${article.hn_comments || 0} comments</span>`
      : '';

    return `
      <article class="news-card">
        <div class="news-card-header">
          <span class="news-source">${escapeHtml(article.source)}</span>
          <span class="news-lang lang-${article.lang}">${article.lang}</span>
          <span>${timeAgo(article.published)}</span>
        </div>
        <h3 class="news-title">
          <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener">${escapeHtml(article.title)}</a>
        </h3>
        ${article.description ? `<p class="news-desc">${escapeHtml(article.description)}</p>` : ''}
        <div class="news-meta">
          <span class="news-category">${escapeHtml(article.category)}</span>
          ${hnStats}
        </div>
      </article>
    `;
  }).join('');
}

function applyFilters() {
  let result = [...state.articles];

  // Category filter
  if (state.activeFilter !== 'all') {
    result = result.filter(a => a.category === state.activeFilter);
  }

  // Language filter
  if (state.activeLang !== 'all') {
    result = result.filter(a => a.lang === state.activeLang);
  }

  // Search
  if (state.searchQuery) {
    const q = state.searchQuery.toLowerCase();
    result = result.filter(a =>
      a.title.toLowerCase().includes(q) ||
      (a.description || '').toLowerCase().includes(q) ||
      a.source.toLowerCase().includes(q)
    );
  }

  state.filtered = result;
  renderArticles();
}

// --- Event Handlers ---
function setupFilters() {
  // Category filters
  $$('.filter-btn[data-category]').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.filter-btn[data-category]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeFilter = btn.dataset.category;
      applyFilters();
    });
  });

  // Language filters
  $$('.filter-btn[data-lang]').forEach(btn => {
    btn.addEventListener('click', () => {
      $$('.filter-btn[data-lang]').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      state.activeLang = btn.dataset.lang;
      applyFilters();
    });
  });

  // Search
  const searchBox = $('#search-box');
  if (searchBox) {
    let debounce;
    searchBox.addEventListener('input', (e) => {
      clearTimeout(debounce);
      debounce = setTimeout(() => {
        state.searchQuery = e.target.value;
        applyFilters();
      }, 200);
    });
  }
}

// --- Init ---
async function init() {
  const grid = $('#news-grid');
  grid.innerHTML = `
    <div class="loading" style="grid-column: 1 / -1;">
      <div class="loading-spinner"></div>
      <p>Loading AI news...</p>
    </div>
  `;

  try {
    const resp = await fetch(DATA_URL);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    state.articles = data.articles || [];
    state.filtered = [...state.articles];

    // Update time
    if (data.updated_at) {
      const d = new Date(data.updated_at);
      $('#update-time').textContent = `Updated: ${d.toLocaleString('ja-JP')}`;
    }

    renderStats();
    renderArticles();
    setupFilters();
  } catch (err) {
    console.error('Failed to load news:', err);
    grid.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1;">
        <p>Failed to load news data.</p>
        <p style="font-size: 0.8rem; margin-top: 8px;">Run the fetch script first or wait for GitHub Actions.</p>
        <p style="font-size: 0.75rem; margin-top: 4px; color: var(--text-muted);">${escapeHtml(err.message)}</p>
      </div>
    `;
  }
}

document.addEventListener('DOMContentLoaded', init);
