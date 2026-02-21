"""
Build the digest HTML (email-safe: inline styles) and return as string.
"""

from datetime import date
from html import escape


def build_digest_html(
    items_by_category: dict[str, list[dict]],
    digest_date: date | None = None,
    total_newsletters: int = 0,
    total_messages: int = 0,
) -> str:
    """
    items_by_category: { "Category Name": [ {"title", "url", "snippet", "newsletter_names", "message_ids"}, ... ], ... }
    """
    d = digest_date or date.today()
    date_str = d.strftime("%B %d, %Y")
    title = f"Newsletter Digest — {d.strftime('%Y-%m-%d')}"

    # Section order: put "Other" last
    categories = list(items_by_category.keys())
    if "Other" in categories:
        categories.remove("Other")
        categories.append("Other")

    parts = [
        "<!DOCTYPE html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="UTF-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1.0">',
        f"<title>{escape(title)}</title>",
        "</head>",
        "<body style=\"font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; color: #333; background: #fff;\">",
        "<h1 style=\"font-size: 2em; margin-bottom: 0.2em; border-bottom: 2px solid #000; padding-bottom: 10px;\">Newsletter Digest</h1>",
        f"<p style=\"color: #666; font-style: italic; margin-bottom: 2em;\">{escape(date_str)}</p>",
    ]

    for cat in categories:
        items = items_by_category.get(cat, [])
        if not items:
            continue
        parts.append(f"<h2 style=\"font-size: 1.5em; margin-top: 2em; margin-bottom: 0.5em; color: #000;\">{escape(cat)}</h2>")
        for it in items:
            title_text = it.get("title") or "Untitled"
            url = it.get("url") or "#"
            snippet = (it.get("snippet") or "")[:400]
            newsletters = it.get("newsletter_names") or []
            sources_str = ", ".join(escape(n) for n in newsletters)
            parts.append("<div style=\"margin-bottom: 1.5em; padding-bottom: 1em; border-bottom: 1px solid #eee;\">")
            parts.append(f"<h3 style=\"font-size: 1.2em; margin-top: 0; margin-bottom: 0.3em;\"><a href=\"{escape(url)}\" style=\"color: #0066cc; text-decoration: none;\">{escape(title_text)}</a></h3>")
            parts.append(f"<p style=\"font-size: 0.9em; color: #666; font-style: italic; margin: 0.3em 0;\">Sources: {sources_str}</p>")
            if snippet:
                parts.append(f"<p style=\"margin: 0.5em 0;\">{escape(snippet)}</p>")
            parts.append("</div>")

    parts.append("<div style=\"font-size: 0.85em; color: #999; margin-top: 3em; padding-top: 1em; border-top: 2px solid #eee;\">")
    parts.append(f"<p><strong>Newsletters processed:</strong> {total_newsletters}</p>")
    parts.append(f"<p><strong>Messages examined:</strong> {total_messages}</p>")
    parts.append("</div>")
    parts.append("</body>")
    parts.append("</html>")

    return "\n".join(parts)
