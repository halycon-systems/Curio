from pathlib import Path

from app.models import Dataset, MuseumItem
from app.settings import RAW_DIR
from ingestors.base import BaseIngestor, as_list, normalize_item, read_json_file, slug_to_name


DEFAULTS = {
    "obsolete_household_objects": {
        "category": "objects",
        "template": "archive",
        "theme": "candlelit",
        "mood": "curious",
    },
    "superstitions": {
        "category": "folklore",
        "template": "tale",
        "theme": "candlelit",
        "mood": "uncanny",
    },
    "weird_place_names": {
        "category": "places",
        "template": "archive",
        "theme": "velvet",
        "mood": "odd",
    },
}


class HandcraftedJsonIngestor(BaseIngestor):
    def __init__(self, path: Path):
        self.path = path
        slug = path.stem
        defaults = DEFAULTS.get(slug, {})
        self.default_category = defaults.get("category", slug)
        self.default_template = defaults.get("template", "archive")
        self.default_theme = defaults.get("theme", "candlelit")
        self.default_mood = defaults.get("mood")
        self.dataset = Dataset(
            slug=slug,
            name=slug_to_name(slug),
            category=self.default_category,
            source_url=str(path),
        )

    def load(self) -> list[MuseumItem]:
        payload = read_json_file(self.path)
        items: list[MuseumItem] = []
        for raw in as_list(payload):
            item = normalize_item(
                raw,
                default_category=self.default_category,
                default_template=self.default_template,
                default_theme=self.default_theme,
                default_mood=self.default_mood,
            )
            if item:
                items.append(item)
        return items


def discover() -> list[HandcraftedJsonIngestor]:
    directory = RAW_DIR / "handcrafted"
    if not directory.exists():
        return []
    return [HandcraftedJsonIngestor(path) for path in sorted(directory.glob("*.json"))]
