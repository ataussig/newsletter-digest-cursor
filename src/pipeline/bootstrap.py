"""
Bootstrap: ensure data/mece-categories.json exists.
When LLM is available, can infer categories from a sample of newsletter content;
for now we only ensure the file exists (use default from repo).
"""

import json
from pathlib import Path

import config


def ensure_categories_file() -> Path:
    """If MECE categories file is missing, write default. Return path."""
    path = Path(config.MECE_CATEGORIES_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        default = [
            {"name": "Technology & AI", "definition": "Products, models, tools, platforms, software, hardware."},
            {"name": "Business & Finance", "definition": "Markets, investing, startups, corporate strategy, economics."},
            {"name": "Politics & Policy", "definition": "Government, regulation, elections, legislation, diplomacy."},
            {"name": "Science & Health", "definition": "Research, discoveries, medicine, climate, environment."},
            {"name": "Culture & Society", "definition": "Media, trends, ideas, arts, education, consumer behavior."},
            {"name": "Other", "definition": "Items that do not fit the above categories."},
        ]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, indent=2)
    return path
