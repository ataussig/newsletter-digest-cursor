"""
Newsletter digest pipeline: fetch unread newsletters, extract content, dedupe, categorize, build HTML, send email.
"""

from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

import config
from src.gmail.client import build_client
from src.gmail.filters import is_likely_newsletter
from src.extractors.newsletter import extract_body, extract_links
from src.fetcher.article import fetch_and_extract
from src.pipeline.bootstrap import ensure_categories_file
from src.pipeline.categories import load_categories, categorize_items
from src.pipeline.dedup import merge_items
from src.generator.digest import build_digest_html


def run(backfill_days: int | None = None, send: bool = True, mark_read: bool = True) -> str:
    """
    Run the full pipeline. Returns path to saved HTML file.
    If backfill_days is set, use that instead of config.LOOKBACK_DAYS.
    If send is False, skip email. If mark_read is False, don't mark messages as read.
    """
    ensure_categories_file()
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    lookback = backfill_days if backfill_days is not None else config.LOOKBACK_DAYS
    query = f"in:inbox is:unread newer_than:{lookback}d"

    client = build_client()
    message_ids = list(client.list_message_ids(query))
    if not message_ids:
        print("No unread messages in lookback window.")
        return ""

    newsletters = []
    all_links: list[dict] = []
    link_to_newsletters: dict[str, list[str]] = defaultdict(list)

    for mid in message_ids:
        msg = client.get_message(mid)
        headers = client.get_headers(msg)
        from_h = headers.get("from", "")
        subject = headers.get("subject", "")
        if not is_likely_newsletter(from_h, subject):
            continue
        body_html = client.get_body(msg)
        if not body_html.strip():
            continue
        body_text = extract_body(body_html)
        if len(body_text.split()) < config.MIN_WORD_COUNT:
            continue
        links = extract_links(body_html)
        newsletter_name = from_h.split("<")[0].strip() or from_h[:50]
        newsletters.append({
            "message_id": mid,
            "newsletter_name": newsletter_name,
            "subject": subject,
            "body_text": body_text,
            "links": links,
        })
        for lnk in links:
            url = lnk.get("url", "")
            if url:
                link_to_newsletters[url].append(newsletter_name)

    # Build items from newsletter bodies (one item per newsletter)
    items = []
    for n in newsletters:
        items.append({
            "title": n["subject"],
            "url": "",
            "snippet": n["body_text"][:500],
            "newsletter_name": n["newsletter_name"],
            "newsletter_names": [n["newsletter_name"]],
            "message_id": n["message_id"],
        })

    # Collect unique links and fetch (up to MAX_LINKS_PER_RUN)
    seen_url = set()
    to_fetch = []
    for n in newsletters:
        for lnk in n["links"]:
            u = lnk.get("url", "").strip()
            if not u or u in seen_url:
                continue
            seen_url.add(u)
            to_fetch.append((u, lnk.get("text") or ""))
            if len(to_fetch) >= config.MAX_LINKS_PER_RUN:
                break
        if len(to_fetch) >= config.MAX_LINKS_PER_RUN:
            break

    for url, _ in to_fetch:
        result = fetch_and_extract(url)
        if result.get("error"):
            continue
        names = link_to_newsletters.get(url, [])
        items.append({
            "title": result.get("title") or url,
            "url": url,
            "snippet": result.get("snippet", ""),
            "newsletter_name": names[0] if names else "Unknown",
            "newsletter_names": names,
        })

    if not items:
        print("No content to digest.")
        return ""

    merged = merge_items(items)
    categories = load_categories()
    categorized = categorize_items(merged, categories)

    by_category = defaultdict(list)
    for it in categorized:
        by_category[it["category"]].append(it)

    digest_date = date.today()
    html = build_digest_html(
        dict(by_category),
        digest_date=digest_date,
        total_newsletters=len(newsletters),
        total_messages=len(message_ids),
    )

    out_path = config.OUTPUT_DIR / f"newsletter-digest-{digest_date.isoformat()}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path}")

    if send and config.DIGEST_RECIPIENT:
        client.send_email(
            config.DIGEST_RECIPIENT,
            f"Newsletter Digest — {digest_date.isoformat()}",
            html,
        )
        print(f"Sent digest to {config.DIGEST_RECIPIENT}")

    if mark_read:
        for n in newsletters:
            client.mark_as_read(n["message_id"])
        print("Marked newsletters as read.")

    return str(out_path)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--backfill", type=int, default=None, help="Use N days lookback instead of config")
    p.add_argument("--no-send", action="store_true", help="Do not send email")
    p.add_argument("--no-mark-read", action="store_true", help="Do not mark messages as read")
    args = p.parse_args()
    run(backfill_days=args.backfill, send=not args.no_send, mark_read=not args.no_mark_read)
