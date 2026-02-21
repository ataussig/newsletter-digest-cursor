"""
Extract main body text and content links from newsletter HTML.
Excludes sponsor/unsubscribe/social links.
"""

import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

# Link href substrings to skip (sponsor, unsubscribe, social, tracking)
SKIP_LINK_PATTERNS = (
    "unsubscribe",
    "view in browser",
    "preferences",
    "twitter.com",
    "x.com",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "sponsored",
    "advertisement",
    "partner content",
    "brought to you by",
    "mailto:",
    "#",
)
# If the link text or surrounding context suggests sponsor, skip
SKIP_TEXT_PATTERNS = (
    "unsubscribe",
    "sponsored",
    "advertisement",
    "partner content",
)


def extract_body(html: str) -> str:
    """
    Get main body text from newsletter HTML.
    Prefer text from article/main content; strip nav, footer, unsubscribe blocks.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove script, style, nav, footer
    for tag in soup.find_all(["script", "style", "nav", "footer"]):
        tag.decompose()

    # Common newsletter containers
    for selector in ["article", "[role='main']", ".post", ".content", ".newsletter-body", "main"]:
        el = soup.select_one(selector)
        if el:
            return _get_text(el)

    # Fallback: body without first/last big blocks (often header/footer)
    body = soup.find("body")
    if body:
        return _get_text(body)
    return _get_text(soup)


def _get_text(el) -> str:
    text = el.get_text(separator="\n", strip=True)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def extract_links(html: str, base_url: str = "https://example.com/") -> list[dict]:
    """
    Extract content links from newsletter HTML.
    Returns list of {"url": str, "text": str, "context": str} for links
    that look like article/source links (not sponsor, unsubscribe, social).
    """
    soup = BeautifulSoup(html, "html.parser")
    seen_urls = set()
    out = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or href.startswith("#") or href.startswith("mailto:"):
            continue

        url = urljoin(base_url, href)
        parsed = urlparse(url)
        if not parsed.scheme in ("http", "https"):
            continue

        url_lower = url.lower()
        if any(p in url_lower for p in SKIP_LINK_PATTERNS):
            continue

        link_text = (a.get_text() or "").strip()[:200]
        if any(p in link_text.lower() for p in SKIP_TEXT_PATTERNS):
            continue

        # Context: surrounding paragraph or parent text
        context = ""
        parent = a.find_parent(["p", "li", "td", "div"])
        if parent:
            context = (parent.get_text() or "").strip()[:500]

        if any(p in context.lower() for p in SKIP_TEXT_PATTERNS):
            continue

        norm = url.split("?")[0].rstrip("/")
        if norm in seen_urls:
            continue
        seen_urls.add(norm)

        out.append({"url": url, "text": link_text, "context": context})

    return out
