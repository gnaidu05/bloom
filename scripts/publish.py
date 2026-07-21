#!/usr/bin/env python3
"""Publish The Morning Bloom.

Promotes the newest file in editions/ (named YYYY-MM-DD.html) to index.html
and rebuilds archive.html with a date-wise list of all editions.
Run from anywhere: python3 scripts/publish.py
"""
import re
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://gnaidu05.github.io/bloom"

ARCHIVE_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>The Morning Bloom — Archive</title>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg%20xmlns%3D%27http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%27%20viewBox%3D%270%200%2064%2064%27%3E%3Cg%3E%3Cg%20transform%3D%27rotate%280%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%234fb0c4%27%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%27rotate%2860%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%23f2a9c4%27%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%27rotate%28120%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%23c14066%27%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%27rotate%28180%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%23e2b264%27%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%27rotate%28240%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%23c97a10%27%2F%3E%3C%2Fg%3E%3Cg%20transform%3D%27rotate%28300%2032%2032%29%27%3E%3Cpath%20d%3D%27M32%2033%20C25%2021%2025%2011%2032%205%20C39%2011%2039%2021%2032%2033%20Z%27%20fill%3D%27%232b96ad%27%2F%3E%3C%2Fg%3E%3C%2Fg%3E%3Ccircle%20cx%3D%2732%27%20cy%3D%2732%27%20r%3D%278.5%27%20fill%3D%27%23fdf6e8%27%2F%3E%3Ccircle%20cx%3D%2732%27%20cy%3D%2732%27%20r%3D%274%27%20fill%3D%27%23c14066%27%2F%3E%3C%2Fsvg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Libre+Bodoni:wght@400;500;600;700&family=Public+Sans:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
<style>
  :root{{--bg:#fafafa; --card:#fff; --ink:#18181b; --muted:#71717a; --teal:#0d7085; --rose:#c14066; --amber:#c97a10; --navy:#1d3557; --line:#e4e4e7; --radius:18px; --shadow:0 1px 2px rgba(24,24,27,.05), 0 2px 8px rgba(24,24,27,.05);}}
  *{{box-sizing:border-box; margin:0; padding:0;}}
  body{{background:var(--bg); color:var(--ink); font-family:'Public Sans','Segoe UI',Roboto,Arial,sans-serif; line-height:1.6; padding:2rem 1.25rem 3rem;}}
  .sheet{{max-width:720px; margin:0 auto; display:flex; flex-direction:column; gap:1.2rem;}}
  .card{{background:var(--card); border-radius:var(--radius); box-shadow:var(--shadow); overflow:hidden;}}
  .masthead{{padding:1.6rem 2rem 1.4rem; position:relative;}}
  .masthead::before{{content:""; position:absolute; inset:0 0 auto 0; height:8px; background:linear-gradient(90deg,var(--teal) 0 34%,var(--rose) 34% 67%,var(--amber) 67% 100%);}}
  .pill{{display:inline-block; background:var(--teal); color:#fff; font-size:.68rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; padding:.35rem .9rem; border-radius:999px;}}
  h1{{font-family:'Libre Bodoni',Georgia,serif; font-size:clamp(1.9rem,6vw,2.8rem); font-weight:700; text-transform:uppercase; letter-spacing:-.01em; margin:.6rem 0 .2rem;}}
  h1 .bloom{{color:var(--rose); font-style:italic;}}
  .titlelock{{display:flex; align-items:center; gap:.85rem; margin:.6rem 0 .2rem;}}
  .titlelock h1{{margin:0;}}
  .logo-mark{{width:clamp(42px,7vw,56px); height:auto; flex:none; filter:drop-shadow(0 2px 5px rgba(24,24,27,.16)); transition:transform .7s cubic-bezier(.34,1.56,.64,1);}}
  .titlelock:hover .logo-mark{{transform:rotate(60deg);}}
  @media (prefers-reduced-motion: reduce){{.logo-mark{{transition:none;}} .titlelock:hover .logo-mark{{transform:none;}}}}
  .tagline{{color:var(--muted); font-size:.9rem;}}
  .back{{margin-top:.9rem;}}
  .back a{{font-size:.75rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; background:#fdf1e0; color:var(--amber); padding:.35rem .85rem; border-radius:999px; text-decoration:none;}}
  .listcard{{padding:1.3rem 1.5rem;}}
  .listcard h2{{font-size:.78rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:var(--navy); margin-bottom:.9rem;}}
  ul{{list-style:none;}}
  li a{{display:flex; justify-content:space-between; align-items:center; padding:.75rem 1rem; margin-bottom:.55rem; border-radius:12px; background:#fafafa; border:1px solid var(--line); color:var(--ink); text-decoration:none; font-weight:600; font-size:.95rem; transition:background .2s ease, border-color .2s ease;}}
  li a:hover{{background:#e9f3f5; border-color:var(--teal);}}
  li a:focus-visible{{outline:3px solid var(--teal); outline-offset:2px;}}
  li .latest{{font-size:.66rem; letter-spacing:.12em; text-transform:uppercase; color:#fff; background:var(--rose); padding:.2rem .6rem; border-radius:999px;}}
  footer{{background:var(--navy); color:#cfdcea; text-align:center; padding:1.2rem 2rem; font-size:.78rem;}}
</style>
</head>
<body>
<div class="sheet">
  <header class="card masthead">
    <span class="pill">The Archive</span>
    <div class="titlelock">
      <svg class="logo-mark" viewBox="0 0 64 64" role="img" aria-label="The Morning Bloom emblem — a six-petal bloom">
        <g>
          <g transform="rotate(0 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#4fb0c4"/></g>
          <g transform="rotate(60 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#f2a9c4"/></g>
          <g transform="rotate(120 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#c14066"/></g>
          <g transform="rotate(180 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#e2b264"/></g>
          <g transform="rotate(240 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#c97a10"/></g>
          <g transform="rotate(300 32 32)"><path d="M32 33 C25 21 25 11 32 5 C39 11 39 21 32 33 Z" fill="#2b96ad"/></g>
        </g>
        <circle cx="32" cy="32" r="8.5" fill="#fdf6e8"/>
        <circle cx="32" cy="32" r="4" fill="#c14066"/>
      </svg>
      <h1>The Morning <span class="bloom">Bloom</span></h1>
    </div>
    <p class="tagline">Your five-minute edge on AI, technology and the future of work — every morning</p>
    <p class="back"><a href="index.html">→ Today's Edition</a></p>
  </header>
  <div class="card listcard">
    <h2>Past editions, date-wise</h2>
    <ul>
{rows}
    </ul>
  </div>
  <footer class="card">
    <p>The Morning Bloom · Pune Edition · <a href="index.html#subscribe" style="color:#8fd0e2">Subscribe</a> · Summaries are Claude's own words; source links carry the full reporting.</p>
  </footer>
</div>
</body>
</html>
"""


def main() -> None:
    editions = sorted((ROOT / "editions").glob("????-??-??.html"), reverse=True)
    if not editions:
        raise SystemExit("No editions found in editions/")

    latest = editions[0]
    # Edition pages link to ../archive.html etc.; from the root copy those
    # links must drop the ../ prefix.
    (ROOT / "index.html").write_text(
        latest.read_text(encoding="utf-8").replace('href="../', 'href="'),
        encoding="utf-8",
    )

    rows = []
    for e in editions:
        d = datetime.strptime(e.stem, "%Y-%m-%d")
        pretty = d.strftime("%A, %B %d, %Y").replace(" 0", " ")
        badge = '<span class="latest">Latest</span>' if e == latest else ""
        rows.append(f'    <li><a href="editions/{e.name}"><span class="d">{pretty}</span>{badge}</a></li>')

    (ROOT / "archive.html").write_text(
        ARCHIVE_TEMPLATE.format(rows="\n".join(rows)), encoding="utf-8"
    )

    # RSS feed — consumed by the newsletter service (RSS-to-email) and feed readers.
    items = []
    for e in editions[:20]:
        d = datetime.strptime(e.stem, "%Y-%m-%d")
        pretty = d.strftime("%A, %B %d, %Y").replace(" 0", " ")
        pub = d.strftime("%a, %d %b %Y") + " 01:00:00 GMT"
        html = e.read_text(encoding="utf-8")
        m = re.search(r"Inside this issue</div>\s*<ol>(.*?)</ol>", html, re.S)
        heads = re.findall(r"<li>(.*?)</li>", m.group(1), re.S) if m else []
        heads = [re.sub(r"<[^>]+>", "", h).strip().replace("&amp;", "&") for h in heads]
        desc = " · ".join(heads) or "The day's stories across AI & Technology, IT Industry, and Recruitment & HR."
        url = f"{SITE}/editions/{e.name}"
        items.append(
            f"    <item>\n"
            f"      <title>The Morning Bloom — {escape(pretty)}</title>\n"
            f"      <link>{url}</link>\n"
            f"      <guid>{url}</guid>\n"
            f"      <pubDate>{pub}</pubDate>\n"
            f"      <description>{escape(desc)}</description>\n"
            f"    </item>"
        )
    feed = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        "  <channel>\n"
        "    <title>The Morning Bloom</title>\n"
        f"    <link>{SITE}/</link>\n"
        "    <description>Daily news briefing — AI &amp; Technology, IT Industry, Recruitment &amp; HR. Pune Edition.</description>\n"
        "    <language>en</language>\n"
        + "\n".join(items) + "\n"
        "  </channel>\n"
        "</rss>\n"
    )
    (ROOT / "feed.xml").write_text(feed, encoding="utf-8")
    print(f"Published {latest.name} -> index.html; archive.html lists {len(editions)} edition(s); feed.xml has {len(items)} item(s).")


if __name__ == "__main__":
    main()
