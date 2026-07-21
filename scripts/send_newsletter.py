#!/usr/bin/env python3
"""Email the latest Morning Bloom edition to subscribers.

Runs in GitHub Actions after each push that touches editions/.
Sends only when the newest edition is dated today (Asia/Kolkata), so
style-only re-publishes of an old edition never re-mail anyone.

Requires repo Actions secrets:
  MAIL_USERNAME      Gmail address to send from
  MAIL_APP_PASSWORD  Gmail App Password (Google Account -> Security -> App passwords)

Subscriber list — either or both of:
  SUBSCRIBERS        Recipient emails, separated by commas/spaces/newlines (manual)
  SUPABASE_URL + SUPABASE_SERVICE_KEY
                     Supabase project URL + service_role key; the live list of
                     web signups is read from the `subscribers` table and merged
                     with SUBSCRIBERS. The service key bypasses RLS (full read);
                     it is secret and must never appear in the website.

If mail creds or all subscriber sources are missing, exits 0 with a notice.
"""
import json
import os
import re
import smtplib
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://gnaidu05.github.io/bloom"
IST = timezone(timedelta(hours=5, minutes=30))


def supabase_subscribers() -> list:
    """Fetch the live signup list from the Supabase `subscribers` table (if configured)."""
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    if not (url and key):
        return []
    req = urllib.request.Request(
        url + "/rest/v1/subscribers?select=email&order=created_at.asc",
        headers={"apikey": key, "Authorization": "Bearer " + key},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as ex:  # network/config hiccup shouldn't break the send
        print(f"NOTICE: could not read Supabase subscribers ({ex}); using SUBSCRIBERS secret only.")
        return []
    if not isinstance(rows, list):
        print(f"NOTICE: unexpected Supabase response ({rows}); using SUBSCRIBERS secret only.")
        return []
    return [r["email"].strip() for r in rows
            if isinstance(r, dict) and "@" in str(r.get("email", ""))]


def main() -> None:
    user = os.environ.get("MAIL_USERNAME", "").strip()
    # Google displays App Passwords with spaces ("xxxx xxxx xxxx xxxx"); strip them.
    password = re.sub(r"\s+", "", os.environ.get("MAIL_APP_PASSWORD", ""))
    if not (user and password):
        print("NOTICE: MAIL_USERNAME / MAIL_APP_PASSWORD not set; skipping send.")
        return

    raw_subs = os.environ.get("SUBSCRIBERS", "").strip()
    manual = [s for s in re.split(r"[,\s;]+", raw_subs) if "@" in s]
    # Merge manual list + live web signups, de-duplicated case-insensitively.
    seen, subscribers = set(), []
    for addr in manual + supabase_subscribers():
        key = addr.lower()
        if key not in seen:
            seen.add(key)
            subscribers.append(addr)
    if not subscribers:
        print("NOTICE: no subscribers (SUBSCRIBERS secret empty and Supabase returned none); skipping send.")
        return

    editions = sorted((ROOT / "editions").glob("????-??-??.html"), reverse=True)
    if not editions:
        print("NOTICE: no editions found; skipping send.")
        return
    latest = editions[0]

    today = datetime.now(IST).strftime("%Y-%m-%d")
    if latest.stem != today:
        print(f"NOTICE: latest edition {latest.stem} is not today's ({today}); skipping send.")
        return

    d = datetime.strptime(latest.stem, "%Y-%m-%d")
    pretty = d.strftime("%A, %B %d, %Y").replace(" 0", " ")
    url = f"{SITE}/editions/{latest.name}"

    html = latest.read_text(encoding="utf-8")
    m = re.search(r"Inside this issue</div>\s*<ol>(.*?)</ol>", html, re.S)
    heads = re.findall(r"<li>(.*?)</li>", m.group(1), re.S) if m else []
    heads = [re.sub(r"<[^>]+>", "", h).strip().replace("&amp;", "&") for h in heads]

    items_html = "".join(
        f'<tr><td style="padding:6px 0 6px 14px;border-left:3px solid #c14066;'
        f'font:600 15px/1.5 Arial,sans-serif;color:#18181b;">{i + 1:02d}&nbsp;&nbsp;{h}</td></tr>'
        f'<tr><td style="height:8px;"></td></tr>'
        for i, h in enumerate(heads)
    )
    body_html = f"""\
<div style="background:#fafafa;padding:28px 14px;">
  <div style="max-width:600px;margin:0 auto;background:#ffffff;border-radius:14px;overflow:hidden;border:1px solid #e4e4e7;">
    <div style="background:#1d3557;padding:26px 28px;">
      <div style="font:700 13px/1 Arial,sans-serif;color:#a9bacd;letter-spacing:2px;text-transform:uppercase;">Daily News Briefing</div>
      <div style="font:700 30px/1.15 Georgia,serif;color:#ffffff;margin-top:10px;">The Morning <span style="color:#f2a9c4;font-style:italic;">Bloom</span></div>
      <div style="font:400 14px/1.4 Arial,sans-serif;color:#a9bacd;margin-top:8px;">{pretty} &middot; Pune Edition</div>
    </div>
    <div style="padding:26px 28px;">
      <div style="font:700 12px/1 Arial,sans-serif;color:#8f5606;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;">Inside this issue</div>
      <table role="presentation" cellpadding="0" cellspacing="0" style="width:100%;">{items_html}</table>
      <div style="text-align:center;margin:22px 0 6px;">
        <a href="{url}" style="display:inline-block;background:#c14066;color:#ffffff;text-decoration:none;font:700 15px/1 Arial,sans-serif;padding:14px 30px;border-radius:999px;">Read today's edition &rarr;</a>
      </div>
    </div>
    <div style="background:#14263f;padding:16px 28px;font:400 12px/1.6 Arial,sans-serif;color:#8298af;text-align:center;">
      Summaries are Claude's own words; links carry the full reporting.<br>
      <a href="{SITE}/archive.html" style="color:#8fd0e2;">Archive</a> &middot;
      To unsubscribe, reply to this email with "unsubscribe".<br>
      <span style="color:#6c7f95;">You received this email because you signed up on our website or made a purchase from us.</span>
    </div>
  </div>
</div>"""
    body_text = (
        f"The Morning Bloom — {pretty} (Pune Edition)\n\nInside this issue:\n"
        + "\n".join(f"  {i + 1:02d}. {h}" for i, h in enumerate(heads))
        + f"\n\nRead today's edition: {url}\nArchive: {SITE}/archive.html\n"
        "To unsubscribe, reply with \"unsubscribe\".\n\n"
        "You received this email because you signed up on our website or made a purchase from us."
    )

    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"The Morning Bloom — {pretty}"
    msg["From"] = f"The Morning Bloom <{user}>"
    msg["To"] = user
    msg.attach(MIMEText(body_text, "plain", "utf-8"))
    msg.attach(MIMEText(body_html, "html", "utf-8"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(user, password)
        smtp.sendmail(user, [user] + subscribers, msg.as_string())
    print(f"Sent {latest.name} to {len(subscribers)} subscriber(s) (BCC).")


if __name__ == "__main__":
    try:
        main()
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Gmail rejected the login — check MAIL_USERNAME and MAIL_APP_PASSWORD "
              "(must be an App Password, not the normal account password).")
        sys.exit(1)
