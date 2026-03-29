# My Hub

Personal information dashboard hosted on GitHub Pages. Modular design — add new Hubs as needed.

## Current Hubs

- **AI Hub** — AI/LLM/ML news auto-collected from English & Japanese sources

## Setup

### 1. Create GitHub Repository

```bash
cd my-hub
git init
git add .
git commit -m "Initial commit"
gh repo create my-hub --public --push --source=.
```

### 2. Enable GitHub Pages

1. Go to repo **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: `main` / `/ (root)`
4. Save

Your site will be live at: `https://<username>.github.io/my-hub/`

### 3. Run Initial News Fetch

```bash
python3 scripts/fetch-news.py
git add data/ai-news.json
git commit -m "Initial news data"
git push
```

### 4. Enable GitHub Actions

Actions are enabled by default. The workflow will:
- Run 3x daily (7:00, 13:00, 21:00 JST)
- Fetch RSS feeds + Hacker News API
- Commit updated `data/ai-news.json`
- You can also trigger manually: **Actions** → **Fetch AI News** → **Run workflow**

## Project Structure

```
my-hub/
├── index.html              # Hub home (portal)
├── ai/
│   └── index.html          # AI Hub dashboard
├── css/
│   └── style.css           # Shared styles
├── js/
│   └── ai-hub.js           # AI Hub logic
├── data/
│   └── ai-news.json        # Auto-generated news data
├── scripts/
│   └── fetch-news.py       # News fetcher (used by Actions)
└── .github/
    └── workflows/
        └── fetch-news.yml  # Scheduled workflow
```

## Adding a New Hub

1. Create a new folder (e.g., `finance/`)
2. Add `index.html` inside it
3. Link from `index.html` hub grid
4. If it needs data fetching, add a script + workflow

## News Sources

### English
- TechCrunch AI
- The Verge AI
- Ars Technica
- MIT Technology Review AI
- Google News (AI search)
- Hacker News (Algolia API)

### Japanese
- ITmedia AI+
- GIGAZINE
- Google News JP (AI search)

## Cost

**$0** — Everything runs on free tiers:
- GitHub Pages (static hosting)
- GitHub Actions (free for public repos)
- RSS feeds & Hacker News API (no API keys needed)
