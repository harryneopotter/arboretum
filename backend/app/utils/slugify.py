"""
Utility functions.
"""

import re


def slugify(text: str) -> str:
    """
    Convert plant name or ID to URL-safe slug.

    Examples:
        "Chinese Evergreen (Aglaonema)" -> "chinese-evergreen-aglaonema"
        "plant:money_plant" -> "money-plant"
    """
    # Remove prefix if present
    if ":" in text:
        text = text.split(":", 1)[1]

    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[-\s]+", "-", text)
    text = text.strip("-")

    return text


def extract_plant_id_from_payload(payload: dict) -> str:
    """Extract plant_id from Qdrant payload."""
    return payload.get("plant_id", payload.get("id", ""))
