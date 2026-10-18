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
  1 = could not assemble 9 stories (feeds down / too little recent news)
"""

import os
import sys
import time
import re
import json
import html
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from pathlib import Path

RECENCY_DAYS = 4          # "latest": prefer items from the last few days
FALLBACK_DAYS = 8         # widen to this only if a desk is short
# AI is the edition's primary focus: it gets the lead slots (5 of 9); the
# other desks fill the rest. Total stays 9 (generate_edition caps at 9 cards).
PER_DESK = {"AI & Technology": 5, "IT Industry": 2, "Recruitment & HR": 2}
UA = {"User-Agent": "Mozilla/5.0 (Morning Bloom feed reader)"}

ROOT = Path(__file__).resolve().parent.parent
EDITIONS_DIR = ROOT / "editions"
REPUBLISH_LOOKBACK_DAYS = 10   # don't re-pick a story used in an edition this recent

# desk -> (theme, category, [feed urls, best first])
DESKS = [
    ("t-teal", "AI & Technology", [
        "https://techcrunch.com/category/artificial-intelligence/feed/",
        "https://venturebeat.com/category/ai/feed/",
        "https://www.technologyreview.com/topic/artificial-intelligence/feed",
        "https://openai.com/news/rss.xml",
        "https://deepmind.google/blog/rss.xml",
    ]),
    ("t-amber", "IT Industry", [
        "https://techcrunch.com/category/enterprise/feed/",
        "https://www.zdnet.com/news/rss.xml",
        "https://feeds.arstechnica.com/arstechnica/index",
        "https://www.theregister.com/headlines.atom",
        "https://www.bleepingcomputer.com/feed/",
    ]),
    ("t-navy", "Recruitment & HR", [
        "https://hr.economictimes.indiatimes.com/rss/topstories",
        "https://www.thehindu.com/education/careers/feeder/default.rss",
        "https://indianexpress.com/section/education/feed/",
        "https://www.livemint.com/rss/education",
    ]),
]

WHY = {
    "AI & Technology": "What's new and trending in AI, and how each shift moves the global market.",
    "IT Industry": "The global tech-industry moves — launches, deals, outages and market shifts — that set how the sector competes.",
    "Recruitment & HR": "How AI is reshaping Indian recruitment — campus and lateral — and the hiring, pay and skills trends that follow.",
}
FIGCAP = {
    "AI & Technology": "AI & technology desk",
    "IT Industry": "Global IT industry desk",
    "Recruitment & HR": "India recruitment — campus & lateral desk",
}

# Per-desk relevance ranking. Items are scored on title+description and the
# highest scorers rank first (newest-first within a score). "strong" terms
# weigh 3, "weak" terms weigh 1. Matching is word-boundary (so "ai" matches
# "AI" / "AI-powered" but not "email" or "chain"); multi-word terms allow any
# whitespace. Desks absent here stay pure newest-first.
#
#   AI & Technology / IT Industry: surface what's NEW, TRENDING and
#   MARKET-MOVING (launches, funding, deals, adoption, regulation) over
#   incremental/internal items.
#   Recruitment & HR: prioritise AI's impact on INDIAN recruitment and new
#   hiring trends across BOTH campus and lateral.
_TREND_STRONG = [
    "launch", "launches", "launched", "unveil", "unveils", "release",
    "releases", "released", "rolls out", "rollout", "general availability",
    "raises", "funding", "funding round", "valuation", "billion", "ipo",
    "acquire", "acquires", "acquisition", "merger", "partnership", "partners",
    "deal", "market", "markets", "enterprise", "adoption", "revenue",
    "earnings", "profit", "demand", "surge", "record", "breakthrough",
    "regulation", "regulator", "lawsuit", "ban", "bans", "outage", "shares",
    "stock", "layoffs",
]
DESK_KEYWORDS = {
    "AI & Technology": {
        "strong": _TREND_STRONG + ["model", "models", "agent", "agents", "frontier"],
        "weak": ["ai", "artificial intelligence", "genai", "gen ai", "llm",
                 "gpt", "chip", "chips", "gpu", "open source", "openai",
                 "anthropic", "google", "nvidia", "microsoft", "meta"],
    },
    "IT Industry": {
        "strong": _TREND_STRONG + ["cloud", "datacenter", "data center",
                 "chip", "semiconductor", "saas", "breach", "ransomware"],
        "weak": ["software", "hardware", "data", "platform", "startup",
                 "google", "microsoft", "amazon", "aws", "oracle", "ibm",
                 "security", "enterprise"],
    },
    "Recruitment & HR": {
        "strong": [
            "ai", "artificial intelligence", "genai", "gen ai",
            "generative ai", "automation", "placement", "placements",
            "campus hiring", "campus placement", "lateral", "lateral hiring",
            "recruit", "recruitment", "hiring", "hire", "layoff", "layoffs",
            "fresher", "freshers", "ctc", "lpa", "attrition", "workforce",
            "headcount", "hike", "appraisal", "offer letter", "offers",
            "job cuts", "mass hiring", "net hiring", "gcc", "apprentice",
            "internship", "upskill", "reskill", "stipend",
        ],
        "weak": [
            "iit", "iim", "nit", "iiit", "mba", "salary", "package", "job",
            "jobs", "career", "intern", "talent", "graduate", "employee",
            "employer", "skills", "tcs", "infosys", "wipro", "cognizant",
            "hcl", "accenture", "hr",
        ],
    },
}


def _compile_terms(terms):
    """One case-insensitive, word-boundary regex matching any of the terms.
    Multi-word terms match across any run of whitespace."""
    parts = []
    for t in terms:
        t = t.strip().lower()
        if t:
            words = [re.escape(w) for w in t.split()]
            parts.append(r"\b" + r"\s+".join(words) + r"\b")
    return re.compile("|".join(parts), re.I) if parts else None


DESK_PATTERNS = {
    cat: {"strong": _compile_terms(kw["strong"]),
          "weak": _compile_terms(kw["weak"])}
    for cat, kw in DESK_KEYWORDS.items()
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
        "technologyreview.com": "MIT Technology Review",
        "openai.com": "OpenAI",
        "deepmind.google": "Google DeepMind",
        "wired.com": "WIRED",
        "marktechpost.com": "MarkTechPost",
        "simonwillison.net": "Simon Willison's Weblog",
        "huggingface.co": "Hugging Face",
        "krebsonsecurity.com": "Krebs on Security",
        "shrm.org": "SHRM",
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


HEDGES = re.compile(
    r"\b(reportedly|allegedly|alleged|according to|sources? (?:say|said|familiar)|"
    r"claims?|claimed|could|may|might|plans? to|expected to|set to|suspected|"
    r"unconfirmed|rumou?rs?|preliminary|early|beta|preview)\b", re.I)


def unproven(item, src):
    """Deterministic 'what's unproven' line: flag hedged language in the feed
    text, otherwise state plainly that it rests on a single outlet's report."""
    text = f'{item["title"]}. {item["desc"]}'
    hits = []
    for m in HEDGES.finditer(text):
        w = m.group(1).lower()
        if w not in hits:
            hits.append(w)
    if hits:
        return (f"The reporting leans on hedged language (\u201c{hits[0]}\u201d"
                + (f", \u201c{hits[1]}\u201d" if len(hits) > 1 else "")
                + f"), so treat specifics as unconfirmed until {src} or the company follows up.")
    return (f"Rests on a single outlet\u2019s report ({src}); the figures and claims "
            "have not been independently checked here.")


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
        "unproven": unproven(item, src),
        "_src": src,
        "_desc": trim(item["desc"], 1500),
        "why": WHY.get(category, "A notable development for people tracking this sector."),
        "sources": sources,
        "topics": topics,
    }


LLM_URL = "https://openrouter.ai/api/v1/chat/completions"
# Free open-weight models by default, tried in order; override with
# OPENROUTER_MODEL (comma-separated) to use a paid model.
LLM_MODELS = [m.strip() for m in os.environ.get(
    "OPENROUTER_MODEL",
    "nvidia/nemotron-3-super-120b-a12b:free,google/gemma-4-31b-it:free").split(",") if m.strip()]
LLM_MODEL = LLM_MODELS[0]
LLM_PROMPT = """You are the editor of a daily tech-news brief. Using ONLY the headline and
excerpt below (never add facts, numbers or names that are not in them), write:
- "deck": one sentence (max 25 words) summarising the story
- "happened": 2-3 short bullets with the concrete specifics (who, what, numbers, dates)
- "changes": 1-2 sentences on what this changes for tech, IT or HR professionals
- "unproven": 1-2 sentences on what is still unconfirmed, single-sourced, or unclear
Reply with a single JSON object with exactly those four keys and nothing else.

Desk: {category}
Source: {src}
Headline: {headline}
Excerpt: {desc}"""


def llm_enrich(story):
    """Rewrite one story's analysis via OpenRouter. Returns True on success;
    on any failure the deterministic text already on the story is kept."""
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        return False
    prompt = LLM_PROMPT.format(
        category=story["category"], src=story["_src"],
        headline=story["headline"], desc=story["_desc"] or story["deck"])
    clean = lambda t: html.escape(re.sub(r"^[\s\-*•]+", "", str(t)).strip(), quote=False)
    last = None
    for model in LLM_MODELS:
        body = json.dumps({"model": model, "temperature": 0.2,
                           "messages": [{"role": "user", "content": prompt}]}).encode()
        req = urllib.request.Request(LLM_URL, data=body, headers={
            "Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=90) as r:
                    text = json.load(r)["choices"][0]["message"]["content"]
                out = json.loads(re.search(r"\{.*\}", text, re.S).group(0))
                happened = [clean(b) for b in out["happened"] if clean(b)]
                deck, changes, unp = (clean(out[k]) for k in ("deck", "changes", "unproven"))
                if not (happened and deck and changes and unp):
                    raise ValueError("empty field")
                story.update(deck=deck, takeaways=happened[:3], why=changes, unproven=unp)
                return True
            except Exception as e:
                last = e
                if isinstance(e, urllib.error.HTTPError) and e.code == 429 and attempt < 2:
                    time.sleep(5 * (attempt + 1))
                    continue
                break
    log(f"LLM enrich failed for '{story['headline'][:50]}': {type(last).__name__}: {last}", "WARN")
    return False


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
    # Rank: highest relevance first (weighted, word-boundary DESK_PATTERNS),
    # newest-first within each score. Desks without patterns stay newest-first.
    pats = DESK_PATTERNS.get(category)

    def relevance(it):
        if not pats:
            return 0
        text = (it["title"] + " " + it.get("desc", "")).lower()
        strong = len(set(pats["strong"].findall(text))) if pats["strong"] else 0
        weak = len(set(pats["weak"].findall(text))) if pats["weak"] else 0
        return 3 * strong + weak

    cand.sort(key=lambda x: (relevance(x[0]), x[0]["date"]), reverse=True)
    chosen = []
    for it, url in cand:
        n = norm(it["title"])
        if not n or n in seen_titles or it["link"].strip() in seen_links:
            continue
        seen_titles.add(n)
        chosen.append(build_story(it, theme, category, url))
        if len(chosen) >= PER_DESK[category]:
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
        if len(got) < PER_DESK[category]:
            log(f"{category}: only {len(got)} in {RECENCY_DAYS}d, widening to {FALLBACK_DAYS}d", "WARN")
            got = collect_desk(theme, category, feeds,
                               now - timedelta(days=FALLBACK_DAYS), seen_titles, pub_links) or got
        if len(got) < PER_DESK[category]:
            log(f"{category}: still only {len(got)} after widening; allowing repeats "
                f"of recently-published stories to fill the desk", "WARN")
            got = collect_desk(theme, category, feeds,
                               now - timedelta(days=FALLBACK_DAYS), seen) or got
        seen |= {norm(s["headline"]) for s in got}
        stories.extend(got[:PER_DESK[category]])

    if len(stories) < 6:
        log(f"Only assembled {len(stories)} stories; need at least 6. Aborting.", "ERROR")
        return 1

    log(f"Assembled {len(stories)} stories")
    if os.environ.get("OPENROUTER_API_KEY"):
        ok = sum(llm_enrich(st) for st in stories)
        log(f"LLM analysis applied to {ok}/{len(stories)} stories ({LLM_MODEL})")
    else:
        log("OPENROUTER_API_KEY not set; using deterministic summaries", "WARN")
    for st in stories:
        st.pop("_src", None); st.pop("_desc", None)
    print(json.dumps(stories, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
