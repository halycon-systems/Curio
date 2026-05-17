import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from app.models import Dataset, MuseumItem


class BaseIngestor(ABC):
    dataset: Dataset

    @abstractmethod
    def load(self) -> list[MuseumItem]:
        raise NotImplementedError


def read_json_file(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def as_list(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        for key in ("items", "data", "records", "results"):
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return [payload]
    return []


def first_present(raw: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = raw.get(key)
        if value not in (None, ""):
            return value
    return None


def slug_to_name(slug: str) -> str:
    return slug.replace("_", " ").strip().title()


def normalize_tags(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    if isinstance(value, list):
        return [str(part).strip() for part in value if str(part).strip()]
    return [str(value).strip()]


def normalize_item(
    raw: dict[str, Any],
    default_category: str,
    default_template: str = "archive",
    default_theme: str = "candlelit",
    default_mood: str | None = None,
) -> MuseumItem | None:
    title = first_present(raw, "title", "name", "label", "site", "object")
    if not title:
        return None

    description = first_present(
        raw,
        "description",
        "summary",
        "text",
        "notes",
        "body",
        "details",
    )
    category = first_present(raw, "category", "type") or default_category
    metadata = {
        key: value
        for key, value in raw.items()
        if key
        not in {
            "title",
            "name",
            "label",
            "site",
            "object",
            "subtitle",
            "description",
            "summary",
            "text",
            "notes",
            "body",
            "details",
            "category",
            "type",
            "subcategory",
            "era",
            "period",
            "date",
            "region",
            "location",
            "lat",
            "latitude",
            "lon",
            "lng",
            "longitude",
            "source_url",
            "url",
            "image_url",
            "image",
            "rarity",
            "mood",
            "template",
            "theme",
            "tags",
        }
    }

    return MuseumItem(
        title=str(title),
        subtitle=first_present(raw, "subtitle"),
        description=description,
        category=str(category),
        subcategory=first_present(raw, "subcategory"),
        era=first_present(raw, "era", "period", "date"),
        region=first_present(raw, "region", "location"),
        lat=first_present(raw, "lat", "latitude"),
        lon=first_present(raw, "lon", "lng", "longitude"),
        source_url=first_present(raw, "source_url", "url"),
        image_url=first_present(raw, "image_url", "image"),
        rarity=first_present(raw, "rarity"),
        mood=first_present(raw, "mood") or default_mood,
        template=first_present(raw, "template") or default_template,
        theme=first_present(raw, "theme") or default_theme,
        metadata=metadata,
        tags=normalize_tags(raw.get("tags")),
    )
