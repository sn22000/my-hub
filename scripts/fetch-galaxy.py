#!/usr/bin/env python3
"""
Galaxy News Fetcher
Fetches space, astronomy, rockets, satellites, and space industry news.
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

RSS_FEEDS = [
    # ==============================
    # English — Space News & Media
    # ==============================
    {
        "name": "Space.com",
        "url": "https://www.space.com/feeds/all",
        "lang": "en",
        "category": "Space",
    },
    {
        "name": "SpaceNews",
        "url": "https://spacenews.com/feed/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Ars Technica Space",
        "url": "https://feeds.arstechnica.com/arstechnica/science",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "The Verge Space",
        "url": "https://www.theverge.com/rss/science/index.xml",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Spaceflight Now",
        "url": "https://spaceflightnow.com/feed/",
        "lang": "en",
        "category": "Launch",
    },
    {
        "name": "NASASpaceflight",
        "url": "https://www.nasaspaceflight.com/feed/",
        "lang": "en",
        "category": "Launch",
    },
    {
        "name": "Planetary Society",
        "url": "https://www.planetary.org/the-downlink/rss",
        "lang": "en",
        "category": "Exploration",
    },
    {
        "name": "Universe Today",
        "url": "https://www.universetoday.com/feed/",
        "lang": "en",
        "category": "Astronomy",
    },
    # ==============================
    # English — NASA & Agencies
    # ==============================
    {
        "name": "NASA Breaking News",
        "url": "https://www.nasa.gov/news-release/feed/",
        "lang": "en",
        "category": "NASA",
    },
    {
        "name": "NASA Image of the Day",
        "url": "https://www.nasa.gov/rss/dyn/lg_image_of_the_day.rss",
        "lang": "en",
        "category": "NASA",
    },
    {
        "name": "ESA News",
        "url": "https://www.esa.int/rssfeed/Our_Activities/Space_Science",
        "lang": "en",
        "category": "Agency",
    },
    {
        "name": "ESA Exploration",
        "url": "https://www.esa.int/rssfeed/Our_Activities/Human_and_Robotic_Exploration",
        "lang": "en",
        "category": "Exploration",
    },
    # ==============================
    # English — Astronomy & Science
    # ==============================
    {
        "name": "Astronomy Magazine",
        "url": "https://www.astronomy.com/feed/",
        "lang": "en",
        "category": "Astronomy",
    },
    {
        "name": "Sky & Telescope",
        "url": "https://skyandtelescope.org/feed/",
        "lang": "en",
        "category": "Astronomy",
    },
    {
        "name": "Phys.org Space",
        "url": "https://phys.org/rss-feed/space-news/",
        "lang": "en",
        "category": "Science",
    },
    {
        "name": "Science Daily Space",
        "url": "https://www.sciencedaily.com/rss/space_time.xml",
        "lang": "en",
        "category": "Science",
    },
    {
        "name": "New Scientist Space",
        "url": "https://www.newscientist.com/subject/space/feed/",
        "lang": "en",
        "category": "Science",
    },
    {
        "name": "arXiv astro-ph",
        "url": "https://rss.arxiv.org/rss/astro-ph",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Webb / Hubble News",
        "url": "https://news.google.com/rss/search?q=%22James+Webb%22+OR+%22JWST%22+OR+%22Hubble+telescope%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Astronomy",
    },
    # ==============================
    # English — Space Industry & Commercial
    # ==============================
    {
        "name": "SpaceX News",
        "url": "https://news.google.com/rss/search?q=SpaceX+OR+Starship+OR+Falcon&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Payload Space",
        "url": "https://payloadspace.com/feed/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Via Satellite",
        "url": "https://www.satellitetoday.com/feed/",
        "lang": "en",
        "category": "Satellite",
    },
    {
        "name": "SpaceRef",
        "url": "https://spaceref.com/feed/",
        "lang": "en",
        "category": "Space",
    },
    {
        "name": "Teslarati Space",
        "url": "https://www.teslarati.com/category/spacex/feed/",
        "lang": "en",
        "category": "Launch",
    },
    # ==============================
    # English — Defense & Military Space
    # ==============================
    {
        "name": "SpacePolicyOnline",
        "url": "https://spacepolicyonline.com/feed/",
        "lang": "en",
        "category": "Policy",
    },
    {
        "name": "Breaking Defense Space",
        "url": "https://breakingdefense.com/tag/space/feed/",
        "lang": "en",
        "category": "Defense",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - Space",
        "url": "https://news.google.com/rss/search?q=space+exploration+OR+NASA+OR+rocket+launch+OR+Mars+OR+moon+mission&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Space Media
    # ==============================
    {
        "name": "sorae 宇宙へのポータル",
        "url": "https://sorae.info/feed",
        "lang": "ja",
        "category": "Space",
    },
    {
        "name": "マイナビ 宇宙",
        "url": "https://news.google.com/rss/search?q=site:news.mynavi.jp+%E5%AE%87%E5%AE%99+OR+%E3%83%AD%E3%82%B1%E3%83%83%E3%83%88+OR+%E8%A1%9B%E6%98%9F&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Space",
    },
    {
        "name": "AstroArts",
        "url": "https://news.google.com/rss/search?q=site:astroarts.co.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Astronomy",
    },
    {
        "name": "JAXA プレスリリース",
        "url": "https://www.jaxa.jp/rss/press_j.rdf",
        "lang": "ja",
        "category": "Agency",
    },
    {
        "name": "UchuBiz",
        "url": "https://uchubiz.com/feed/",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "月探査情報ステーション",
        "url": "https://moonstation.jp/feed",
        "lang": "ja",
        "category": "Exploration",
    },
    # ==============================
    # Japanese — Aggregator
    # ==============================
    {
        "name": "Google News - 宇宙 (JP)",
        "url": "https://news.google.com/rss/search?q=%E5%AE%87%E5%AE%99+OR+%E3%83%AD%E3%82%B1%E3%83%83%E3%83%88+OR+NASA+OR+JAXA+OR+%E5%A4%A9%E6%96%87&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

SPACE_KEYWORDS = [
    r"\bspace\b", r"\bNASA\b", r"\bESA\b", r"\bJAXA\b", r"\bSpaceX\b",
    r"\brocket\b", r"\blaunch\b", r"\borbit\b", r"\bsatellite\b",
    r"\bastronom", r"\btelescope\b", r"\bgalaxy\b", r"\bplanet\b",
    r"\bmoon\b", r"\bMars\b", r"\bJupiter\b", r"\bSaturn\b",
    r"\bastronaut\b", r"\bcosmonaut\b", r"\bISS\b",
    r"\bStarship\b", r"\bFalcon\b", r"\bStarlink\b",
    r"\bBlue Origin\b", r"\bBoeing Starliner\b", r"\bArtemis\b",
    r"\bexoplanet\b", r"\bnebula\b", r"\bblack hole\b",
    r"\bJames Webb\b", r"\bHubble\b", r"\bcosm",
    r"\basteroid\b", r"\bcomet\b", r"\bmeteor",
    # Japanese
    r"宇宙", r"ロケット", r"打ち上げ", r"衛星", r"天文",
    r"銀河", r"惑星", r"火星", r"月面", r"探査",
    r"宇宙飛行士", r"国際宇宙ステーション",
]

_MEDIA_NAMES = ["日本経済新聞", "朝日新聞", "Yahoo!ニュース", "NHK", "Reuters"]
SPACE_PATTERN = re.compile("|".join(SPACE_KEYWORDS), re.IGNORECASE)
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)

USER_AGENT = "MyHub-GalaxyFetcher/1.0"
FETCH_TIMEOUT = 15

FILTER_SOURCES = {
    "Google News - Space", "Google News - 宇宙 (JP)",
    "Ars Technica Space", "The Verge Space", "SpaceX News",
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
    if not text: return ""
    return re.sub(r"<[^>]+>", "", unescape(text)).strip()

def make_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:10]

def is_space_related(title, description="", source_name=""):
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    return bool(SPACE_PATTERN.search(f"{clean_title} {clean_desc}"))

def parse_rss_date(date_str):
    if not date_str: return datetime.now(timezone.utc).isoformat()
    for fmt in ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
                "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]:
        try:
            dt = datetime.strptime(date_str.strip(), fmt)
            if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
            return dt.isoformat()
        except ValueError: continue
    return datetime.now(timezone.utc).isoformat()

def fetch_rss_feed(feed_config):
    print(f"  Fetching: {feed_config['name']}...")
    data = fetch_url(feed_config["url"])
    if not data: return []
    try: root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"  [WARN] Parse error for {feed_config['name']}: {e}", file=sys.stderr)
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        if not link: link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext("{http://purl.org/dc/elements/1.1/}date", "")
        if not title or not link: continue
        if feed_config["name"] in FILTER_SOURCES and not is_space_related(title, desc, feed_config["name"]): continue
        articles.append({"id": make_id(link), "title": title, "url": link, "description": desc[:300] if desc else "",
            "source": feed_config["name"], "lang": feed_config["lang"], "category": feed_config["category"], "published": parse_rss_date(pub_date)})

    for entry in root.findall("atom:entry", ns):
        title = (entry.findtext("atom:title", "", ns) or "").strip()
        link_el = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = strip_html(entry.findtext("atom:summary", "", ns) or entry.findtext("atom:content", "", ns) or "")
        updated = entry.findtext("atom:updated", "", ns) or entry.findtext("atom:published", "", ns)
        if not title or not link: continue
        if feed_config["name"] in FILTER_SOURCES and not is_space_related(title, summary, feed_config["name"]): continue
        articles.append({"id": make_id(link), "title": title, "url": link, "description": summary[:300] if summary else "",
            "source": feed_config["name"], "lang": feed_config["lang"], "category": feed_config["category"], "published": parse_rss_date(updated)})

    print(f"    -> {len(articles)} articles")
    return articles

def deduplicate(articles):
    seen, unique = set(), []
    for a in articles:
        if a["url"] not in seen: seen.add(a["url"]); unique.append(a)
    return unique

def main():
    print("=== Galaxy News Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    all_articles = []
    for feed in RSS_FEEDS:
        all_articles.extend(fetch_rss_feed(feed))
    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = [a for a in all_articles if a.get("published", "") >= cutoff][:500]

    output = {"updated_at": datetime.now(timezone.utc).isoformat(), "total": len(all_articles), "articles": all_articles}
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "galaxy-news.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")

if __name__ == "__main__":
    main()
