#!/usr/bin/env python3
"""
Economics News Fetcher
Fetches macroeconomics, policy, trade, labor, and central bank news,
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
    # English — Economics Media
    # ==============================
    {
        "name": "The Economist",
        "url": "https://www.economist.com/finance-and-economics/rss.xml",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "The Economist World",
        "url": "https://www.economist.com/the-world-this-week/rss.xml",
        "lang": "en",
        "category": "Global",
    },
    {
        "name": "FT Economy",
        "url": "https://www.ft.com/global-economy?format=rss",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "FT Trade",
        "url": "https://www.ft.com/trade?format=rss",
        "lang": "en",
        "category": "Trade",
    },
    {
        "name": "Bloomberg Economics",
        "url": "https://feeds.bloomberg.com/economics/news.rss",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "Reuters Economy",
        "url": "https://news.google.com/rss/search?q=site:reuters.com+economy+OR+GDP+OR+inflation+OR+%22central+bank%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "CNBC Economy",
        "url": "https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "NPR Economy",
        "url": "https://feeds.npr.org/1017/rss.xml",
        "lang": "en",
        "category": "Macro",
    },
    {
        "name": "WSJ Economy",
        "url": "https://feeds.content.dowjones.io/public/rss/WSJcomUSBusiness",
        "lang": "en",
        "category": "Macro",
    },
    # ==============================
    # English — Central Banks & Policy
    # ==============================
    {
        "name": "Federal Reserve",
        "url": "https://www.federalreserve.gov/feeds/press_all.xml",
        "lang": "en",
        "category": "Central Bank",
    },
    {
        "name": "ECB Press",
        "url": "https://www.ecb.europa.eu/rss/press.html",
        "lang": "en",
        "category": "Central Bank",
    },
    {
        "name": "Bank of England",
        "url": "https://www.bankofengland.co.uk/rss/news",
        "lang": "en",
        "category": "Central Bank",
    },
    {
        "name": "IMF Blog",
        "url": "https://www.imf.org/en/Blogs/rss",
        "lang": "en",
        "category": "Policy",
    },
    {
        "name": "World Bank",
        "url": "https://news.google.com/rss/search?q=site:worldbank.org+economy+OR+development&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Policy",
    },
    {
        "name": "BIS Speeches",
        "url": "https://www.bis.org/doclist/cbspeeches.rss",
        "lang": "en",
        "category": "Central Bank",
    },
    {
        "name": "Axios Macro",
        "url": "https://api.axios.com/feed/",
        "lang": "en",
        "category": "General",
    },
    {
        "name": "Business Insider Econ",
        "url": "https://markets.businessinsider.com/rss/news",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # English — Academic / Research
    # ==============================
    {
        "name": "Bruegel Blog",
        "url": "https://www.bruegel.org/rss.xml",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "NBER New Papers",
        "url": "https://www.nber.org/rss/new.xml",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Fed Reserve Research",
        "url": "https://www.federalreserve.gov/feeds/feds_notes.xml",
        "lang": "en",
        "category": "Research",
    },
    {
        "name": "Project Syndicate Econ",
        "url": "https://www.project-syndicate.org/rss/section/economics",
        "lang": "en",
        "category": "Opinion",
    },
    {
        "name": "Naked Capitalism",
        "url": "https://www.nakedcapitalism.com/feed",
        "lang": "en",
        "category": "Opinion",
    },
    {
        "name": "Marginal Revolution",
        "url": "https://marginalrevolution.com/feed",
        "lang": "en",
        "category": "Opinion",
    },
    # ==============================
    # English — Trade & Geopolitics
    # ==============================
    {
        "name": "Google News - Trade",
        "url": "https://news.google.com/rss/search?q=trade+war+OR+tariff+OR+WTO+OR+global+trade&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Trade",
    },
    {
        "name": "Google News - Economy",
        "url": "https://news.google.com/rss/search?q=economy+OR+GDP+OR+inflation+OR+%22interest+rate%22+OR+trade+war+OR+tariff&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Economics Media
    # ==============================
    {
        "name": "日経 経済",
        "url": "https://assets.wor.jp/rss/rdf/nikkei/economy.rdf",
        "lang": "ja",
        "category": "Macro",
    },
    {
        "name": "日経 国際",
        "url": "https://news.google.com/rss/search?q=site:nikkei.com+%E7%B5%8C%E6%B8%88+OR+%E9%87%91%E5%88%A9+OR+%E7%89%A9%E4%BE%A1+OR+GDP+OR+%E8%B2%BF%E6%98%93+OR+%E7%82%BA%E6%9B%BF+OR+%E6%97%A5%E9%8A%80+OR+%E5%8E%9F%E6%B2%B9&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Global",
    },
    {
        "name": "ロイター 経済",
        "url": "https://news.google.com/rss/search?q=site:jp.reuters.com+%E7%B5%8C%E6%B8%88+OR+%E9%87%91%E5%88%A9+OR+GDP+OR+%E6%97%A5%E9%8A%80&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Macro",
    },
    {
        "name": "現代ビジネス",
        "url": "https://gendai.media/list/feed/rss",
        "lang": "ja",
        "category": "General",
    },
    {
        "name": "NHK ビジネス",
        "url": "https://www.nhk.or.jp/rss/news/cat5.xml",
        "lang": "ja",
        "category": "Macro",
    },
    {
        "name": "日銀 公表資料",
        "url": "https://www.boj.or.jp/rss/whatsnew.xml",
        "lang": "ja",
        "category": "Central Bank",
    },
    {
        "name": "Google News - 貿易 (JP)",
        "url": "https://news.google.com/rss/search?q=%E8%B2%BF%E6%98%93+OR+%E9%96%A2%E7%A8%8E+OR+%E8%BC%B8%E5%87%BA+OR+%E8%BC%B8%E5%85%A5+OR+WTO+OR+%E9%80%9A%E5%95%86&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Trade",
    },
    {
        "name": "ZUU Online",
        "url": "https://zuuonline.com/feed",
        "lang": "ja",
        "category": "Macro",
    },
    {
        "name": "ITmedia ビジネス",
        "url": "https://rss.itmedia.co.jp/rss/2.0/business.xml",
        "lang": "ja",
        "category": "General",
    },
    # ==============================
    # Japanese — Aggregator
    # ==============================
    {
        "name": "Google News - 経済 (JP)",
        "url": "https://news.google.com/rss/search?q=%22%E6%97%A5%E6%9C%AC%E7%B5%8C%E6%B8%88%22+OR+%22%E9%87%91%E8%9E%8D%E6%94%BF%E7%AD%96%22+OR+%22%E5%88%A9%E4%B8%8A%E3%81%92%22+OR+%22%E5%88%A9%E4%B8%8B%E3%81%92%22+OR+%22%E6%B6%88%E8%B2%BB%E8%80%85%E7%89%A9%E4%BE%A1%22+OR+%22%E5%AE%9F%E8%B3%AAGDP%22+OR+%22%E6%99%AF%E6%B0%97%E5%8B%95%E5%90%91%22&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

# Economics keywords for filtering general feeds
ECON_KEYWORDS = [
    r"\beconom", r"\bGDP\b", r"\binflation\b", r"\bdeflation\b",
    r"\brecession\b", r"\binterest rate\b", r"\bcentral bank\b",
    r"\bmonetary policy\b", r"\bfiscal policy\b", r"\btariff\b",
    r"\btrade war\b", r"\btrade deficit\b", r"\bsupply chain\b",
    r"\bunemployment\b", r"\bjob market\b", r"\blabor market\b",
    r"\bwage\b", r"\bconsumer price\b", r"\bCPI\b", r"\bPPI\b",
    r"\bFed\b", r"\bECB\b", r"\bBoJ\b", r"\bIMF\b", r"\bWorld Bank\b",
    r"\bOECD\b", r"\bWTO\b", r"\bsanction", r"\bgeopolit",
    r"\bglobal trade\b", r"\bsovereign debt\b", r"\bauster",
    r"\bstimulus\b", r"\bquantitative easing\b", r"\bQE\b",
    r"\bdebt\b", r"\bdeficit\b", r"\bbond\b", r"\btreasur",
    r"\benergy price\b", r"\boil price\b", r"\bcrude\b",
    r"\bhousing market\b", r"\breal estate market\b",
    r"\bgrowth\b", r"\bcontraction\b", r"\bdownturn\b",
    # Japanese
    r"経済", r"GDP", r"インフレ", r"デフレ", r"景気",
    r"金利", r"金融政策", r"財政", r"関税", r"貿易",
    r"雇用", r"失業", r"物価", r"日銀", r"中央銀行",
    r"為替", r"円安", r"円高", r"サプライチェーン",
    r"制裁", r"地政学", r"賃金", r"消費者物価",
    r"原油", r"エネルギー", r"国債", r"利上げ", r"利下げ",
    r"マクロ", r"成長率", r"不況", r"株価", r"金融市場", r"株式市場",
]

# Sources that need keyword filtering (broad feeds with mixed content)
FILTER_SOURCES = {
    "東洋経済オンライン", "現代ビジネス", "ZUU Online", "ITmedia ビジネス",
    "日経 国際", "WSJ Economy", "Marginal Revolution", "Naked Capitalism",
    "Axios Macro", "Business Insider Econ", "JETRO 通商弘報",
    "Google News - 経済 (JP)", "Google News - Economy",
}

ECON_PATTERN = re.compile("|".join(ECON_KEYWORDS), re.IGNORECASE)

USER_AGENT = "MyHub-EconFetcher/1.0"
FETCH_TIMEOUT = 15


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


# Media names that appear in Google News titles/descriptions causing false keyword matches
_MEDIA_NAMES = [
    "日本経済新聞", "東洋経済オンライン", "現代ビジネス", "ダイヤモンド・オンライン",
    "Reuters", "Bloomberg", "CNBC", "Financial Times", "The Economist",
    "Yahoo!ニュース", "朝日新聞", "読売新聞", "毎日新聞", "産経新聞", "NHK",
    "外為どっとコム", "ZUU online", "ニューズウィーク日本版",
]
# Remove "- SourceName" or standalone "SourceName" at end of text
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)


def is_econ_related(title, description="", source_name=""):
    # Strip trailing "- SourceName" from both title and description (Google News adds these)
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    combined = f"{clean_title} {clean_desc}"
    return bool(ECON_PATTERN.search(combined))


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

    # RSS 2.0 / RDF
    for item in root.findall(".//item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        if not link:
            link = item.get("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")
        desc = strip_html(item.findtext("description", ""))
        pub_date = item.findtext("pubDate", "") or item.findtext("{http://purl.org/dc/elements/1.1/}date", "")

        if not title or not link:
            continue
        if feed_config["name"] in FILTER_SOURCES and not is_econ_related(title, desc, feed_config["name"]):
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
        if feed_config["category"] == "General" and not is_econ_related(title, summary):
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
    print("=== Economics News Fetcher ===")
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
    out_path = os.path.join(out_dir, "economics-news.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
