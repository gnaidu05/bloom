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
