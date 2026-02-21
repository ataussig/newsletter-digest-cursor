"""
In-memory deduplication: merge items that refer to the same story (same URL or very similar title).
"""

import re
from collections import defaultdict


def normalize_title(s: str) -> str:
    """Lowercase, collapse whitespace, remove punctuation for comparison."""
    if not s:
        return ""
    s = re.sub(r"[^\w\s]", " ", s.lower())
    return " ".join(s.split())[:100]


def normalize_url(url: str) -> str:
    """Strip query and fragment for dedup."""
    if not url:
        return ""
    return url.split("?")[0].split("#")[0].rstrip("/")


def merge_items(items: list[dict]) -> list[dict]:
    """
    Take a list of items (each with url, title, newsletter_name, snippet, etc.)
    and merge duplicates: same normalized URL or same normalized title.
    Merged item keeps one url/title, concatenates newsletter_name and sources.
    Items without URL (e.g. newsletter body) are kept as-is.
    """
    with_url = [it for it in items if normalize_url(it.get("url") or "")]
    without_url = [it for it in items if not normalize_url(it.get("url") or "")]

    by_url: dict[str, list[dict]] = defaultdict(list)
    for it in with_url:
        nurl = normalize_url(it.get("url") or "")
        if nurl:
            by_url[nurl].append(it)

    result: list[dict] = []
    for nurl, group in by_url.items():
        if len(group) == 1:
            result.append(_single_to_merged(group[0]))
        else:
            result.append(_merge_group(group))

    for it in without_url:
        result.append(_single_to_merged(it))

    return result


def _single_to_merged(it: dict) -> dict:
    newsletters = it.get("newsletter_names") or [it.get("newsletter_name") or it.get("newsletter") or "Unknown"]
    if isinstance(newsletters, str):
        newsletters = [newsletters]
    return {
        "url": it.get("url"),
        "title": it.get("title") or it.get("snippet", "")[:200],
        "snippet": it.get("snippet") or it.get("text", "")[:500],
        "newsletter_names": newsletters,
        "message_ids": [it.get("message_id")] if it.get("message_id") else [],
    }


def _merge_group(group: list[dict]) -> dict:
    first = group[0]
    collected = []
    for x in group:
        names = x.get("newsletter_names")
        if isinstance(names, list):
            collected.extend(names)
        else:
            collected.append(x.get("newsletter_name") or x.get("newsletter") or "Unknown")
    newsletters = list(dict.fromkeys(collected))
    message_ids = list({x.get("message_id") for x in group if x.get("message_id")})
    return {
        "url": first.get("url"),
        "title": first.get("title") or first.get("snippet", "")[:200],
        "snippet": first.get("snippet") or first.get("text", "")[:500],
        "newsletter_names": newsletters,
        "message_ids": message_ids,
    }
