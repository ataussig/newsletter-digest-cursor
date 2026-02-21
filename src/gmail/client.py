"""
Gmail API wrapper: list messages (with pagination), get body, send, mark as read.
"""

import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Iterator

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from .auth import get_credentials


# Search query for unread in inbox; caller appends newer_than
DEFAULT_QUERY = "in:inbox is:unread"


def _get_service():
    creds = get_credentials()
    # Ensure we have a valid token (refresh if using refresh_token from env)
    if not creds.valid and creds.refresh_token:
        from google.auth.transport.requests import Request
        creds.refresh(Request())
    return build("gmail", "v1", credentials=creds)


def list_message_ids(service, query: str, max_results: int = 500) -> Iterator[str]:
    """Yield message IDs for the given query, paginating through all results."""
    # Only pass userId and q to avoid googleapiclient discovery casting bug (maxResults as int)
    request = service.users().messages().list(userId="me", q=query)
    while request is not None:
        response = request.execute()
        for msg in response.get("messages", []):
            yield msg["id"]
        request = service.users().messages().list_next(request, response)
        if request is None:
            break


def get_message(service, message_id: str) -> dict:
    """Get full message with payload (headers + body)."""
    return service.users().messages().get(userId="me", id=message_id, format="full").execute()


def get_body_from_message(msg: dict) -> str:
    """Extract plain or HTML body from Gmail message payload."""
    payload = msg.get("payload", {})
    body = ""
    if "body" in payload and payload["body"].get("data"):
        data = payload["body"]["data"]
        body = base64.urlsafe_b64decode(data).decode("utf-8", errors="replace")
    elif "parts" in payload:
        for part in payload["parts"]:
            mime = part.get("mimeType", "")
            if mime == "text/plain" and part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break
            if mime == "text/html" and part.get("body", {}).get("data"):
                body = base64.urlsafe_b64decode(part["body"]["data"]).decode("utf-8", errors="replace")
                break
    return body


def get_headers_from_message(msg: dict) -> dict:
    """Return dict of header name (lower) -> value."""
    payload = msg.get("payload", {})
    headers = payload.get("headers", [])
    return {h["name"].lower(): h["value"] for h in headers}


def mark_as_read(service, message_id: str) -> None:
    """Remove UNREAD label from the message."""
    try:
        service.users().messages().modify(
            userId="me",
            id=message_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
    except HttpError as e:
        # Log but don't fail the pipeline
        print(f"Warning: could not mark {message_id} as read: {e}")


def send_email(service, to: str, subject: str, html_body: str, from_email: str | None = None) -> dict:
    """
    Send an email. Uses the authenticated user as sender.
    Returns the sent message dict.
    """
    message = MIMEMultipart("alternative")
    message["To"] = to
    message["Subject"] = subject
    # Plain text fallback: strip tags roughly
    import re
    plain = re.sub(r"<[^>]+>", "", html_body)
    message.attach(MIMEText(plain, "plain"))
    message.attach(MIMEText(html_body, "html"))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()


def build_client():
    """Return a simple client object with the service and helpers."""
    service = _get_service()
    return type("GmailClient", (), {
        "service": service,
        "list_message_ids": lambda q, max_results=500: list_message_ids(service, q, max_results),
        "get_message": lambda mid: get_message(service, mid),
        "get_body": get_body_from_message,
        "get_headers": get_headers_from_message,
        "mark_as_read": lambda mid: mark_as_read(service, mid),
        "send_email": lambda to, subj, body: send_email(service, to, subj, body),
    })()
