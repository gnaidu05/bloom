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

Subscribers are BCC'd. Subscription requests arrive by email (the site's Subscribe form opens a
pre-filled email); add each new address to the `SUBSCRIBERS` secret. Until the secrets are set,
the workflow exits green with a notice and sends nothing.
