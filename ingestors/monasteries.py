from pathlib import Path

from app.models import Dataset, MuseumItem
from app.settings import BASE_DIR, RAW_DIR
from ingestors.base import BaseIngestor, as_list, normalize_item, read_json_file
from ingestors.xlsx import clean_text, read_xlsx_tables


class MonasteriesIngestor(BaseIngestor):
    def __init__(self, path: Path | None = None):
        self.path = path
        self.json_path = RAW_DIR / "downloaded" / "monasteries.json"
        self.xlsx_path = (
            BASE_DIR / "data" / "raw" / "Monistaries" / "Monistary2.xlsx"
        )
        self.dataset = Dataset(
            slug="monasteries",
            name="Historical Monasteries",
            category="sacred_history",
            source_url=str(path or self.xlsx_path),
        )

    def load(self) -> list[MuseumItem]:
        if self.path:
            if self.path.suffix.lower() == ".xlsx":
                return self._load_xlsx(self.path)
            return self._load_json(self.path)
        if self.xlsx_path.exists():
            return self._load_xlsx(self.xlsx_path)
        if self.json_path.exists():
            return self._load_json(self.json_path)
        return []

    def _load_json(self, path: Path) -> list[MuseumItem]:
        payload = read_json_file(path)
        items: list[MuseumItem] = []
        for raw in as_list(payload):
            item = normalize_item(
                raw,
                default_category="sacred_history",
                default_template="archive",
                default_theme="candlelit",
                default_mood="reverent",
            )
            if item:
                if not item.subcategory:
                    item.subcategory = "monastery"
                items.append(item)
        return items

    def _load_xlsx(self, path: Path) -> list[MuseumItem]:
        self.source_path = path
        tables = read_xlsx_tables(path, required_field="Monastery")
        items: list[MuseumItem] = []
        for order, rows in tables.items():
            for raw in rows:
                item = self._row_to_item(order, raw)
                if item:
                    items.append(item)
        return items

    def _row_to_item(self, order: str, raw: dict[str, str]) -> MuseumItem | None:
        name = _tidy_name(clean_text(raw.get("Monastery")))
        if not name:
            return None
        order_name = ORDER_NAMES.get(order, order.rstrip("s"))

        city = _tidy_name(clean_text(raw.get("City")))
        country = clean_text(raw.get("Country"))
        historical_region = clean_text(raw.get("Historical Region"))
        administrative_region = clean_text(raw.get("Administrative Region"))
        starting = _clean_year(raw.get("Starting"))
        ending = _clean_year(raw.get("Ending"))

        place = ", ".join(part for part in (city, country) if part)
        subtitle = f"{order_name} monastery"
        if starting:
            subtitle += f", founded c. {starting}"

        article = "An" if order_name[:1].lower() in "aeiou" else "A"
        description_parts = [f"{article} {order_name} monastery"]
        if place:
            description_parts.append(f"recorded in {place}")
        if starting:
            description_parts.append(f"with activity beginning around {starting}")
        if ending:
            description_parts.append(f"and recorded through {ending}")
        description = " ".join(description_parts).rstrip(".") + "."

        tags = [
            "monastery",
            "sacred history",
            order_name.lower(),
            clean_text(country).lower(),
        ]

        return MuseumItem(
            title=name,
            subtitle=subtitle,
            description=description,
            category="sacred_history",
            subcategory=order_name.lower(),
            era=starting,
            region=historical_region or administrative_region or country,
            lat=_clean_float(raw.get("Latitude")),
            lon=_clean_float(raw.get("Longitude")),
            source_url=None,
            mood="reverent",
            template="archive",
            theme="candlelit",
            metadata={
                "order": order_name,
                "city": city,
                "country": country,
                "administrative_region": administrative_region,
                "historical_region": historical_region,
                "starting": starting,
                "ending": ending,
                "source_file": getattr(self, "source_path", self.xlsx_path).name,
            },
            tags=[tag for tag in tags if tag],
        )


def _clean_year(value: object) -> str | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return str(int(float(text)))
    except ValueError:
        return text


def _clean_float(value: object) -> float | None:
    text = clean_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def _tidy_name(value: str) -> str:
    if value.islower():
        return value.title()
    return value


ORDER_NAMES = {
    "Cistercians": "Cistercian",
    "Franciscans": "Franciscan",
}
