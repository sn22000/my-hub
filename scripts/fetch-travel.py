#!/usr/bin/env python3
"""
Travel News Fetcher
Fetches travel, airline, hotel, destination, and tourism industry news.
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
    # English — Major Travel Media
    # ==============================
    {
        "name": "Condé Nast Traveler",
        "url": "https://www.cntraveler.com/feed/rss",
        "lang": "en",
        "category": "Destination",
    },
    {
        "name": "Travel + Leisure",
        "url": "https://news.google.com/rss/search?q=site:travelandleisure.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Destination",
    },
    {
        "name": "Lonely Planet",
        "url": "https://news.google.com/rss/search?q=site:lonelyplanet.com+travel+OR+destination&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Destination",
    },
    {
        "name": "Skift",
        "url": "https://skift.com/feed/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "The Points Guy",
        "url": "https://thepointsguy.com/feed/",
        "lang": "en",
        "category": "Points & Miles",
    },
    {
        "name": "One Mile at a Time",
        "url": "https://onemileatatime.com/feed/",
        "lang": "en",
        "category": "Points & Miles",
    },
    {
        "name": "Tnooz / Phocuswire",
        "url": "https://news.google.com/rss/search?q=site:phocuswire.com+travel+technology&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Traveller AU",
        "url": "https://www.traveller.com.au/rss.xml",
        "lang": "en",
        "category": "Destination",
    },
    # ==============================
    # English — Airlines & Aviation
    # ==============================
    {
        "name": "Simple Flying",
        "url": "https://simpleflying.com/feed/",
        "lang": "en",
        "category": "Aviation",
    },
    {
        "name": "View from the Wing",
        "url": "https://viewfromthewing.com/feed/",
        "lang": "en",
        "category": "Aviation",
    },
    {
        "name": "Aviation Week",
        "url": "https://aviationweek.com/rss.xml",
        "lang": "en",
        "category": "Aviation",
    },
    {
        "name": "Paddle Your Own Kanoo",
        "url": "https://www.paddleyourownkanoo.com/feed/",
        "lang": "en",
        "category": "Aviation",
    },
    {
        "name": "Reuters Airlines",
        "url": "https://news.google.com/rss/search?q=airline+OR+aviation+OR+airport+site:reuters.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Aviation",
    },
    # ==============================
    # English — Hotels & Hospitality
    # ==============================
    {
        "name": "Hotel Dive",
        "url": "https://www.hoteldive.com/feeds/news/",
        "lang": "en",
        "category": "Hotels",
    },
    {
        "name": "Hospitality Net",
        "url": "https://www.hospitalitynet.org/rss/news.xml",
        "lang": "en",
        "category": "Hotels",
    },
    {
        "name": "Hotel Management",
        "url": "https://www.hotelmanagement.net/rss/xml",
        "lang": "en",
        "category": "Hotels",
    },
    # ==============================
    # English — Adventure & Outdoor
    # ==============================
    {
        "name": "Fodors Travel",
        "url": "https://www.fodors.com/feed/",
        "lang": "en",
        "category": "Destination",
    },
    {
        "name": "Atlas Obscura",
        "url": "https://www.atlasobscura.com/feeds/latest",
        "lang": "en",
        "category": "Destination",
    },
    {
        "name": "Nomadic Matt",
        "url": "https://www.nomadicmatt.com/feed/",
        "lang": "en",
        "category": "Budget",
    },
    # ==============================
    # English — Digital Nomad & Remote
    # ==============================
    {
        "name": "Matador Network",
        "url": "https://matadornetwork.com/feed/",
        "lang": "en",
        "category": "Destination",
    },
    # ==============================
    # English — Deals & Tips
    # ==============================
    {
        "name": "Secret Flying",
        "url": "https://www.secretflying.com/feed/",
        "lang": "en",
        "category": "Deals",
    },
    {
        "name": "Upgraded Points",
        "url": "https://upgradedpoints.com/feed/",
        "lang": "en",
        "category": "Points & Miles",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - Travel",
        "url": "https://news.google.com/rss/search?q=travel+OR+airline+OR+hotel+OR+tourism+OR+%22flight+deal%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "BBC News Travel",
        "url": "https://news.google.com/rss/search?q=site:bbc.com+travel+OR+airline+OR+tourism&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Travel Media
    # ==============================
    {
        "name": "トラベルWatch",
        "url": "https://news.google.com/rss/search?q=site:travel.watch.impress.co.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "トラベルボイス",
        "url": "https://www.travelvoice.jp/feed",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "Traicy",
        "url": "https://www.traicy.com/feed",
        "lang": "ja",
        "category": "Aviation",
    },
    {
        "name": "TABIPPO",
        "url": "https://tabippo.net/feed/",
        "lang": "ja",
        "category": "Destination",
    },
    {
        "name": "LCC News",
        "url": "https://news.google.com/rss/search?q=LCC+OR+%E6%A0%BC%E5%AE%89%E8%88%AA%E7%A9%BA+OR+%E3%83%94%E3%83%BC%E3%83%81+OR+%E3%82%B8%E3%82%A7%E3%83%83%E3%83%88%E3%82%B9%E3%82%BF%E3%83%BC&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Aviation",
    },
    {
        "name": "じゃらんニュース",
        "url": "https://www.jalan.net/news/feed/",
        "lang": "ja",
        "category": "Destination",
    },
    {
        "name": "ANA Travel",
        "url": "https://news.google.com/rss/search?q=ANA+%E8%88%AA%E7%A9%BA+OR+%E5%85%A8%E6%97%A5%E7%A9%BA&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Aviation",
    },
    {
        "name": "観光経済新聞",
        "url": "https://www.kankokeizai.com/feed/",
        "lang": "ja",
        "category": "Industry",
    },
    # ==============================
    # Japanese — Aggregators
    # ==============================
    {
        "name": "Google News - 旅行 (JP)",
        "url": "https://news.google.com/rss/search?q=%E6%97%85%E8%A1%8C+OR+%E8%88%AA%E7%A9%BA+OR+%E3%83%9B%E3%83%86%E3%83%AB+OR+%E8%A6%B3%E5%85%89+OR+%E3%82%A4%E3%83%B3%E3%83%90%E3%82%A6%E3%83%B3%E3%83%89&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

# Travel keywords for filtering general feeds
TRAVEL_KEYWORDS = [
    r"\btravel\b", r"\btouris", r"\bairline\b", r"\baviation\b",
    r"\bflight\b", r"\bairport\b", r"\bhotel\b", r"\bhospitality\b",
    r"\bdestination\b", r"\bvacation\b", r"\bholiday\b",
    r"\bbooking\b", r"\bAirbnb\b", r"\bMarriott\b", r"\bHilton\b",
    r"\bcruise\b", r"\bbackpack", r"\bnomad\b", r"\bvisa\b",
    r"\bpassport\b", r"\bresort\b", r"\bexpat\b", r"\bimmigra",
    r"\bJetBlue\b", r"\bDelta\b", r"\bUnited\b", r"\bAmerican Airlines\b",
    r"\bRyanair\b", r"\beasyJet\b", r"\bEmirares\b", r"\bANA\b", r"\bJAL\b",
    r"\bLufthansa\b", r"\bBoeing\b", r"\bAirbus\b",
    r"\bTSA\b", r"\blounge\b", r"\bbusiness class\b", r"\bfirst class\b",
    # Japanese
    r"旅行", r"旅", r"航空", r"空港", r"ホテル", r"観光",
    r"インバウンド", r"フライト", r"ツアー", r"民泊",
    r"LCC", r"格安航空", r"マイル", r"ラウンジ",
    r"ビザ", r"パスポート", r"クルーズ", r"リゾート",
    r"バックパック", r"ノマド", r"温泉", r"宿泊",
]

_MEDIA_NAMES = [
    "日本経済新聞", "朝日新聞", "読売新聞", "毎日新聞", "産経新聞",
    "NHK", "Yahoo!ニュース", "Reuters", "Bloomberg",
]

TRAVEL_PATTERN = re.compile("|".join(TRAVEL_KEYWORDS), re.IGNORECASE)
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)

USER_AGENT = "MyHub-TravelFetcher/1.0"
FETCH_TIMEOUT = 15

# Sources needing keyword filter
FILTER_SOURCES = {
    "Google News - Travel", "Google News - 旅行 (JP)",
    "BBC News Travel", "LCC News", "ANA Travel",
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


def is_travel_related(title, description="", source_name=""):
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    combined = f"{clean_title} {clean_desc}"
    return bool(TRAVEL_PATTERN.search(combined))


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
    }

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        if not link:
            link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext("{http://purl.org/dc/elements/1.1/}date", "")

        if not title or not link:
            continue
        if feed_config["name"] in FILTER_SOURCES and not is_travel_related(title, desc, feed_config["name"]):
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
        if feed_config["name"] in FILTER_SOURCES and not is_travel_related(title, summary, feed_config["name"]):
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
    print("=== Travel News Fetcher ===")
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
    out_path = os.path.join(out_dir, "travel-news.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
