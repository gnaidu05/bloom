#!/usr/bin/env python3
"""
Find real, recent news via live RSS feeds and emit JSON for edition generation.

This is FULLY DETERMINISTIC — no LLM, no search API, no hardcoded stories.
It pulls live headlines from public RSS/Atom feeds grouped by desk, keeps items
published within the recency window, dedupes, and prints a JSON array of 6
stories (2 per desk) to stdout. All logging goes to stderr so stdout is pure JSON.

Story links are REAL (straight from the feed), so "Sources" always resolves.

Exit codes:
  0 = success, JSON printed to stdout
  1 = could not assemble 6 stories (feeds down / too little recent news)
"""

import sys
import re
import json
import html
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

RECENCY_DAYS = 7          # prefer items this fresh
FALLBACK_DAYS = 14        # widen to this if a desk is short
PER_DESK = 2
UA = {"User-Agent": "Mozilla/5.0 (Morning Bloom feed reader)"}

ROOT = Path(__file__).resolve().parent.parent
EDITIONS_DIR = ROOT / "editions"
REPUBLISH_LOOKBACK_DAYS = 10   # don't re-pick a story used in an edition this recent

# desk -> (theme, category, [feed urls, best first])
DESKS = [
    ("t-teal", "AI & Technology", [
        "https://techcrunch.com/tag/artificial-intelligence/feed/",
        "https://feeds.arstechnica.com/arstechnica/technology-lab",
        "https://venturebeat.com/category/ai/feed/",
    ]),
    ("t-amber", "IT Industry", [
        "https://www.bleepingcomputer.com/feed/",
        "https://www.theregister.com/security/headlines.atom",
    ]),
    ("t-navy", "Recruitment & HR", [
        "https://techcrunch.com/tag/layoffs/feed/",
        "https://www.hrdive.com/feeds/news/",
    ]),
]

WHY = {
    "AI & Technology": "Shifts in AI capability and tooling shape how every team builds, ships, and competes.",
    "IT Industry": "Security and infrastructure incidents set the risk backdrop that IT teams plan and budget against.",
    "Recruitment & HR": "Hiring, layoff, and pay signals map where tech talent is moving and what skills now command a premium.",
}
FIGCAP = {
    "AI & Technology": "AI & technology desk",
    "IT Industry": "IT industry & security desk",
    "Recruitment & HR": "Recruitment & HR desk",
}


def log(msg, level="INFO"):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", file=sys.stderr, flush=True)


def strip_html(s: str) -> str:
    s = re.sub(r"(?is)<(script|style).*?</\1>", " ", s or "")
    s = re.sub(r"(?s)<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def parse_date(raw: str):
    if not raw:
        return None
    raw = raw.strip()
    try:
        d = parsedate_to_datetime(raw)          # RFC 822 (RSS)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        pass
    try:
        iso = raw.replace("Z", "+00:00")         # ISO 8601 (Atom)
        d = datetime.fromisoformat(iso)
        if d.tzinfo is None:
            d = d.replace(tzinfo=timezone.utc)
        return d
    except Exception:
        return None


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read()


def source_name(url: str) -> str:
    host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0]
    names = {
        "techcrunch.com": "TechCrunch",
        "feeds.arstechnica.com": "Ars Technica",
        "arstechnica.com": "Ars Technica",
        "venturebeat.com": "VentureBeat",
        "bleepingcomputer.com": "BleepingComputer",
        "theregister.com": "The Register",
        "hrdive.com": "HR Dive",
    }
    return names.get(host, host)


def parse_feed(xml_bytes: bytes):
    """Return list of dicts: title, link, desc, date (datetime)."""
    root = ET.fromstring(xml_bytes)
    for e in root.iter():                         # strip namespaces
        if isinstance(e.tag, str) and "}" in e.tag:
            e.tag = e.tag.split("}", 1)[1]
    out = []
    for it in root.iter("item"):                  # RSS
        link = (it.findtext("link") or "").strip()
        out.append({
            "title": strip_html(it.findtext("title") or ""),
            "link": link,
            "desc": strip_html(it.findtext("description") or ""),
            "date": parse_date(it.findtext("pubDate") or ""),
        })
    for it in root.iter("entry"):                 # Atom
        link = ""
        for l in it.iter("link"):
            href = l.get("href")
            if href and (l.get("rel") in (None, "alternate")):
                link = href
                break
        body = it.findtext("summary") or it.findtext("content") or ""
        out.append({
            "title": strip_html(it.findtext("title") or ""),
            "link": link.strip(),
            "desc": strip_html(body),
            "date": parse_date(it.findtext("updated") or it.findtext("published") or ""),
        })
    return [i for i in out if i["title"] and i["link"]]


def sentences(text: str):
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in parts if len(p.strip()) > 20]


def trim(text: str, limit: int) -> str:
    """Trim to <= limit on a word boundary, adding an ellipsis if cut."""
    text = text.strip()
    if len(text) <= limit:
        return text
    cut = text[:limit].rsplit(" ", 1)[0].rstrip(" ,;:—-")
    if not cut.endswith((".", "!", "?", "…")):
        cut += "…"
    return cut


def build_story(item, theme, category, feed_url):
    desc = item["desc"]
    sents = sentences(desc)
    deck = trim(sents[0] if sents else desc, 180)
    para1 = " ".join(sents[:2]) if sents else trim(desc, 300)
    para2 = " ".join(sents[2:4]) if len(sents) > 2 else \
        f"Full reporting is available from {source_name(feed_url)} at the source link below."
    takeaways = [trim(s, 140) for s in (sents[:3] if sents else [item["title"]])]
    if not takeaways:
        takeaways = ["See the linked source for full details."]
    d = item["date"]
    datestr = d.strftime("%b %d, %Y") if d else "recent"
    src = source_name(feed_url)
    sources = (f'<strong>Sources ({datestr}):</strong> '
               f'<a href="{item["link"]}">{html.escape(item["title"][:70])} — {src}</a>')
    topics = [t for t in re.findall(r"[A-Z][a-zA-Z]{3,}", item["title"])][:3] or [src]
    return {
        "theme": theme,
        "category": category,
        "headline": item["title"][:110],
        "deck": deck or item["title"],
        "figcap": FIGCAP.get(category, "News"),
        "para1": para1 or deck or item["title"],
        "para2": para2,
        "takeaways": takeaways,
        "why": WHY.get(category, "A notable development for people tracking this sector."),
        "sources": sources,
        "topics": topics,
    }


def norm(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", t.lower()).strip()


def load_recently_published(days=REPUBLISH_LOOKBACK_DAYS):
    """Scan editions/*.html from the last N days and return (titles, links)
    already used, so today's picks don't repeat a story a recent edition ran."""
    titles, links = set(), set()
    if not EDITIONS_DIR.is_dir():
        return titles, links
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=days)
    for f in EDITIONS_DIR.glob("????-??-??.html"):
        try:
            d = datetime.strptime(f.stem, "%Y-%m-%d").date()
        except ValueError:
            continue
        if d < cutoff:
            continue
        try:
            text = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in re.finditer(r"<h2>(.*?)</h2>", text, re.S):
            n = norm(strip_html(m.group(1)))
            if n:
                titles.add(n)
        for m in re.finditer(r'class="sources"[^>]*>.*?<a href="([^"]+)"', text, re.S):
            links.add(m.group(1).strip())
    return titles, links


def collect_desk(theme, category, feeds, cutoff, seen_titles, seen_links=frozenset()):
    """Gather candidate items across a desk's feeds, freshest first."""
    cand = []
    for url in feeds:
        try:
            items = parse_feed(fetch(url))
            log(f"{category}: {len(items)} items from {source_name(url)}")
        except Exception as e:
            log(f"{category}: FAILED {url} -> {type(e).__name__}: {e}", "WARN")
            continue
        for it in items:
            if it["date"] and it["date"] >= cutoff:
                cand.append((it, url))
    # newest first
    cand.sort(key=lambda x: x[0]["date"], reverse=True)
    chosen = []
    for it, url in cand:
        n = norm(it["title"])
        if not n or n in seen_titles or it["link"].strip() in seen_links:
            continue
        seen_titles.add(n)
        chosen.append(build_story(it, theme, category, url))
        if len(chosen) >= PER_DESK:
            break
    return chosen


def main():
    log("Starting RSS story discovery")
    now = datetime.now(timezone.utc)
    stories = []
    seen = set()

    pub_titles, pub_links = load_recently_published()
    log(f"Excluding {len(pub_titles)} story title(s) from editions in the last "
        f"{REPUBLISH_LOOKBACK_DAYS} days")

    # First pass at 7 days, widen per-desk to 14 if short. Recently-published
    # stories are excluded so the feed's still-top item doesn't repeat verbatim.
    for theme, category, feeds in DESKS:
        seen_titles = seen | pub_titles
        got = collect_desk(theme, category, feeds,
                           now - timedelta(days=RECENCY_DAYS), seen_titles, pub_links)
        if len(got) < PER_DESK:
            log(f"{category}: only {len(got)} in {RECENCY_DAYS}d, widening to {FALLBACK_DAYS}d", "WARN")
            got = collect_desk(theme, category, feeds,
                               now - timedelta(days=FALLBACK_DAYS), seen_titles, pub_links) or got
        if len(got) < PER_DESK:
            log(f"{category}: still only {len(got)} after widening; allowing repeats "
                f"of recently-published stories to fill the desk", "WARN")
            got = collect_desk(theme, category, feeds,
                               now - timedelta(days=FALLBACK_DAYS), seen) or got
        seen |= {norm(s["headline"]) for s in got}
        stories.extend(got[:PER_DESK])

    if len(stories) < 6:
        log(f"Only assembled {len(stories)} stories; need 6. Aborting.", "ERROR")
        return 1

    log(f"Assembled {len(stories)} stories")
    print(json.dumps(stories[:6], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
