"""
Configuration for the newsletter digest pipeline.
Reads from environment variables with defaults for local development.
"""

import os
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Gmail (set via env or GitHub Secrets)
LOOKBACK_DAYS = int(os.environ.get("LOOKBACK_DAYS", "7"))
DIGEST_RECIPIENT = os.environ.get("DIGEST_RECIPIENT", "ataussig@gmail.com")

# OAuth: use refresh token in CI; credentials.json + token.json for local
GMAIL_CLIENT_ID = os.environ.get("GMAIL_CLIENT_ID", "")
GMAIL_CLIENT_SECRET = os.environ.get("GMAIL_CLIENT_SECRET", "")
GMAIL_REFRESH_TOKEN = os.environ.get("GMAIL_REFRESH_TOKEN", "")
GMAIL_CREDENTIALS_PATH = os.environ.get("GMAIL_CREDENTIALS_PATH", str(PROJECT_ROOT / "credentials.json"))
GMAIL_TOKEN_PATH = os.environ.get("GMAIL_TOKEN_PATH", str(PROJECT_ROOT / "token.json"))

# Content limits
MAX_LINKS_PER_RUN = int(os.environ.get("MAX_LINKS_PER_RUN", "25"))
MIN_WORD_COUNT = int(os.environ.get("MIN_WORD_COUNT", "80"))

# MECE categories file (inferred by bootstrap or committed)
MECE_CATEGORIES_PATH = DATA_DIR / "mece-categories.json"

# Scopes for Gmail
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
]
