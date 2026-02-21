"""
Load MECE categories from data/mece-categories.json and assign items to one category each.
Uses simple keyword matching per category definition/name; can be extended with LLM.
"""

import json
from pathlib import Path

import config


def load_categories() -> list[dict]:
    """Load category list from config path. Returns [{"name": str, "definition": str}, ...]."""
    path = Path(config.MECE_CATEGORIES_PATH)
    if not path.exists():
        return [
            {"name": "Other", "definition": "Items that do not fit other categories."},
        ]
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    return data.get("categories", data.get("items", []))


def _keywords_for_category(cat: dict) -> set[str]:
    name = (cat.get("name") or "").lower()
    definition = (cat.get("definition") or "").lower()
    # Use first 2-3 words of name and words from definition (min length 4)
    words = set()
    for part in name.replace("&", " ").split():
        if len(part) >= 2:
            words.add(part)
    for part in definition.replace(",", " ").replace(".", " ").split():
        if len(part) >= 4:
            words.add(part)
    return words


def assign_category(item: dict, categories: list[dict]) -> str:
    """
    Assign one category name to the item based on title/snippet text.
    Returns category name; falls back to "Other" if no match.
    """
    text = ((item.get("title") or "") + " " + (item.get("snippet") or "")).lower()
    if not text:
        return "Other"

    best = "Other"
    best_score = 0
    for cat in categories:
        if cat.get("name") == "Other":
            continue
        kw = _keywords_for_category(cat)
        score = sum(1 for w in kw if w in text)
        if score > best_score:
            best_score = score
            best = cat.get("name", "Other")

    return best


def categorize_items(items: list[dict], categories: list[dict] | None = None) -> list[dict]:
    """Add "category" key to each item. Returns new list (items are shallow copies)."""
    if categories is None:
        categories = load_categories()
    out = []
    for it in items:
        copy = dict(it)
        copy["category"] = assign_category(it, categories)
        out.append(copy)
    return out
