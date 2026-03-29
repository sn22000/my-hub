#!/usr/bin/env python3
"""
Game Hub News Fetcher
Fetches video game, esports, gaming industry, and game development news.
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
    # English — Major Gaming Media
    # ==============================
    {
        "name": "IGN",
        "url": "https://feeds.feedburner.com/ign/all",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Kotaku",
        "url": "https://kotaku.com/rss",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Polygon",
        "url": "https://www.polygon.com/rss/index.xml",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Eurogamer",
        "url": "https://www.eurogamer.net/feed",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "PC Gamer",
        "url": "https://www.pcgamer.com/rss/",
        "lang": "en",
        "category": "PC",
    },
    {
        "name": "Rock Paper Shotgun",
        "url": "https://www.rockpapershotgun.com/feed",
        "lang": "en",
        "category": "PC",
    },
    {
        "name": "Destructoid",
        "url": "https://www.destructoid.com/feed/",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "VG247",
        "url": "https://www.vg247.com/feed",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "GameSpot",
        "url": "https://www.gamespot.com/feeds/news/",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Giant Bomb",
        "url": "https://www.giantbomb.com/feeds/news/",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # English — Industry & Business
    # ==============================
    {
        "name": "GamesIndustry.biz",
        "url": "https://www.gamesindustry.biz/feed",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Game Developer",
        "url": "https://www.gamedeveloper.com/rss.xml",
        "lang": "en",
        "category": "Development",
    },
    {
        "name": "Axios Gaming",
        "url": "https://news.google.com/rss/search?q=%22video+game%22+OR+gaming+OR+Xbox+OR+PlayStation+OR+Nintendo+site:axios.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Bloomberg Gaming",
        "url": "https://news.google.com/rss/search?q=gaming+OR+%22video+game%22+OR+esports+site:bloomberg.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "VentureBeat Gaming",
        "url": "https://news.google.com/rss/search?q=gaming+OR+%22video+game%22+site:venturebeat.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Industry",
    },
    # ==============================
    # English — Esports
    # ==============================
    {
        "name": "HLTV (CS2/Esports)",
        "url": "https://www.hltv.org/rss/news",
        "lang": "en",
        "category": "Esports",
    },
    {
        "name": "Esports News",
        "url": "https://news.google.com/rss/search?q=%22esports%22+%22game%22+OR+%22League+of+Legends%22+OR+%22Valorant%22+OR+%22Counter-Strike%22+OR+%22Dota%22+OR+%22Overwatch%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Esports",
    },
    {
        "name": "Dot Esports",
        "url": "https://dotesports.com/feed",
        "lang": "en",
        "category": "Esports",
    },
    {
        "name": "TheGamer",
        "url": "https://www.thegamer.com/feed/",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # English — Console & Platform
    # ==============================
    {
        "name": "Nintendo Life",
        "url": "https://www.nintendolife.com/feeds/latest",
        "lang": "en",
        "category": "Nintendo",
    },
    {
        "name": "Push Square (PlayStation)",
        "url": "https://www.pushsquare.com/feeds/latest",
        "lang": "en",
        "category": "PlayStation",
    },
    {
        "name": "Pure Xbox",
        "url": "https://www.purexbox.com/feeds/latest",
        "lang": "en",
        "category": "Xbox",
    },
    {
        "name": "Ars Technica Gaming",
        "url": "https://news.google.com/rss/search?q=gaming+OR+%22video+game%22+site:arstechnica.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "The Verge Gaming",
        "url": "https://news.google.com/rss/search?q=gaming+OR+%22video+game%22+OR+console+site:theverge.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # English — Mobile Gaming
    # ==============================
    {
        "name": "Pocket Gamer",
        "url": "https://www.pocketgamer.com/rss/",
        "lang": "en",
        "category": "Mobile",
    },
    {
        "name": "TouchArcade",
        "url": "https://toucharcade.com/feed/",
        "lang": "en",
        "category": "Mobile",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - Gaming",
        "url": "https://news.google.com/rss/search?q=%22video+game%22+OR+%22video+games%22+OR+%22gaming+industry%22+OR+PlayStation+OR+%22Xbox+Game%22+OR+%22Nintendo+Switch%22+OR+%22Steam+game%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Gaming Media
    # ==============================
    {
        "name": "4Gamer.net",
        "url": "https://news.google.com/rss/search?q=site:4gamer.net&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Famitsu",
        "url": "https://news.google.com/rss/search?q=site:famitsu.com+%E3%82%B2%E3%83%BC%E3%83%A0&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Game Watch (Impress)",
        "url": "https://news.google.com/rss/search?q=site:game.watch.impress.co.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Dengeki Online",
        "url": "https://news.google.com/rss/search?q=site:dengekionline.com+%E3%82%B2%E3%83%BC%E3%83%A0&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "Automaton",
        "url": "https://automaton-media.com/feed/",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "GameBusiness.jp",
        "url": "https://news.google.com/rss/search?q=site:gamebusiness.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "Inside Games",
        "url": "https://news.google.com/rss/search?q=site:inside-games.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "game*spark",
        "url": "https://news.google.com/rss/search?q=site:gamespark.jp&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
    # ==============================
    # Japanese — Aggregator
    # ==============================
    {
        "name": "Google News - ゲーム (JP)",
        "url": "https://news.google.com/rss/search?q=%E3%83%93%E3%83%87%E3%82%AA%E3%82%B2%E3%83%BC%E3%83%A0+OR+%E3%82%B2%E3%83%BC%E3%83%9F%E3%83%B3%E3%82%B0+OR+%E3%82%A8%E3%82%B9%E3%83%9D%E3%83%BC%E3%83%84+OR+%E3%83%8B%E3%83%B3%E3%83%86%E3%83%B3%E3%83%89%E3%83%BC%E3%82%B9%E3%82%A4%E3%83%83%E3%83%81+OR+%E3%83%97%E3%83%AC%E3%82%A4%E3%82%B9%E3%83%86%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

GAME_KEYWORDS = [
    # Video game specific — tight compound forms first
    r"\bvideo ?game", r"\bgaming\b", r"\bgamer\b", r"\bgameplay\b",
    r"\bplaythrough\b", r"\bgame dev\b", r"\bindiegame\b", r"\bindie game\b",
    # Platforms — specific enough to be safe
    r"\bPlayStation\b", r"\bPS5\b", r"\bPS4\b", r"\bXbox\b",
    r"\bNintendo Switch\b", r"\bNintendo Direct\b", r"\bGame Boy\b",
    r"\bSteam\b", r"\bGame Pass\b", r"\bPSN\b", r"\bEpic Games Store\b",
    r"\bPC game\b",
    # Companies — gaming-specific names only
    r"\bActivision\b", r"\bBlizzard\b", r"\bElectronic Arts\b", r"\bEA Sports\b",
    r"\bUbisoft\b", r"\bRoblox\b", r"\bEpic Games\b", r"\bValve\b",
    r"\bTake-Two\b", r"\bRockstar Games\b", r"\b2K Games\b",
    r"\bSquare Enix\b", r"\bCapcom\b", r"\bBandai Namco\b", r"\bFromSoftware\b",
    r"\bBethesda\b", r"\bCD Projekt\b", r"\bSega\b", r"\bKonami\b",
    r"\bMicrosoft Gaming\b",
    # Esports — specific titles and terms
    r"\besport", r"\bLeague of Legends\b", r"\bDota 2\b",
    r"\bCounter-Strike\b", r"\bCS2\b", r"\bCS:GO\b",
    r"\bValorant\b", r"\bFortnite\b", r"\bOverwatch\b", r"\bApex Legends\b",
    r"\bTwitch\b", r"\bYouTube Gaming\b",
    # Game content types
    r"\bDLC\b", r"\bexpansion pack\b", r"\bgame pass\b",
    r"\bopen world game\b", r"\bRPG game\b", r"\bMMO\b", r"\bMOBA\b",
    r"\bmobile game\b", r"\bgacha\b",
    # Japanese — safe, ゲーム is specific enough in context
    r"ゲーム", r"ゲーミング", r"任天堂", r"プレイステーション",
    r"エスポーツ", r"ゲーム開発", r"インディーゲーム",
    r"ニンテンドー", r"ファミコン",
]

# Hard-block real sports articles that slip through on broad terms
SPORT_BLOCK_KEYWORDS = [
    r"\bNFL\b", r"\bNBA\b", r"\bMLB\b", r"\bNHL\b", r"\bMLS\b",
    r"\bPremier League\b", r"\bLa Liga\b", r"\bBundesliga\b", r"\bSerie A\b",
    r"\bSuper Bowl\b", r"\bWorld Cup\b", r"\bOlympics\b", r"\bOlympic Games\b",
    r"\btouchdown\b", r"\bhome run\b", r"\bslam dunk\b",
    r"\bscored a goal\b", r"\bfinal score\b", r"\bgame winner\b",
    r"\bplayoff game\b", r"\bchampionship game\b",
    r"\btennis\b", r"\bgolf\b", r"\bboxing match\b", r"\bUFC\b",
    r"\bF1\b", r"\bFormula 1\b", r"\bFormula One\b",
]

_MEDIA_NAMES = [
    "日本経済新聞", "朝日新聞", "毎日新聞", "読売新聞",
    "Yahoo!ニュース", "NHK", "Reuters", "Bloomberg",
]
GAME_PATTERN = re.compile("|".join(GAME_KEYWORDS), re.IGNORECASE)
SPORT_BLOCK_PATTERN = re.compile("|".join(SPORT_BLOCK_KEYWORDS), re.IGNORECASE)
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)

USER_AGENT = "MyHub-GameFetcher/1.0"
FETCH_TIMEOUT = 15

FILTER_SOURCES = {
    "Google News - Gaming",
    "Google News - ゲーム (JP)",
    "Bloomberg Gaming",
    "Ars Technica Gaming",
    "The Verge Gaming",
    "Esports News",
    "Axios Gaming",
    # Apply filter to broad feeds that mix gaming with other content
    "IGN",
    "TheGamer",
    "VG247",
    "Destructoid",
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
    return re.sub(r"<[^>]+>", "", unescape(text)).strip()


def make_id(url):
    return hashlib.md5(url.encode()).hexdigest()[:10]


def is_game_related(title, description="", source_name=""):
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    combined = f"{clean_title} {clean_desc}"
    # Must match a gaming keyword
    if not GAME_PATTERN.search(combined):
        return False
    # If it matches a real-sports keyword but has NO strong gaming term, reject it
    if SPORT_BLOCK_PATTERN.search(combined):
        strong_game = re.search(
            r"video ?game|gaming|gamer|gameplay|PlayStation|Xbox|Nintendo|Steam|Roblox|esport|Twitch|"
            r"ゲーム|エスポーツ|任天堂|プレイステーション",
            combined, re.IGNORECASE
        )
        if not strong_game:
            return False
    return True


def parse_rss_date(date_str):
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    for fmt in [
        "%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d",
    ]:
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
    try:
        root = ET.fromstring(data)
    except ET.ParseError as e:
        print(f"  [WARN] Parse error for {feed_config['name']}: {e}", file=sys.stderr)
        return []

    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "dc": "http://purl.org/dc/elements/1.1/",
    }
    articles = []

    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        if not link:
            link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext(
            "{http://purl.org/dc/elements/1.1/}date", ""
        )
        if not title or not link:
            continue
        if feed_config["name"] in FILTER_SOURCES and not is_game_related(
            title, desc, feed_config["name"]
        ):
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
        link_el = entry.find("atom:link[@rel='alternate']", ns) or entry.find("atom:link", ns)
        link = link_el.get("href", "") if link_el is not None else ""
        summary = strip_html(
            entry.findtext("atom:summary", "", ns)
            or entry.findtext("atom:content", "", ns)
            or ""
        )
        updated = entry.findtext("atom:updated", "", ns) or entry.findtext(
            "atom:published", "", ns
        )
        if not title or not link:
            continue
        if feed_config["name"] in FILTER_SOURCES and not is_game_related(
            title, summary, feed_config["name"]
        ):
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
    seen, unique = set(), []
    for a in articles:
        if a["url"] not in seen:
            seen.add(a["url"])
            unique.append(a)
    return unique


def main():
    print("=== Game News Fetcher ===")
    print(f"Time: {datetime.now(timezone.utc).isoformat()}")
    all_articles = []
    for feed in RSS_FEEDS:
        all_articles.extend(fetch_rss_feed(feed))
    all_articles = deduplicate(all_articles)
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    all_articles = [a for a in all_articles if a.get("published", "") >= cutoff][:500]

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(all_articles),
        "articles": all_articles,
    }
    out_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "game-news.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
