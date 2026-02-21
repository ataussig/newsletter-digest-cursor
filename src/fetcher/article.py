"""
Fetch a URL and extract main article content (title, text) using readability.
"""

import re
import time
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

try:
    from readability import Document
    HAS_READABILITY = True
except ImportError:
    HAS_READABILITY = False

# User-Agent to avoid some blocks
USER_AGENT = "Mozilla/5.0 (compatible; NewsletterDigest/1.0; +https://github.com/newsletter-digest)"
REQUEST_TIMEOUT = 15
# Rate limit: pause between requests (seconds)
REQUEST_DELAY = 0.5


def fetch_url(url: str) -> tuple[int, str, str]:
    """
    GET url; return (status_code, content_type, body).
    On error returns (0, "", "") or (status_code, "", "").
    """
    try:
        r = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={"User-Agent": USER_AGENT},
            allow_redirects=True,
        )
        ct = r.headers.get("Content-Type", "")
        if "text/html" not in ct and "application/xhtml" not in ct:
            return (r.status_code, ct, "")
        return (r.status_code, ct, r.text)
    except requests.RequestException as e:
        return (0, "", str(e))


def extract_article(html: str, url: str) -> dict:
    """
    Extract title and main text from HTML.
    Returns {"title": str, "text": str, "snippet": str} (snippet = first ~300 chars of text).
    """
    soup = BeautifulSoup(html, "html.parser")

    title = ""
    text = ""

    if HAS_READABILITY:
        try:
            doc = Document(html)
            title = doc.title() or ""
            text = doc.summary()
            soup = BeautifulSoup(text, "html.parser")
            text = soup.get_text(separator="\n", strip=True)
        except Exception:
            pass

    if not text:
        # Fallback: get body, remove script/style
        for tag in soup.find_all(["script", "style", "nav", "footer", "aside"]):
            tag.decompose()
        body = soup.find("body") or soup
        text = body.get_text(separator="\n", strip=True)

    if not title:
        t = soup.find("title")
        title = (t.get_text() if t else "").strip() or urlparse(url).path or url

    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    snippet = (text[:500] + "…") if len(text) > 500 else text

    return {"title": title[:300], "text": text, "snippet": snippet}


def fetch_and_extract(url: str, delay: bool = True) -> dict:
    """
    Fetch URL and extract article content.
    Returns dict with keys: url, title, text, snippet, error (if any), status_code.
    """
    if delay:
        time.sleep(REQUEST_DELAY)
    status, _, body = fetch_url(url)
    if status != 200 or not body:
        return {
            "url": url,
            "title": "",
            "text": "",
            "snippet": "",
            "error": f"HTTP {status}" if status else "Request failed",
            "status_code": status,
        }
    extracted = extract_article(body, url)
    return {
        "url": url,
        "title": extracted["title"],
        "text": extracted["text"],
        "snippet": extracted["snippet"],
        "error": None,
        "status_code": status,
    }
