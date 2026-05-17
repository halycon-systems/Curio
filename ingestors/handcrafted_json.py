from pathlib import Path

from app.models import Dataset, MuseumItem
from app.settings import BASE_DIR, RAW_DIR
from ingestors.base import (
    BaseIngestor,
    as_list,
    normalize_item,
    read_json_file,
    slug_to_name,
)


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
                classification = raw.get("classification")
                if classification and not item.subcategory:
                    item.subcategory = str(classification)
                if self.path.stem == "superstitions":
                    item.metadata["display_label"] = "Folklore Fragment"
                    item.metadata["icon"] = superstition_icon(raw)
                items.append(item)
        return items


def handcrafted_slugs() -> set[str]:
    return {path.stem for path in handcrafted_paths()}


def discover() -> list[HandcraftedJsonIngestor]:
    by_slug: dict[str, Path] = {}
    for path in handcrafted_paths():
        by_slug[path.stem] = path
    return [HandcraftedJsonIngestor(path) for _, path in sorted(by_slug.items())]


def handcrafted_paths() -> list[Path]:
    paths: list[Path] = []
    for directory in (RAW_DIR / "handcrafted", BASE_DIR / "data" / "raw"):
        if directory.exists():
            paths.extend(directory.glob("*.json"))
    return paths


def superstition_icon(raw: dict) -> str:
    haystack = " ".join(
        [
            str(raw.get("title", "")),
            str(raw.get("classification", "")),
            " ".join(str(tag) for tag in raw.get("tags", [])),
        ]
    ).lower()

    if "cat" in haystack:
        icon = "black-cat.png"
    elif "mirror" in haystack:
        icon = "mirror.png"
    elif any(word in haystack for word in ("raven", "crow", "corvid", "magpie", "owl", "robin", "bird")):
        icon = "raven.png"
    elif any(word in haystack for word in ("death", "corpse", "mourning", "fetch", "black dog", "grave")):
        icon = "grim-reaper.png"
    elif any(word in haystack for word in ("witch", "fairy", "protection", "divination", "charm", "spirit", "spell")):
        icon = "spellbook.png"
    else:
        icon = "spell-book.png"

    return f"/media/category_art/Superstitions/{icon}"
