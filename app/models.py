from dataclasses import dataclass, field
from typing import Any


@dataclass
class MuseumItem:
    title: str
    subtitle: str | None = None
    description: str | None = None
    category: str = "uncategorised"
    subcategory: str | None = None
    era: str | None = None
    region: str | None = None
    lat: float | None = None
    lon: float | None = None
    source_url: str | None = None
    image_url: str | None = None
    rarity: str | None = None
    mood: str | None = None
    template: str = "archive"
    theme: str = "candlelit"
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)


@dataclass
class Dataset:
    slug: str
    name: str
    category: str
    source_url: str | None = None
    enabled: bool = True
    version: str = "1"
