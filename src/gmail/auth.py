"""
Obtain Gmail API credentials from refresh token (CI) or token.json (local).
"""

from pathlib import Path

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

import config


def get_credentials():
    """
    Return Credentials for Gmail API.
    Prefers env vars (GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN)
    for CI; falls back to credentials.json + token.json for local.
    """
    # CI / GitHub Actions: use refresh token from env
    if config.GMAIL_REFRESH_TOKEN and config.GMAIL_CLIENT_ID and config.GMAIL_CLIENT_SECRET:
        return Credentials(
            token=None,
            refresh_token=config.GMAIL_REFRESH_TOKEN,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=config.GMAIL_CLIENT_ID,
            client_secret=config.GMAIL_CLIENT_SECRET,
            scopes=config.GMAIL_SCOPES,
        )

    # Local: use token.json (and refresh if needed)
    token_path = Path(config.GMAIL_TOKEN_PATH)
    credentials_path = Path(config.GMAIL_CREDENTIALS_PATH)

    if not token_path.exists():
        raise FileNotFoundError(
            "No Gmail credentials. Run: python scripts/oauth_setup.py\n"
            "Or set GMAIL_CLIENT_ID, GMAIL_CLIENT_SECRET, GMAIL_REFRESH_TOKEN."
        )

    creds = Credentials.from_authorized_user_file(str(token_path), config.GMAIL_SCOPES)

    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return creds
