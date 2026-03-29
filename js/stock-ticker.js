/**
 * Stock Ticker & Sparkline Chart
 * Custom canvas-based sparklines with grunge aesthetic.
 */

(function () {
  'use strict';

  const COLORS = {
    up: '#34d399',
    down: '#f87171',
    neutral: '#9b9590',
    grid: 'rgba(255,255,255,0.03)',
    glow: 0.6,
  };

  /**
   * Draw a sparkline on a canvas element.
   */
  function drawSparkline(canvas, data, isUp) {
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const w = canvas.clientWidth;
    const h = canvas.clientHeight;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    ctx.scale(dpr, dpr);

    if (!data || data.length < 2) return;

    const color = isUp ? COLORS.up : (isUp === false ? COLORS.down : COLORS.neutral);
    const points = data.length;
    const stepX = w / (points - 1);

    // Subtle horizontal grid lines
    ctx.strokeStyle = COLORS.grid;
    ctx.lineWidth = 0.5;
    for (let i = 1; i < 4; i++) {
      const y = (h / 4) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // Gradient fill under line
    const gradient = ctx.createLinearGradient(0, 0, 0, h);
    gradient.addColorStop(0, color.replace(')', ', 0.15)').replace('rgb', 'rgba'));
    gradient.addColorStop(1, 'transparent');

    ctx.beginPath();
    ctx.moveTo(0, h);
    for (let i = 0; i < points; i++) {
      const x = i * stepX;
      const y = h - (data[i] / 100) * h * 0.85 - h * 0.075;
      if (i === 0) ctx.lineTo(x, y);
      else {
        // Smooth curve
        const prevX = (i - 1) * stepX;
        const prevY = h - (data[i - 1] / 100) * h * 0.85 - h * 0.075;
        const cpX = (prevX + x) / 2;
        ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
      }
    }
    ctx.lineTo(w, h);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Main line
    ctx.beginPath();
    for (let i = 0; i < points; i++) {
      const x = i * stepX;
      const y = h - (data[i] / 100) * h * 0.85 - h * 0.075;
      if (i === 0) ctx.moveTo(x, y);
      else {
        const prevX = (i - 1) * stepX;
        const prevY = h - (data[i - 1] / 100) * h * 0.85 - h * 0.075;
        const cpX = (prevX + x) / 2;
        ctx.bezierCurveTo(cpX, prevY, cpX, y, x, y);
      }
    }
    ctx.strokeStyle = color;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Glow effect on line
    ctx.shadowColor = color;
    ctx.shadowBlur = 8;
    ctx.strokeStyle = color.replace(')', `, ${COLORS.glow})`).replace('rgb', 'rgba');
    ctx.lineWidth = 1;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Current price dot (last point)
    const lastX = (points - 1) * stepX;
    const lastY = h - (data[points - 1] / 100) * h * 0.85 - h * 0.075;

    // Outer glow
    ctx.beginPath();
    ctx.arc(lastX, lastY, 4, 0, Math.PI * 2);
    ctx.fillStyle = color.replace(')', ', 0.25)').replace('rgb', 'rgba');
    ctx.fill();

    // Inner dot
    ctx.beginPath();
    ctx.arc(lastX, lastY, 2, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
  }

  /**
   * Format price for display.
   */
  function formatPrice(price) {
    if (price >= 10000) return price.toLocaleString('en-US', { maximumFractionDigits: 0 });
    if (price >= 100) return price.toLocaleString('en-US', { maximumFractionDigits: 1 });
    return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }

  /**
   * Render the ticker section for a hub.
   */
  function renderTickers(containerId, stocks) {
    const container = document.getElementById(containerId);
    if (!container || !stocks || stocks.length === 0) return;

    container.innerHTML = stocks.map((s, i) => {
      const isUp = s.change >= 0;
      const arrow = isUp ? '&#9650;' : '&#9660;';
      const colorClass = isUp ? 'ticker-up' : 'ticker-down';

      return `
        <div class="ticker-card" data-index="${i}">
          <div class="ticker-top">
            <div class="ticker-symbol">${s.symbol.replace('^', '')}</div>
            <div class="ticker-name">${s.name}</div>
          </div>
          <div class="ticker-chart">
            <canvas class="sparkline-canvas" id="spark-${containerId}-${i}"></canvas>
          </div>
          <div class="ticker-bottom">
            <div class="ticker-price">${formatPrice(s.price)}</div>
            <div class="ticker-change ${colorClass}">
              <span>${arrow}</span>
              <span>${isUp ? '+' : ''}${s.change_pct.toFixed(2)}%</span>
            </div>
          </div>
        </div>
      `;
    }).join('');

    // Draw sparklines after DOM update
    requestAnimationFrame(() => {
      stocks.forEach((s, i) => {
        const canvas = document.getElementById(`spark-${containerId}-${i}`);
        if (canvas && s.sparkline) {
          drawSparkline(canvas, s.sparkline, s.change >= 0);
        }
      });
    });
  }

  /**
   * Render related stock headlines.
   */
  function renderStockHeadlines(containerId, articles, symbols) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Build regex from symbols
    const symbolNames = symbols.flatMap(s => [
      s.symbol.replace('^', ''),
      s.name,
    ]);
    const pattern = new RegExp(symbolNames.join('|'), 'i');

    // Filter articles mentioning any tracked stock
    const relevant = (articles || [])
      .filter(a => pattern.test(a.title) || pattern.test(a.description || ''))
      .slice(0, 6);

    if (relevant.length === 0) {
      container.style.display = 'none';
      return;
    }

    container.innerHTML = `
      <div class="headlines-title">related headlines</div>
      <div class="headlines-list">
        ${relevant.map(a => `
          <a href="${a.url}" target="_blank" rel="noopener" class="headline-item">
            <span class="headline-source">${a.source}</span>
            <span class="headline-text">${a.title}</span>
          </a>
        `).join('')}
      </div>
    `;
  }

  /**
   * Initialize: load stock data and render.
   */
  async function initStockTicker(hub) {
    const stockUrl = `../data/stocks-${hub}.json`;
    const tickerContainer = document.getElementById('stock-tickers');
    const headlineContainer = document.getElementById('stock-headlines');

    if (!tickerContainer) return;

    try {
      const resp = await fetch(stockUrl);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      if (data.stocks && data.stocks.length > 0) {
        renderTickers('stock-tickers', data.stocks);

        // Try to load related headlines from news data
        const newsFiles = {
          ai: '../data/ai-news.json',
          finance: '../data/finance-news.json',
          economics: '../data/economics-news.json',
        };
        try {
          const newsResp = await fetch(newsFiles[hub]);
          if (newsResp.ok) {
            const newsData = await newsResp.json();
            renderStockHeadlines('stock-headlines', newsData.articles, data.stocks);
          }
        } catch (e) { /* no headlines, that's ok */ }
      }
    } catch (err) {
      console.log('Stock data not yet available:', err.message);
      tickerContainer.innerHTML = '';
    }
  }

  // Resize handler for sparklines
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      document.querySelectorAll('.sparkline-canvas').forEach(canvas => {
        const idx = canvas.id.split('-').pop();
        // Re-render would need data; skip for now since resize is rare
      });
    }, 300);
  });

  // Expose init function
  window.initStockTicker = initStockTicker;
})();
