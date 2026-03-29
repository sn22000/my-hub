#!/usr/bin/env python3
"""
Industry Hub News Fetcher
Fetches manufacturing, energy, supply chain, conglomerates, and industrial news.
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
    # English — Manufacturing & Industry
    # ==============================
    {
        "name": "IndustryWeek",
        "url": "https://www.industryweek.com/rss",
        "lang": "en",
        "category": "Manufacturing",
    },
    {
        "name": "Manufacturing Dive",
        "url": "https://www.manufacturingdive.com/feeds/news/",
        "lang": "en",
        "category": "Manufacturing",
    },
    {
        "name": "Industry Dive",
        "url": "https://www.industrydive.com/news/rss/",
        "lang": "en",
        "category": "Industry",
    },
    {
        "name": "Supply Chain Dive",
        "url": "https://www.supplychaindive.com/feeds/news/",
        "lang": "en",
        "category": "Logistics",
    },
    {
        "name": "Automation World",
        "url": "https://www.automationworld.com/rss.xml",
        "lang": "en",
        "category": "Manufacturing",
    },
    {
        "name": "Engineering.com",
        "url": "https://www.engineering.com/rss.axd",
        "lang": "en",
        "category": "Engineering",
    },
    {
        "name": "Plant Engineering",
        "url": "https://www.plantengineering.com/rss/all",
        "lang": "en",
        "category": "Manufacturing",
    },
    # ==============================
    # English — Business & Finance (Industry focus)
    # ==============================
    {
        "name": "Reuters Business",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "lang": "en",
        "category": "Business",
    },
    {
        "name": "Bloomberg Industry",
        "url": "https://news.google.com/rss/search?q=manufacturing+OR+%22supply+chain%22+OR+industrial+site:bloomberg.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Business",
    },
    {
        "name": "WSJ Business",
        "url": "https://feeds.a.dj.com/rss/WSJcomUSBusiness.xml",
        "lang": "en",
        "category": "Business",
    },
    {
        "name": "Financial Times Industry",
        "url": "https://news.google.com/rss/search?q=manufacturing+OR+industrial+OR+%22supply+chain%22+site:ft.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Business",
    },
    {
        "name": "Harvard Business Review",
        "url": "http://feeds.hbr.org/harvardbusiness",
        "lang": "en",
        "category": "Strategy",
    },
    {
        "name": "MIT Sloan Management",
        "url": "https://sloanreview.mit.edu/feed/",
        "lang": "en",
        "category": "Strategy",
    },
    # ==============================
    # English — Energy & Materials
    # ==============================
    {
        "name": "OilPrice.com",
        "url": "https://oilprice.com/rss/main",
        "lang": "en",
        "category": "Energy",
    },
    {
        "name": "Reuters Energy",
        "url": "https://feeds.reuters.com/reuters/energy",
        "lang": "en",
        "category": "Energy",
    },
    {
        "name": "S&P Global Commodity",
        "url": "https://news.google.com/rss/search?q=commodities+OR+energy+OR+steel+OR+metals+site:spglobal.com&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "Materials",
    },
    {
        "name": "Mining.com",
        "url": "https://www.mining.com/feed/",
        "lang": "en",
        "category": "Materials",
    },
    {
        "name": "Chemical & Engineering News",
        "url": "https://cen.acs.org/rss/latest.xml",
        "lang": "en",
        "category": "Materials",
    },
    # ==============================
    # English — Logistics & Supply Chain
    # ==============================
    {
        "name": "FreightWaves",
        "url": "https://www.freightwaves.com/news/feed",
        "lang": "en",
        "category": "Logistics",
    },
    {
        "name": "DC Velocity",
        "url": "https://www.dcvelocity.com/rss/articles/",
        "lang": "en",
        "category": "Logistics",
    },
    {
        "name": "Logistics Management",
        "url": "https://www.logisticsmgmt.com/rss/news",
        "lang": "en",
        "category": "Logistics",
    },
    # ==============================
    # English — Defense & Aerospace
    # ==============================
    {
        "name": "Defense News",
        "url": "https://www.defensenews.com/rss/",
        "lang": "en",
        "category": "Defense",
    },
    {
        "name": "Breaking Defense",
        "url": "https://breakingdefense.com/feed/",
        "lang": "en",
        "category": "Defense",
    },
    {
        "name": "Aviation Week",
        "url": "https://aviationweek.com/rss.xml",
        "lang": "en",
        "category": "Aerospace",
    },
    # ==============================
    # English — Tech & Automation
    # ==============================
    {
        "name": "Control Engineering",
        "url": "https://www.controleng.com/rss/",
        "lang": "en",
        "category": "Automation",
    },
    {
        "name": "IEEE Spectrum",
        "url": "https://spectrum.ieee.org/feeds/feed.rss",
        "lang": "en",
        "category": "Engineering",
    },
    {
        "name": "MIT Technology Review",
        "url": "https://www.technologyreview.com/feed/",
        "lang": "en",
        "category": "Technology",
    },
    # ==============================
    # English — Aggregators
    # ==============================
    {
        "name": "Google News - Industry",
        "url": "https://news.google.com/rss/search?q=manufacturing+OR+%22supply+chain%22+OR+industrial+OR+conglomerate+OR+Caterpillar+OR+Honeywell+OR+%22General+Electric%22&hl=en-US&gl=US&ceid=US:en",
        "lang": "en",
        "category": "General",
    },
    # ==============================
    # Japanese — Industry & Manufacturing
    # ==============================
    {
        "name": "日刊工業新聞",
        "url": "https://news.google.com/rss/search?q=site:nikkan.co.jp+%E8%A3%BD%E9%80%A0+OR+%E7%94%A3%E6%A5%AD+OR+%E5%B7%A5%E6%A5%AD&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Manufacturing",
    },
    {
        "name": "日経産業新聞",
        "url": "https://news.google.com/rss/search?q=site:nikkei.com+%E7%94%A3%E6%A5%AD+OR+%E8%A3%BD%E9%80%A0+OR+%E3%82%B5%E3%83%97%E3%83%A9%E3%82%A4%E3%83%81%E3%82%A7%E3%83%BC%E3%83%B3&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "ものづくり.jp",
        "url": "https://news.google.com/rss/search?q=%E3%82%82%E3%81%AE%E3%81%A5%E3%81%8F%E3%82%8A+OR+%E8%A3%BD%E9%80%A0%E6%A5%AD+OR+%E5%B7%A5%E5%A0%B4&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Manufacturing",
    },
    {
        "name": "産業タイムズ社",
        "url": "https://news.google.com/rss/search?q=%E5%8D%8A%E5%B0%8E%E4%BD%93+OR+%E9%9B%BB%E5%AD%90%E9%83%A8%E5%93%81+OR+%E8%A3%BD%E9%80%A0%E6%A5%AD+OR+%E3%82%B5%E3%83%97%E3%83%A9%E3%82%A4%E3%83%81%E3%82%A7%E3%83%BC%E3%83%B3+OR+%E7%89%A9%E6%B5%81&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "Industry",
    },
    {
        "name": "ロイター産業",
        "url": "https://feeds.reuters.com/reuters/JPjpBusinessNews",
        "lang": "ja",
        "category": "Business",
    },
    # ==============================
    # Japanese — Energy & Infrastructure
    # ==============================
    {
        "name": "Google News - 製造業 (JP)",
        "url": "https://news.google.com/rss/search?q=%E8%A3%BD%E9%80%A0%E6%A5%AD+OR+%E7%94%A3%E6%A5%AD+OR+%E3%82%B5%E3%83%97%E3%83%A9%E3%82%A4%E3%83%81%E3%82%A7%E3%83%BC%E3%83%B3+OR+%E7%89%A9%E6%B5%81+OR+%E3%82%A8%E3%83%8D%E3%83%AB%E3%82%AE%E3%83%BC&hl=ja&gl=JP&ceid=JP:ja",
        "lang": "ja",
        "category": "General",
    },
]

INDUSTRY_KEYWORDS = [
    # Manufacturing
    r"\bmanufactur", r"\bindustri", r"\bfactor[y|ies]", r"\bplant\b",
    r"\bassembl", r"\bproduction\b", r"\boutput\b", r"\boperations\b",
    # Supply chain & logistics
    r"\bsupply chain\b", r"\blogistic", r"\bwarehouse\b", r"\bfreight\b",
    r"\bshipping\b", r"\btransport", r"\binventory\b", r"\bprocurement\b",
    # Energy
    r"\benergy\b", r"\bpower\b", r"\boil\b", r"\bgas\b", r"\bfuel\b",
    r"\brenewable\b", r"\bsolar\b", r"\bwind\b", r"\bnuclear\b",
    r"\belectricit", r"\bgrid\b",
    # Materials & commodities
    r"\bsteel\b", r"\bmetal\b", r"\bmining\b", r"\bmineral\b",
    r"\bcopper\b", r"\blithium\b", r"\baluminum\b", r"\bchemical\b",
    r"\bcommodit", r"\braw material",
    # Engineering & automation
    r"\bengineering\b", r"\bautomation\b", r"\brobot", r"\bmachiner",
    r"\bequipment\b", r"\binfrastructure\b", r"\bconstruction\b",
    r"\bdefense\b", r"\baerospace\b", r"\baviation\b",
    # Business strategy
    r"\bconglomerate\b", r"\bmanufacturer\b", r"\bindustrial\b",
    r"\bCaterpillar\b", r"\bHoneywell\b", r"\bDeere\b", r"\bEaton\b",
    r"\b3M\b", r"\bGE\b", r"\bSiemens\b", r"\bABB\b",
    # Japanese
    r"製造", r"産業", r"工場", r"物流", r"サプライチェーン",
    r"エネルギー", r"鉄鋼", r"素材", r"化学", r"建設",
    r"機械", r"設備", r"自動化", r"ロボット", r"インフラ",
    r"航空", r"防衛", r"重工",
]

_MEDIA_NAMES = [
    "日本経済新聞", "朝日新聞", "毎日新聞", "読売新聞",
    "Yahoo!ニュース", "NHK", "Reuters", "Bloomberg",
]
INDUSTRY_PATTERN = re.compile("|".join(INDUSTRY_KEYWORDS), re.IGNORECASE)
_TITLE_NOISE = re.compile(
    r"\s*[-–—|]?\s*(" + "|".join(re.escape(n) for n in _MEDIA_NAMES) + r")\s*$",
    re.IGNORECASE,
)

USER_AGENT = "MyHub-IndustryFetcher/1.0"
FETCH_TIMEOUT = 15

FILTER_SOURCES = {
    "Google News - Industry",
    "Google News - 製造業 (JP)",
    "Bloomberg Industry",
    "Financial Times Industry",
    "Reuters Business",
    "WSJ Business",
    "Harvard Business Review",
    "MIT Sloan Management",
    "MIT Technology Review",
    "IEEE Spectrum",
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


def is_industry_related(title, description="", source_name=""):
    clean_title = _TITLE_NOISE.sub("", title)
    clean_desc = _TITLE_NOISE.sub("", description)
    if source_name:
        clean_title = clean_title.replace(source_name, "")
        clean_desc = clean_desc.replace(source_name, "")
    return bool(INDUSTRY_PATTERN.search(f"{clean_title} {clean_desc}"))


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
        if feed_config["name"] in FILTER_SOURCES and not is_industry_related(
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
        if feed_config["name"] in FILTER_SOURCES and not is_industry_related(
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
    print("=== Industry News Fetcher ===")
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
    out_path = os.path.join(out_dir, "industry-news.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(f"\nDone! {len(all_articles)} articles saved to {out_path}")


if __name__ == "__main__":
    main()
