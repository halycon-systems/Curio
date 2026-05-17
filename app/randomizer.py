import random
from typing import Any

from app.settings import RECENT_WINDOW


def choose_item(
    items: list[dict[str, Any]],
    recent_item_ids: list[int] | None = None,
    recent_categories: list[str] | None = None,
    recent_subcategories: list[str] | None = None,
    recent_moods: list[str] | None = None,
    disable_smart_random: bool = False,
) -> dict[str, Any] | None:
    if not items:
        return None

    if disable_smart_random:
        return random.choice(items)

    recent_item_ids = (recent_item_ids or [])[-RECENT_WINDOW:]
    recent_categories = (recent_categories or [])[-RECENT_WINDOW:]
    recent_subcategories = (recent_subcategories or [])[-RECENT_WINDOW:]
    recent_moods = (recent_moods or [])[-RECENT_WINDOW:]
    most_recent_category = recent_categories[-1] if recent_categories else None
    most_recent_subcategory = recent_subcategories[-1] if recent_subcategories else None

    candidates = [item for item in items if item["id"] not in recent_item_ids]
    if not candidates:
        candidates = items

    category_filtered = [
        item for item in candidates if item.get("category") != most_recent_category
    ]
    if category_filtered:
        candidates = category_filtered

    subcategory_filtered = [
        item for item in candidates if item.get("subcategory") != most_recent_subcategory
    ]
    if subcategory_filtered:
        candidates = subcategory_filtered

    weighted: list[dict[str, Any]] = []
    for item in candidates:
        weight = 6
        if item.get("category") in recent_categories:
            weight -= 2
        if item.get("mood") in recent_moods:
            weight -= 1
        if item.get("subcategory") and item.get("subcategory") in recent_subcategories:
            weight -= 1
        weight = max(weight, 1)
        weighted.extend([item] * weight)

    return random.choice(weighted)


def parse_csv(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def parse_int_csv(value: str | None) -> list[int]:
    parsed: list[int] = []
    for part in parse_csv(value):
        try:
            parsed.append(int(part))
        except ValueError:
            continue
    return parsed
