#!/usr/bin/env python3
"""
Finance News Fetcher
Fetches finance/markets news from RSS feeds,
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
    # English — Major Financial Media
    # ==============================
    {
        "name": "Reuters Business",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+business+OR+markets&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "CNBC Top News",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "CNBC Finance",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "MarketWatch",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "MarketWatch Breaking",
        "url": "https://feeds.content.dowjones.io/public/rss/mw_bulletins",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "Yahoo Finance",
        "url": "https://finance.yahoo.com/news/rssindex",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "Seeking Alpha",
        "url": "https://seekingalpha.com/feed.xml",
        "lang": "en",
        "category": "Analysis",
    },
    {
        "name": "Investing.com News",
        "url": "https://www.investing.com/rss/news.rss",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "Fortune Finance",
        "url": "https://fortune.com/feed/fortune-feeds/?id=3230629",
        "lang": "en",
        "category": "Markets",
    },
    {
        "name": "Business Insider",
        "url": "https://markets.businessinsider.com/rss/news",
        "lang": "en",
        "category": "Markets",
    },
    # ==============================
    # English — Macro / Economics
    # ==============================
    {
        "name": "FT Markets",
        "url": "https://www.ft.com/markets?format=rss",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "Bloomberg Markets",
        "url": "https://feeds.bloomberg.com/markets/news.rss",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "The Economist Finance",
        "url": "https://www.economist.com/finance-and-economics/rss.xml",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "Fed Reserve News",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "lang": "en",
        "category": "Macro",
    },
    # ==============================
    # English — Crypto / Fintech
    # ==============================
    {
        "name": "CoinDesk",
        "url": "https://news.google.com/rss/search?q=site:coindesk.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Crypto",
    },
    {
        "name": "The Block",
        "url": "https://www.theblock.co/rss.xml",
        "lang": "en",
        "category": "Crypto",
    },
    {
        "name": "Decrypt",
        "url": "https://decrypt.co/feed",
        "lang": "en",
        "category": "Crypto",
    },
    {
        "name": "CoinTelegraph",
        "url": "https://cointelegraph.com/rss",
        "lang": "en",
        "category": "Crypto",
    },
    {
        "name": "TechCrunch Fintech",
        "url": "https://techcrunch.com/category/fintech/feed/",
        "lang": "en",
        "category": "Fintech",
    },
    {
        "name": "Nasdaq News",
        "url": "https://www.nasdaq.com/feed/rssoutbound?category=Markets",
        "lang": "en",
        "category": "Stocks",
    },
    # ==============================
    # English — Investing / Personal Finance
    # ==============================
    {
        "name": "Motley Fool",
        "url": "https://www.fool.com/feeds/index.aspx?id=foolwatch&filetype=xml",
        "lang": "en",
        "category": "Investing",
    },
    {
        "name": "Benzinga",
        "url": "https://www.benzinga.com/feed",
        "lang": "en",
        "category": "Stocks",
    },
    {
        "name": "Zero Hedge",
        "url": "https://feeds.feedburner.com/zerohedge/feed",
        "lang": "en",
        "category": "Markets",
    },
    # ==============================
    # English — Aggregator
    # ==============================
    {
        "name": "Google News - Finance",
        "url": "https://news.google.com/rss/search?q=stock+market+OR+Wall+Street+OR+S%26P500+OR+Fed+rate&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Major Financial Media
    # ==============================
    {
        "name": "日経新聞 マーケット",
        "url": "https://assets.wor.jp/rss/rdf/nikkei/markets.rdf",
        "lang": "ja",
        "category": "Markets",
    },
    {
        "name": "日経新聞 経済",
        "url": "https://assets.wor.jp/rss/rdf/nikkei/economy.rdf",
        "lang": "ja",
        "category": "Macro",
    },
    {
        "name": "Bloomberg Japan",
        "url": "https://news.google.com/rss/search?q=site:bloomberg.co.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Markets",
    },
    {
        "name": "ロイター Japan",
        "url": "https://assets.wor.jp/rss/rdf/reuters/top.rdf",
        "lang": "ja",
        "category": "Markets",
    },
    {
        "name": "東洋経済オンライン",
        "url": "https://toyokeizai.net/list/feed/rss",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "現代ビジネス",
        "url": "https://gendai.media/list/feed/rss",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "ZUU Online",
        "url": "https://zuuonline.com/feed",
        "lang": "ja",
        "category": "Investing",
    },
    {
        "name": "LIMO くらしとお金",
        "url": "https://limo.media/list/feed/rss",
        "lang": "ja",
        "category": "Investing",
    },
    {
        "name": "ITmedia ビジネス",
        "url": "https://rss.itmedia.co.jp/rss/2.0/business.xml",
        "lang": "ja",
        "category": "Markets",
    },
    {
        "name": "CoinPost",
        "url": "https://coinpost.jp/?feed=rss2",
        "lang": "ja",
        "category": "Crypto",
    },
    # ==============================
    # Japanese — Aggregator
    # ==============================
    {
        "name": "Google News - 経済 (JP)",
        "url": "https://news.google.com/rss/search?q=%E6%A0%AA%E5%BC%8F+OR+%E7%B5%8C%E6%B8%88+OR+%E7%82%BA%E6%9B%BF+OR+%E6%97%A5%E7%B5%8C%E5%B9%B3%E5%9D%87+OR+%E4%BB%AE%E6%83%B3%E9%80%9A%E8%B2%A8&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

# Finance-related keywords for filtering general feeds
FINANCE_KEYWORDS = [
    r"\bstock\b", r"\bmarket\b", r"\bS&P", r"\bNasdaq\b", r"\bDow\b",
    r"\bWall Street\b", r"\bFed\b", r"\binterest rate\b", r"\binflation\b",
    r"\bearnings\b", r"\bIPO\b", r"\bETF\b", r"\bbond\b", r"\btreasur",
    r"\bGDP\b", r"\brecession\b", r"\bcrypto\b", r"\bbitcoin\b", r"\bethereum\b",
    r"\bfintech\b", r"\bbanking\b", r"\binvest", r"\bequit",
    r"\bforeign exchange\b", r"\bforex\b", r"\bcommodit",
    r"\bmerger\b", r"\bacquisition\b", r"\bM&A\b", r"\bvaluation\b",
    r"\bhedge fund\b", r"\bventure capital\b", r"\bVC\b",
    # Japanese
    r"株式", r"株価", r"日経平均", r"為替", r"円安", r"円高",
    r"金利", r"インフレ", r"デフレ", r"GDP", r"景気",
    r"仮想通貨", r"暗号資産", r"ビットコイン", r"投資",
    r"IPO", r"決算", r"増収", r"減収", r"配当",
    r"マーケット", r"証券", r"銀行", r"金融",
]

FINANCE_PATTERN = re.compile("|".join(FINANCE_KEYWORDS), re.IGNORECASE)

USER_AGENT = "MyHub-FinanceFetcher/1.0"
FETCH_TIMEOUT = 15


class SmartRedirectHandler(HTTPRedirectHandler):
    """Handle 308 redirects."""
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
    if not text:
        return ""
    text = unescape(text)
    return re.sub(r"<[^>]+>", "", text).strip()


def make_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:10]


def is_finance_related(title, description=""):
    combined = f"{title} {description}"
    return bool(FINANCE_PATTERN.search(combined))


def parse_rss_date(date_str):
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
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

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "dc": "http://purl.org/dc/elements/1.1/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    }

    # RSS 2.0
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        # Some RDF feeds use rdf:about on item
        if not link:
            link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext("{http://purl.org/dc/elements/1.1/}date", "")

        if not title or not link:
            continue

        if feed_config["category"] == "General" and not is_finance_related(title, desc):
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

        if feed_config["category"] == "General" and not is_finance_related(title, summary):
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


def deduplicate(articles):
    seen = set()
    unique = []
    for article in articles:
        if article["url"] not in seen:
            seen.add(article["url"])
            unique.append(article)
    return unique


def main():
    print("=== Finance News Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")

    all_articles = []
    for feed in RSS_FEEDS:
        articles = fetch_rss_feed(feed)
        all_articles.extend(articles)

    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)

    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = [a for a in all_articles if a.get("published", "") >= cutoff]
    all_articles = all_articles[:500]

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_articles),
        "articles": all_articles,
    }

    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "finance-news.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
