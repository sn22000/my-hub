#!/usr/bin/env python3
"""
AI News Fetcher
Fetches AI-related news from RSS feeds and Hacker News API,
outputs a JSON file for the static dashboard.
"""

import json
import os
import re
import sys
import hashlib
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen, Request, HTTPRedirectHandler, build_opener
from urllib.error import URLError
from xml.etree import ElementTree as ET
from html import unescape

# --- Configuration ---

RSS_FEEDS = [
    # ==============================
    # English — Major Tech Media
    # ==============================
    {
        "name": "TechCrunch AI",
        "url": "https://techcrunch.com/category/artificial-intelligence/feed/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "The Verge AI",
        "url": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Ars Technica",
        "url": "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Wired AI",
        "url": "https://www.wired.com/feed/tag/ai/latest/rss",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "InfoQ AI",
        "url": "https://feed.infoq.com/ai-ml-data-eng/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "MIT Tech Review AI",
        "url": "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "The Register AI",
        "url": "https://www.theregister.com/software/ai_ml/headlines.atom",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "ZDNet AI",
        "url": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
        "lang": "en",
        "category": "Industry",
    },
    # ==============================
    # English — AI-Specialized Media
    # ==============================
    {
        "name": "AI News",
        "url": "https://www.artificialintelligence-news.com/feed/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "AI Business",
        "url": "https://aibusiness.com/rss.xml",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "MarkTechPost",
        "url": "https://www.marktechpost.com/feed/",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Towards AI",
        "url": "https://pub.towardsai.net/feed",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Synced Review",
        "url": "https://syncedreview.com/feed/",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Last Week in AI",
        "url": "https://lastweekin.ai/feed",
        "lang": "en",
        "category": "Industry",
    },
    # ==============================
    # English — Company / Lab Blogs
    # ==============================
    {
        "name": "OpenAI Blog",
        "url": "https://openai.com/blog/rss.xml",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "Anthropic Engineering",
        "url": "https://raw.githubusercontent.com/conoro/anthropic-engineering-rss-feed/main/anthropic_engineering_rss.xml",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "Google AI Blog",
        "url": "https://blog.google/technology/ai/rss/",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "DeepMind Blog",
        "url": "https://deepmind.google/blog/rss.xml",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "Meta Research",
        "url": "https://research.facebook.com/feed/",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "Microsoft AI Blog",
        "url": "https://blogs.microsoft.com/ai/feed/",
        "lang": "en",
        "category": "Lab",
    },
    {
        "name": "NVIDIA AI Blog",
        "url": "https://blogs.nvidia.com/feed/",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Hugging Face Blog",
        "url": "https://huggingface.co/blog/feed.xml",
        "lang": "en",
        "category": "Lab",
    },
    # ==============================
    # English — Research / Papers
    # ==============================
    {
        "name": "arXiv cs.AI",
        "url": "https://rss.arxiv.org/rss/cs.AI",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "arXiv cs.CL",
        "url": "https://rss.arxiv.org/rss/cs.CL",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "arXiv cs.LG",
        "url": "https://rss.arxiv.org/rss/cs.LG",
        "lang": "en",
        "category": "Research",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - AI",
        "url": "https://news.google.com/rss/search?q=artificial+intelligence+OR+LLM+OR+generative+AI&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Major Tech Media
    # ==============================
    {
        "name": "ITmedia AI+",
        "url": "https://rss.itmedia.co.jp/rss/2.0/aiplus.xml",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "GIGAZINE",
        "url": "https://gigazine.net/news/rss_2.0/",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Impress Watch AI",
        "url": "https://www.watch.impress.co.jp/data/rss/1.0/ipw/feed.rdf",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Publickey",
        "url": "https://www.publickey1.jp/atom.xml",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "ASCII.jp Tech",
        "url": "https://ascii.jp/rss.xml",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Cnet Japan AI",
        "url": "https://japan.cnet.com/rss/index.rdf",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Qiita AI Tag",
        "url": "https://qiita.com/tags/ai/feed",
        "lang": "ja",
        "category": "Community",
    },
    {
        "name": "Zenn AI Topic",
        "url": "https://zenn.dev/topics/ai/feed",
        "lang": "ja",
        "category": "Community",
    },
    # ==============================
    # Japanese — Aggregators
    # ==============================
    {
        "name": "Google News - AI (JP)",
        "url": "https://news.google.com/rss/search?q=AI+%E4%BA%BA%E5%B7%A5%E7%9F%A5%E8%83%BD+OR+LLM+OR+%E7%94%9F%E6%88%90AI&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

# Hacker News Algolia API (free, no key needed)
HN_API_URL = "https://hn.algolia.com/api/v1/search_by_date?query=AI+OR+LLM+OR+GPT+OR+Claude+OR+%22artificial+intelligence%22&tags=story&hitsPerPage=50"

# AI-related keywords for filtering general feeds
AI_KEYWORDS = [
    r"\bAI\b", r"\bartificial intelligence\b", r"\bmachine learning\b",
    r"\bdeep learning\b", r"\bLLM\b", r"\bGPT\b", r"\bClaude\b",
    r"\bOpenAI\b", r"\bAnthro", r"\bGemini\b", r"\bchatbot\b",
    r"\bgenerative\b", r"\btransformer\b", r"\bneural net",
    r"\bcomputer vision\b", r"\bNLP\b", r"\brobotics?\b",
    r"\bMistral\b", r"\bLlama\b", r"\bStable Diffusion\b",
    r"\bMidjourney\b", r"\bSora\b", r"\bCopilot\b",
    r"\bfoundation model\b", r"\bmultimodal\b", r"\bRAG\b",
    r"\bfine.?tun", r"\bprompt engineer", r"\bAGI\b",
    r"\breinforcement learning\b", r"\bdiffusion model\b",
    r"\bvector database\b", r"\bembedding",
    # Japanese
    r"人工知能", r"機械学習", r"深層学習", r"生成AI", r"大規模言語",
    r"チャットボット", r"ロボティクス", r"プロンプト",
    r"ファインチューニング", r"基盤モデル", r"マルチモーダル",
    r"AIエージェント", r"推論", r"学習モデル",
]

AI_PATTERN = re.compile("|".join(AI_KEYWORDS), re.IGNORECASE)

USER_AGENT = "MyHub-NewsFetcher/1.0"
FETCH_TIMEOUT = 15


class SmartRedirectHandler(HTTPRedirectHandler):
    """Handle 308 redirects that urllib doesn't follow by default."""
    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_302(req, fp, code, msg, headers)


_opener = build_opener(SmartRedirectHandler)


def fetch_url(url):
    """Fetch URL content with redirect and error handling."""
    req = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with _opener.open(req, timeout=FETCH_TIMEOUT) as resp:
            return resp.read()
    except (URLError, TimeoutError) as e:
        print(f"  [WARN] Failed to fetch {url}: {e}", file=sys.stderr)
        return None


def strip_html(text):
    """Remove HTML tags from text."""
    if not text:
        return ""
    text = unescape(text)
    return re.sub(r"<[^>]+>", "", text).strip()


def make_id(url):
    """Generate a short unique ID from URL."""
    return hashlib.md5(url.encode()).hexdigest()[:10]


def is_ai_related(title, description=""):
    """Check if an article is AI-related."""
    combined = f"{title} {description}"
    return bool(AI_PATTERN.search(combined))


def parse_rss_date(date_str):
    """Parse various RSS date formats to ISO string."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()

    formats = [
        "%a, %d %b %Y %H:%M:%S %z",      # RFC 822
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",            # ISO 8601
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError:
            continue
    return datetime.now(timezone.utc).isoformat()


def fetch_rss_feed(feed_config):
    """Fetch and parse a single RSS feed."""
    print(f"  Fetching: {feed_config['name']}...")
    data = fetch_url(feed_config["url"])
    if not data:
        return []

    articles = []
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"  [WARN] Parse error for {feed_config['name']}: {e}", file=sys.stderr)
        return []

    # Handle both RSS 2.0 and Atom feeds
    ns = {"atom": "http://www.w3.org/2005/Atom"}

    # RSS 2.0
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "")

        if not title or not link:
            continue

        # For general feeds, filter to AI-related only
        if feed_config["category"] == "General" and not is_ai_related(title, desc):
            continue

        articles.append({
            "id": make_id(link),
            "title": title,
            "url": link,
            "description": desc[:300] if desc else "",
            "source": feed_config["name"],
            "lang": feed_config["lang"],
            "category": feed_config["category"],
            "published": parse_rss_date(pub_date),
        })

    # Atom
    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", "", ns) or "").strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns)
        if link_el is None:
            link_el = entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = strip_html(entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns) or "")
        updated = entry.findtext("atom:updated", "", ns) or entry.findtext("atom:published", "", ns)

        if not title or not link:
            continue

        if feed_config["category"] == "General" and not is_ai_related(title, summary):
            continue

        articles.append({
            "id": make_id(link),
            "title": title,
            "url": link,
            "description": summary[:300] if summary else "",
            "source": feed_config["name"],
            "lang": feed_config["lang"],
            "category": feed_config["category"],
            "published": parse_rss_date(updated),
        })

    print(f"    -> {len(articles)} articles")
    return articles


def fetch_hacker_news():
    """Fetch AI-related stories from Hacker News."""
    print("  Fetching: Hacker News API...")
    data = fetch_url(HN_API_URL)
    if not data:
        return []

    articles = []
    try:
        result = json.loads(data)
    except json.JSONDecodeError:
        return []

    for hit in result.get("hits", []):
        title = hit.get("title", "")
        url = hit.get("url", "")
        if not url:
            url = f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
        created = hit.get("created_at", "")

        if not title:
            continue

        articles.append({
            "id": make_id(url),
            "title": title,
            "url": url,
            "description": "",
            "source": "Hacker News",
            "lang": "en",
            "category": "Community",
            "published": created if created else datetime.now(timezone.utc).isoformat(),
            "hn_points": hit.get("points", 0),
            "hn_comments": hit.get("num_comments", 0),
        })

    print(f"    -> {len(articles)} articles")
    return articles


def deduplicate(articles):
    """Remove duplicate articles based on URL."""
    seen = set()
    unique = []
    for article in articles:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique.append(article)
    return unique


def main():
    print("=== AI News Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")

    all_articles = []

    # Fetch RSS feeds
    for feed in RSS_FEEDS:
        articles = fetch_rss_feed(feed)
        all_articles.extend(articles)

    # Fetch Hacker News
    hn_articles = fetch_hacker_news()
    all_articles.extend(hn_articles)

    # Deduplicate
    all_articles = deduplicate(all_articles)

    # Sort by published date (newest first)
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)

    # Keep only last 7 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = [a for a in all_articles if a.get("published", "") >= cutoff]

    # Limit to 500 articles
    all_articles = all_articles[:500]

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_articles),
        "articles": all_articles,
    }

    # Write output
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "ai-news.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
