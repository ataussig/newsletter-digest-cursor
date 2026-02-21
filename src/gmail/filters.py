"""
Heuristics to treat a message as a newsletter (and exclude non-newsletters).
"""

import re

# From-address substrings that suggest a newsletter
NEWSLETTER_FROM_PATTERNS = (
    "newsletter",
    "substack",
    "beehiiv",
    "ghost",
    "no-reply",
    "noreply",
    "digest",
    "daily",
    "weekly",
)

# Subject substrings that suggest newsletter content
NEWSLETTER_SUBJECT_PATTERNS = (
    "issue",
    "edition",
    "digest",
    "weekly",
    "daily",
    "roundup",
    "round-up",
)

# Subject / from patterns that suggest we should skip
EXCLUDE_SUBJECT_PATTERNS = (
    "security alert",
    "welcome to",
    "is live now",
    "verify your",
    "confirm your",
    "password reset",
    "unusual sign",
)
EXCLUDE_FROM_PATTERNS = (
    "noreply@google.com",  # security alerts
    "mailer-daemon",
)


def is_likely_newsletter(from_header: str, subject: str) -> bool:
    """
    Return True if the message looks like a newsletter.
    from_header and subject should be the raw header values.
    """
    from_lower = (from_header or "").lower()
    subject_lower = (subject or "").lower()

    for pattern in EXCLUDE_FROM_PATTERNS:
        if pattern in from_lower:
            return False
    for pattern in EXCLUDE_SUBJECT_PATTERNS:
        if pattern in subject_lower:
            return False

    from_ok = any(p in from_lower for p in NEWSLETTER_FROM_PATTERNS)
    subject_ok = any(p in subject_lower for p in NEWSLETTER_SUBJECT_PATTERNS)
    return from_ok or subject_ok
