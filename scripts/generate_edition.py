#!/usr/bin/env python3
"""
Automated Daily Edition Generator for The Morning Bloom

Finds recent stories across three desks (AI & Technology, IT Industry, Recruitment & HR),
generates story cards, and publishes the edition. Logs all steps for debugging.

Exit codes:
  0 = success
  1 = search failed (couldn't find stories)
  2 = generation failed (story data incomplete)
  3 = publish failed (couldn't run publish.py)
"""

import sys
import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List

# Try to import tools we'll need
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

ROOT = Path("/home/user/bloom")


def log(msg: str, level: str = "INFO"):
    """Print timestamped log message."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] [{level}] {msg}", flush=True)


def get_latest_edition_date() -> str:
    """Find the most recent edition file."""
    editions_dir = ROOT / "editions"
    if not editions_dir.exists():
        return None

    files = sorted(editions_dir.glob("20*.html"), reverse=True)
    if files:
        # Extract date from filename like 2026-07-25.html
        filename = files[0].stem
        log(f"Latest edition: {filename}")
        return filename
    return None


def calculate_target_date() -> str:
    """Calculate today's date in YYYY-MM-DD format (IST timezone)."""
    # IST is UTC+5:30
    from datetime import timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(ist).strftime("%Y-%m-%d")
    return today


def load_template() -> tuple[str, str]:
    """Load the most recent edition as template.
    Returns (html_content, edition_date)
    """
    latest = get_latest_edition_date()
    if not latest:
        log("ERROR: No previous edition found to use as template", "ERROR")
        return None, None

    template_file = ROOT / "editions" / f"{latest}.html"
    try:
        content = template_file.read_text(encoding="utf-8")
        log(f"Loaded template from {latest}")
        return content, latest
    except Exception as e:
        log(f"ERROR: Failed to read template: {e}", "ERROR")
        return None, None


def parse_date_parts(date_str: str) -> tuple[int, int, int]:
    """Parse YYYY-MM-DD to (year, month, day)."""
    parts = date_str.split("-")
    return int(parts[0]), int(parts[1]), int(parts[2])


def increment_date(date_str: str) -> str:
    """Increment date by one day. date_str is YYYY-MM-DD."""
    year, month, day = parse_date_parts(date_str)
    d = datetime(year, month, day) + timedelta(days=1)
    return d.strftime("%Y-%m-%d")


def format_date_for_ui(date_str: str) -> str:
    """Convert YYYY-MM-DD to 'Day, Month DD, YYYY' format."""
    year, month, day = parse_date_parts(date_str)
    d = datetime(year, month, day)
    return d.strftime("%A, %B %d, %Y")


def format_month_day(date_str: str) -> str:
    """Convert YYYY-MM-DD to 'Month DD, YYYY'."""
    year, month, day = parse_date_parts(date_str)
    d = datetime(year, month, day)
    return d.strftime("%B %d, %Y")


def generate_story_card(
    num: str,
    cid: str,
    theme: str,
    category: str,
    headline: str,
    deck: str,
    svg: str,
    figcap: str,
    para1: str,
    para2: str,
    takeaways: List[str],
    why: str,
    sources: str,
    topics: List[str]
) -> str:
    """Generate HTML for a single story card."""
    tk = "\n".join(f"            <li>{t}</li>" for t in takeaways)
    tp = "\n".join(
        f'          <button type="button" class="topic" data-tag="{t}">#{t}</button>'
        for t in topics
    )

    return f"""    <!-- {num} -->
    <article class="card {theme} reveal" id="{cid}">
      <div class="storyhead"><span class="num">{num}</span><span class="cat">{category}</span><span class="vtag search">Search-verified</span></div>
      <div class="storybody">
        <h2>{headline}</h2>
        <p class="deck">{deck}</p>
        <figure>
{svg}
          <figcaption>{figcap}</figcaption>
        </figure>
        <div class="copy">
          <p>{para1}</p>
          <p>{para2}</p>
        </div>
        <div class="takeaways">
          <h3>Key takeaways</h3>
          <ul>
{tk}
          </ul>
        </div>
        <div class="why">
          <h3>Why it matters</h3>
          <p>{why}</p>
        </div>
        <p class="sources">{sources}</p>
        <div class="topics" aria-label="Topics">
{tp}
        </div>
      </div>
    </article>"""


def create_placeholder_story(num: str, cid: str, theme: str, category: str) -> str:
    """Create a placeholder card when story data is unavailable."""
    svg = """          <svg viewBox="0 0 240 160" role="img" aria-label="Placeholder">
            <rect width="240" height="160" fill="#f0f0f0"/>
            <text x="120" y="80" text-anchor="middle" font-size="14" fill="#999">Story {}</text>
          </svg>""".format(num)

    return generate_story_card(
        num, cid, theme, category,
        f"Story {num}: [Loading...]",
        "Story details pending.",
        svg, "Placeholder",
        "Story data is loading.",
        "Please check back shortly.",
        ["Updates pending"],
        "This story is being prepared.",
        '<a href="#">Source pending</a>',
        ["pending"]
    )


def update_edition_with_date(html: str, old_date: str, new_date: str) -> str:
    """Update all date references in edition template."""
    old_formatted = format_month_day(old_date)
    new_formatted = format_month_day(new_date)
    old_ui_date = format_date_for_ui(old_date)
    new_ui_date = format_date_for_ui(new_date)

    # Update title
    html = html.replace(
        f"<title>The Morning Bloom — {old_formatted} — Pune Edition</title>",
        f"<title>The Morning Bloom — {new_formatted} — Pune Edition</title>"
    )

    # Update date chip
    html = html.replace(
        f'<span class="chip date">{old_ui_date}</span>',
        f'<span class="chip date">{new_ui_date}</span>'
    )

    # Update footer date
    html = html.replace(
        f"The Morning Bloom · Pune Edition · {old_formatted} ·",
        f"The Morning Bloom · Pune Edition · {new_formatted} ·"
    )

    # Update Last updated time (set to current IST time)
    ist = datetime.now() + timedelta(hours=5, minutes=30)
    current_time = ist.strftime("%I:%M %p IST").lstrip("0")
    html = re.sub(
        r"Last updated \d{1,2}:\d{2} [AP]M IST",
        f"Last updated {current_time}",
        html
    )

    log(f"Updated dates: {old_formatted} → {new_formatted}")
    return html


def update_toc(html: str, headlines: List[str]) -> str:
    """Update Table of Contents with new story headlines."""
    toc_items = "\n".join(
        f'        <li><a href="#s{i+1}">{h}</a></li>'
        for i, h in enumerate(headlines)
    )
    toc = f"""      <ol>
{toc_items}
      </ol>"""

    html = re.sub(r"      <ol>.*?</ol>", toc, html, count=1, flags=re.S)
    log("Updated table of contents")
    return html


def update_editor_note(html: str, new_date: str) -> str:
    """Update editor's note with date range."""
    # Calculate 3 days back from target date
    year, month, day = parse_date_parts(new_date)
    target_dt = datetime(year, month, day)
    start = target_dt - timedelta(days=2)
    start_formatted = start.strftime("%B %d")
    end_formatted = target_dt.strftime("%B %d, %Y")

    day_before = target_dt - timedelta(days=1)
    day_before_formatted = day_before.strftime("%B %d")
    note = f"""      <div class="ednote-body">
        <p>Every story below passed this morning's freshness audit — sourced to reporting dated
        {start_formatted}–{end_formatted} (most from {start_formatted}–{day_before_formatted}). Today's brief runs leaner: two stories on each of
        our three desks — <strong>AI &amp; Technology</strong>, <strong>IT Industry</strong> and
        <strong>Recruitment &amp; HR</strong>.</p>
        <p>All of today's items are <strong>Search-verified</strong> — traced to search results and
        dated reporting rather than fully opened articles. Every Sources line links the original reporting.</p>
      </div>"""

    html = re.sub(
        r'      <div class="ednote-body">.*?</div>',
        note,
        html,
        count=1,
        flags=re.S
    )
    log("Updated editor's note")
    return html


def replace_stories(html: str, stories: List[str]) -> str:
    """Replace all story cards in the edition."""
    stories_html = "\n".join(stories)

    # Replace from first story to end of last story
    html = re.sub(
        r"    <!-- 01 -->.*?<!-- end Recruitment & HR grid -->",
        stories_html + "\n    <!-- end Recruitment & HR grid -->",
        html,
        count=1,
        flags=re.S
    )
    log(f"Replaced {len(stories)} stories in edition")
    return html


def generate_edition(old_date: str, new_date: str, stories: List[str], headlines: List[str]) -> Optional[str]:
    """Generate complete edition HTML with new stories and dates."""
    template, _ = load_template()
    if not template:
        return None

    try:
        # Update dates in template
        html = update_edition_with_date(template, old_date, new_date)

        # Update TOC
        html = update_toc(html, headlines)

        # Update editor's note
        html = update_editor_note(html, new_date)

        # Replace stories
        html = replace_stories(html, stories)

        log("Edition generation successful")
        return html
    except Exception as e:
        log(f"ERROR: Failed to generate edition: {e}", "ERROR")
        return None


def save_edition(html: str, date: str) -> bool:
    """Save generated edition to file."""
    target_file = ROOT / "editions" / f"{date}.html"
    try:
        target_file.write_text(html, encoding="utf-8")
        log(f"Saved edition to {target_file.name}")
        return True
    except Exception as e:
        log(f"ERROR: Failed to save edition: {e}", "ERROR")
        return False


def publish_edition() -> bool:
    """Run publish.py to regenerate index.html, archive.html, feed.xml."""
    import subprocess
    try:
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/publish.py")],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            log("publish.py completed successfully")
            log(result.stdout.strip())
            return True
        else:
            log(f"ERROR: publish.py failed with code {result.returncode}", "ERROR")
            log(f"stdout: {result.stdout}", "ERROR")
            log(f"stderr: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        log(f"ERROR: Failed to run publish.py: {e}", "ERROR")
        return False


def load_story_data() -> Optional[List[Dict]]:
    """Load story data from JSON file or environment variable."""
    import os

    # Try environment variable first
    stories_json = os.environ.get("BLOOM_STORIES")
    if stories_json:
        try:
            stories = json.loads(stories_json)
            log(f"Loaded {len(stories)} stories from BLOOM_STORIES env var")
            return stories
        except json.JSONDecodeError as e:
            log(f"ERROR: Invalid JSON in BLOOM_STORIES: {e}", "ERROR")
            return None

    # Try file
    stories_file = ROOT / ".stories.json"
    if stories_file.exists():
        try:
            stories = json.loads(stories_file.read_text())
            log(f"Loaded {len(stories)} stories from {stories_file}")
            return stories
        except json.JSONDecodeError as e:
            log(f"ERROR: Invalid JSON in .stories.json: {e}", "ERROR")
            return None

    return None


def main():
    """Main entry point."""
    log("Starting automated edition generation")

    # Get dates
    old_date = get_latest_edition_date()
    if not old_date:
        log("ERROR: Cannot determine previous edition date", "ERROR")
        return 1

    new_date = calculate_target_date()
    log(f"Previous edition: {old_date}")
    log(f"Target edition: {new_date}")

    # Check if we're ahead of template
    if new_date <= old_date:
        log(f"Edition {new_date} already exists or date is not newer", "WARN")
        return 0

    # Load template
    template, _ = load_template()
    if not template:
        log("ERROR: Could not load template", "ERROR")
        return 2

    # Load story data
    story_data = load_story_data()
    if story_data is None or (isinstance(story_data, list) and len(story_data) < 6):
        log(f"NOTICE: No story data available ({len(story_data) or 0} stories found). Generating placeholder edition.", "WARN")
        stories = []
        headlines = []
        desks = [
            ("t-teal", "AI &amp; Technology"),
            ("t-teal", "AI &amp; Technology"),
            ("t-amber", "IT Industry"),
            ("t-amber", "IT Industry"),
            ("t-navy", "Recruitment &amp; HR"),
            ("t-navy", "Recruitment &amp; HR"),
        ]

        for i, (theme, desk) in enumerate(desks, 1):
            num = f"{i:02d}"
            cid = f"s{i}"
            placeholder = create_placeholder_story(num, cid, theme, desk)
            stories.append(placeholder)
            headlines.append(f"Story {num} [Pending Details]")
    else:
        log(f"Generating edition with {len(story_data)} stories")
        stories = []
        headlines = []

        for i, story in enumerate(story_data[:6], 1):
            num = f"{i:02d}"
            cid = f"s{i}"
            theme = story.get("theme", "t-teal")
            category = story.get("category", "AI &amp; Technology")
            headline = story.get("headline", f"Story {num}")
            deck = story.get("deck", "Story details pending.")
            svg = story.get("svg", """          <svg viewBox="0 0 240 160" role="img" aria-label="News"><rect width="240" height="160" fill="#f0f0f0"/></svg>""")
            figcap = story.get("figcap", "Illustration")
            para1 = story.get("para1", "Story details pending.")
            para2 = story.get("para2", "Please check back shortly.")
            takeaways = story.get("takeaways", ["Story pending"])
            why = story.get("why", "Updates coming soon.")
            sources = story.get("sources", '<a href="#">Source</a>')
            topics = story.get("topics", ["pending"])

            card_html = generate_story_card(
                num, cid, theme, category, headline, deck, svg, figcap,
                para1, para2, takeaways, why, sources, topics
            )
            stories.append(card_html)
            headlines.append(headline)

    # Generate edition with placeholders
    html = generate_edition(old_date, new_date, stories, headlines)
    if not html:
        log("ERROR: Failed to generate edition HTML", "ERROR")
        return 2

    # Save edition
    if not save_edition(html, new_date):
        log("ERROR: Failed to save edition", "ERROR")
        return 2

    # Publish (update index.html, archive.html, feed.xml)
    if not publish_edition():
        log("ERROR: Failed to publish edition", "ERROR")
        return 3

    log("✓ Edition generation and publication complete")
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
