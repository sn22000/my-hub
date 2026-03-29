#!/usr/bin/env python3
"""
SEO News Fetcher
Fetches SEO, SEM, content marketing, Google algorithm, and digital marketing news.
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
    # English — Core SEO Media
    # ==============================
    {
        "name": "Search Engine Journal",
        "url": "https://www.searchenginejournal.com/feed/",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Search Engine Land",
        "url": "https://searchengineland.com/feed",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Search Engine Roundtable",
        "url": "https://news.google.com/rss/search?q=site:seroundtable.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Moz Blog",
        "url": "https://moz.com/blog/feed",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Ahrefs Blog",
        "url": "https://ahrefs.com/blog/feed/",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "SEMrush Blog",
        "url": "https://www.semrush.com/blog/feed/",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Backlinko",
        "url": "https://backlinko.com/feed",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Yoast SEO Blog",
        "url": "https://yoast.com/feed/",
        "lang": "en",
        "category": "SEO",
    },
    # ==============================
    # English — Google Official
    # ==============================
    {
        "name": "Google Search Central",
        "url": "https://developers.google.com/search/blog/feed.xml",
        "lang": "en",
        "category": "Google",
    },
    {
        "name": "Google Keyword Blog",
        "url": "https://blog.google/products/search/rss/",
        "lang": "en",
        "category": "Google",
    },
    {
        "name": "Chrome Developers",
        "url": "https://developer.chrome.com/blog/feed.xml",
        "lang": "en",
        "category": "Web Dev",
    },
    # ==============================
    # English — Content & Digital Marketing
    # ==============================
    {
        "name": "Content Marketing Institute",
        "url": "https://news.google.com/rss/search?q=site:contentmarketinginstitute.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Content",
    },
    {
        "name": "HubSpot Marketing Blog",
        "url": "https://blog.hubspot.com/marketing/rss.xml",
        "lang": "en",
        "category": "Marketing",
    },
    {
        "name": "Neil Patel Blog",
        "url": "https://neilpatel.com/blog/feed/",
        "lang": "en",
        "category": "SEO",
    },
    {
        "name": "Copyblogger",
        "url": "https://copyblogger.com/feed/",
        "lang": "en",
        "category": "Content",
    },
    {
        "name": "Search Engine Watch",
        "url": "https://www.searchenginewatch.com/feed/",
        "lang": "en",
        "category": "SEO",
    },
    # ==============================
    # English — PPC / SEM
    # ==============================
    {
        "name": "PPC Hero",
        "url": "https://www.ppchero.com/feed/",
        "lang": "en",
        "category": "PPC",
    },
    {
        "name": "WordStream Blog",
        "url": "https://www.wordstream.com/blog/feed",
        "lang": "en",
        "category": "PPC",
    },
    # ==============================
    # English — Web Analytics & Technical
    # ==============================
    {
        "name": "web.dev",
        "url": "https://web.dev/feed.xml",
        "lang": "en",
        "category": "Web Dev",
    },
    {
        "name": "Screaming Frog Blog",
        "url": "https://www.screamingfrog.co.uk/feed/",
        "lang": "en",
        "category": "Technical SEO",
    },
    {
        "name": "OnCrawl Blog",
        "url": "https://www.oncrawl.com/feed/",
        "lang": "en",
        "category": "Technical SEO",
    },
    {
        "name": "DeepCrawl / Lumar Blog",
        "url": "https://www.lumar.io/blog/feed/",
        "lang": "en",
        "category": "Technical SEO",
    },
    # ==============================
    # English — AI x SEO / GEO
    # ==============================
    {
        "name": "Google News - AI SEO",
        "url": "https://news.google.com/rss/search?q=%22AI+SEO%22+OR+%22generative+engine%22+OR+%22SGE%22+OR+%22AI+overview%22+OR+%22search+generative%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "AI x SEO",
    },
    # ==============================
    # English — Social & E-commerce
    # ==============================
    {
        "name": "Social Media Examiner",
        "url": "https://www.socialmediaexaminer.com/feed/",
        "lang": "en",
        "category": "Social",
    },
    {
        "name": "Practical Ecommerce",
        "url": "https://www.practicalecommerce.com/feed",
        "lang": "en",
        "category": "E-commerce",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - SEO",
        "url": "https://news.google.com/rss/search?q=SEO+OR+%22search+engine+optimization%22+OR+%22Google+algorithm%22+OR+%22core+update%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — SEO Media
    # ==============================
    {
        "name": "SEO Japan",
        "url": "https://www.seojapan.com/blog/feed",
        "lang": "ja",
        "category": "SEO",
    },
    {
        "name": "海外SEO情報ブログ",
        "url": "https://www.suzukikenichi.com/blog/feed/",
        "lang": "ja",
        "category": "SEO",
    },
    {
        "name": "SEOラボ",
        "url": "https://seolaboratory.jp/feed/",
        "lang": "ja",
        "category": "SEO",
    },
    {
        "name": "Web担当者Forum",
        "url": "https://news.google.com/rss/search?q=site:webtan.impress.co.jp+SEO&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Marketing",
    },
    {
        "name": "バズ部",
        "url": "https://bazubu.com/feed",
        "lang": "ja",
        "category": "Content",
    },
    {
        "name": "SEO HACKS",
        "url": "https://www.seohacks.net/blog/feed/",
        "lang": "ja",
        "category": "SEO",
    },
    {
        "name": "ナイルSEO相談室",
        "url": "https://www.seohacks.net/blog/feed/",
        "lang": "ja",
        "category": "SEO",
    },
    # ==============================
    # Japanese — Aggregators
    # ==============================
    {
        "name": "Google News - SEO (JP)",
        "url": "https://news.google.com/rss/search?q=SEO+OR+%E6%A4%9C%E7%B4%A2%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%B3+OR+Google%E3%82%A2%E3%83%AB%E3%82%B4%E3%83%AA%E3%82%BA%E3%83%A0+OR+%E3%82%B3%E3%82%A2%E3%82%A2%E3%83%83%E3%83%97%E3%83%87%E3%83%BC%E3%83%88&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

# SEO keywords for filtering general feeds
SEO_KEYWORDS = [
    r"\bSEO\b", r"\bSEM\b", r"\bPPC\b", r"\bSERP\b",
    r"\bsearch engine\b", r"\bGoogle algorithm\b", r"\bcore update\b",
    r"\bbacklink\b", r"\blink building\b", r"\bkeyword research\b",
    r"\borganic traffic\b", r"\bsearch ranking\b", r"\bpage rank\b",
    r"\btechnical SEO\b", r"\bon-page\b", r"\boff-page\b",
    r"\bcrawl", r"\bindex", r"\bsitemap\b", r"\brobots\.txt\b",
    r"\bschema markup\b", r"\bstructured data\b", r"\brich snippet\b",
    r"\bGoogle Search Console\b", r"\bGSC\b", r"\bGA4\b",
    r"\bGoogle Analytics\b", r"\bGoogle Ads\b",
    r"\bcontent marketing\b", r"\bconversion rate\b",
    r"\bSGE\b", r"\bAI overview\b", r"\bgenerative engine\b",
    r"\bE-E-A-T\b", r"\bEEAT\b", r"\bE-A-T\b",
    r"\bdomain authority\b", r"\bpage authority\b",
    r"\bAhrefs\b", r"\bSEMrush\b", r"\bMoz\b",
    # Japanese
    r"SEO", r"検索エンジン", r"検索順位", r"アルゴリズム",
    r"被リンク", r"内部リンク", r"キーワード",
    r"コアアップデート", r"インデックス",
    r"コンテンツマーケティング", r"コンバージョン",
    r"サーチコンソール", r"アナリティクス",
    r"オーガニック", r"リスティング広告",
]

_MEDIA_NAMES = [
    "日本経済新聞", "朝日新聞", "Yahoo!ニュース", "Reuters",
]

SEO_PATTERN = re.compile("|".join(SEO_KEYWORDS), re.IGNORECASE)
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)

USER_AGENT = "MyHub-SEOFetcher/1.0"
FETCH_TIMEOUT = 15

FILTER_SOURCES = {
    "Google News - SEO", "Google News - SEO (JP)", "Google News - AI SEO",
}


class SmartRedirectHandler(HTTPRedirectHandler):
    def http_error_308(self, req, fp, code, msg, headers):
        return self.http_error_302(req, fp, code, msg, headers)


_opener = build_opener(SmartRedirectHandler)


def fetch_url(url):
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


def is_seo_related(title, description="", source_name=""):
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    combined = f"{clean_title} {clean_desc}"
    return bool(SEO_PATTERN.search(combined))


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

    ns = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        if not link:
            link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext("{http://purl.org/dc/elements/1.1/}date", "")
        if not title or not link:
            continue
        if feed_config["name"] in FILTER_SOURCES and not is_seo_related(title, desc, feed_config["name"]):
            continue
        articles.append({
            "id": make_id(link), "title": title, "url": link,
            "description": desc[:300] if desc else "",
            "source": feed_config["name"], "lang": feed_config["lang"],
            "category": feed_config["category"], "published": parse_rss_date(pub_date),
        })

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
        if feed_config["name"] in FILTER_SOURCES and not is_seo_related(title, summary, feed_config["name"]):
            continue
        articles.append({
            "id": make_id(link), "title": title, "url": link,
            "description": summary[:300] if summary else "",
            "source": feed_config["name"], "lang": feed_config["lang"],
            "category": feed_config["category"], "published": parse_rss_date(updated),
        })

    print(f"    -> {len(articles)} articles")
    return articles


def deduplicate(articles):
    seen = set()
    unique = []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)
    return unique


def main():
    print("=== SEO News Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    all_articles = []
    for feed in RSS_FEEDS:
        all_articles.extend(fetch_rss_feed(feed))
    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = [a for a in all_articles if a.get("published", "") >= cutoff]
    all_articles = all_articles[:500]

    output = {"updated_at": datetime.now(timezone.utc).isoformat(), "total": len(all_articles), "articles": all_articles}
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "seo-news.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
