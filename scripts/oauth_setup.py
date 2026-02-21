#!/usr/bin/env python3
"""
One-time OAuth flow for the newsletter Gmail account.
Run locally; sign in with the account that receives newsletters.
Prints the refresh token to store in GitHub Secrets (GMAIL_REFRESH_TOKEN).
"""

import json
import sys
from pathlib import Path

# Add project root
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

import config

def main():
    creds = None
    token_path = Path(config.GMAIL_TOKEN_PATH)
    credentials_path = Path(config.GMAIL_CREDENTIALS_PATH)

    if not credentials_path.exists():
        print(f"Missing {credentials_path}")
        print("Download OAuth 2.0 credentials from Google Cloud Console (Desktop app)")
        print("and save as credentials.json in the project root.")
        sys.exit(1)

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), config.GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), config.GMAIL_SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as f:
            f.write(creds.to_json())

    # Print refresh token for GitHub Secrets
    if creds.refresh_token:
        print("\n--- Store this in GitHub Secrets as GMAIL_REFRESH_TOKEN ---\n")
        print(creds.refresh_token)
        print("\n---\n")
    else:
        print("No refresh_token in credentials. Delete token.json and run again to re-consent.")

if __name__ == "__main__":
    main()
