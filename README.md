# Newsletter Digest

Automated daily digest: pull unread newsletters from a dedicated Gmail account, extract essays and follow linked articles, deduplicate and categorize with a MECE framework, then email a minimal HTML digest to your personal inbox.

Runs on **GitHub Actions** (free tier) on a daily schedule.

## Requirements

- Python 3.11+
- A Gmail account for newsletters (e.g. `ataussig.newsletters@gmail.com`)
- Google Cloud project with Gmail API enabled and OAuth 2.0 credentials

## One-time setup

### 1. Google Cloud

1. Create a project (or use existing) at [Google Cloud Console](https://console.cloud.google.com/).
2. Enable **Gmail API** (APIs & Services → Library → Gmail API).
3. Create **OAuth 2.0 credentials** (APIs & Services → Credentials → Create Credentials → OAuth client ID).
   - Application type: **Desktop app** (for local setup) or **Web application** (if you use a redirect URI for localhost).
4. Download the JSON and save as `credentials.json` in the project root (or note Client ID and Client Secret for GitHub Secrets).

### 2. Get a refresh token (local)

Run the OAuth helper once so you can store a refresh token for GitHub Actions:

```bash
pip install -r requirements.txt
python scripts/oauth_setup.py
```

This opens a browser; sign in with your **newsletter** Gmail account and approve. The script prints a **refresh token** — copy it.

### 3. GitHub Secrets

In your repo: Settings → Secrets and variables → Actions. Add:

| Secret | Description |
|--------|-------------|
| `GMAIL_CLIENT_ID` | OAuth 2.0 Client ID from Google Cloud |
| `GMAIL_CLIENT_SECRET` | OAuth 2.0 Client Secret |
| `GMAIL_REFRESH_TOKEN` | Refresh token from `oauth_setup.py` |
| `DIGEST_RECIPIENT` | Email that receives the digest (e.g. your personal Gmail) |

Optional (for LLM summarization / category inference):

- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`

### 4. Local development

Create a `.env` file (or export variables):

```bash
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
GMAIL_REFRESH_TOKEN=...
DIGEST_RECIPIENT=ataussig@gmail.com
```

Use `credentials.json` + `token.json` for local runs if you prefer file-based auth (see `scripts/oauth_setup.py`).

## Running

- **Daily:** The GitHub Action runs on schedule (see `.github/workflows/digest.yml`). No action needed.
- **Local:** `python -m src.run` (uses env or `credentials.json` + `token.json`).

## Project layout

```
newsletter-digest-cursor/
├── config.py           # Config and env
├── requirements.txt
├── src/
│   ├── run.py         # Pipeline entry point
│   ├── gmail/         # Gmail API client and auth
│   ├── extractors/    # Newsletter body and link extraction
│   ├── fetcher/       # Fetch and parse linked articles
│   ├── pipeline/      # Dedup, MECE, bootstrap
│   └── generator/     # HTML digest and send
├── data/
│   └── mece-categories.json   # Inferred or default MECE categories
├── output/            # Generated digest HTML (local)
└── scripts/
    └── oauth_setup.py # One-time OAuth → refresh token
```

## Configuration

See `config.py`. Key env vars:

- `LOOKBACK_DAYS` — How many days of unread mail to consider (default: 7).
- `MAX_LINKS_PER_RUN` — Cap on linked articles to fetch (default: 25).
- `DIGEST_RECIPIENT` — Where to send the digest.
