# The Morning Bloom

Gopi's daily news briefing — AI & Technology · Books & Publishing · Recruitment & HR — styled as a morning newspaper. Pune Edition.

**Live site:** https://gnaidu05.github.io/bloom/

## How it works

- `editions/YYYY-MM-DD.html` — one self-contained page per day's briefing.
- `index.html` — always a copy of the latest edition (the front page).
- `archive.html` — date-wise list of every past edition.
- `scripts/publish.py` — promotes the newest edition to `index.html` and rebuilds `archive.html`. Run after adding a new edition:

  ```
  python3 scripts/publish.py
  ```

- `.github/workflows/pages.yml` — deploys the site to GitHub Pages on every push.

## Daily publishing flow

Each morning, a scheduled Claude session searches the day's news, writes `editions/<today>.html` (matching the structure and style of the latest existing edition), runs `scripts/publish.py`, and pushes. The previous front page automatically becomes part of the archive.

## Newsletter email (automated)

`scripts/publish.py` also writes `feed.xml` (RSS). On every push that changes `editions/`, the
`send-newsletter.yml` workflow runs `scripts/send_newsletter.py`, which emails the day's edition
(headlines digest + link) to subscribers via Gmail — but only when the newest edition is dated
today in IST, so re-publishes never re-send.

One-time setup (repo **Settings → Secrets and variables → Actions**):

| Secret | Value |
|---|---|
| `MAIL_USERNAME` | The Gmail address to send from |
| `MAIL_APP_PASSWORD` | A Gmail **App Password** (Google Account → Security → 2-Step Verification → App passwords) |
| `SUBSCRIBERS` | Recipient emails, separated by commas or newlines |

Subscribers are BCC'd. The recipient list is the union of the `SUBSCRIBERS` secret (manual) and
the live web-signup list (automatic, see below), de-duplicated. Until the mail secrets are set,
the workflow exits green with a notice and sends nothing.

### Auto-updating subscriber list (optional)

`newsletter/subscribe.gs` is a Google Apps Script that turns a Google Sheet into the live list:
the site's Subscribe form POSTs each new email to the script (a row is appended, deduped), and
the send workflow fetches the list back (token-protected) each morning. Setup steps are in the
header comment of `newsletter/subscribe.gs`. After deploying it, add two more Actions secrets:

| Secret | Value |
|---|---|
| `SUBSCRIBE_ENDPOINT` | The Apps Script **Web app URL** |
| `SUBSCRIBE_TOKEN` | The same `TOKEN` string set inside the script |

Then set `SUBSCRIBE_ENDPOINT` (the same URL) as the `SUBSCRIBE_ENDPOINT` constant in the site's
inline script so the form auto-submits instead of opening an email. Web signups then flow into the
Sheet with no manual step; open the Sheet anytime to see the count and every subscriber.
