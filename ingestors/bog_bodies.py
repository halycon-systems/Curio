import re
from pathlib import Path

from app.models import Dataset, MuseumItem
from app.settings import BASE_DIR, RAW_DIR
from ingestors.base import BaseIngestor, as_list, normalize_item, read_json_file
from ingestors.xlsx import clean_text, read_xlsx_tables


class BogBodiesIngestor(BaseIngestor):
    def __init__(self, path: Path | None = None):
        self.path = path
        self.json_path = RAW_DIR / "downloaded" / "bog_bodies.json"
        self.xlsx_path = BASE_DIR / "data" / "raw" / "BogBodies.xlsx"
        self.dataset = Dataset(
            slug="bog_bodies",
            name="Bog Bodies",
            category="morbid_history",
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
                default_category="morbid_history",
                default_template="memorial",
                default_theme="quiet",
                default_mood="solemn",
            )
            if item:
                if not item.subcategory:
                    item.subcategory = "bog_body"
                items.append(item)
        return items

    def _load_xlsx(self, path: Path) -> list[MuseumItem]:
        tables = read_xlsx_tables(path)
        rows = next(iter(tables.values()), [])
        grouped: dict[str, list[dict[str, str]]] = {}
        for raw in rows:
            record_id = clean_text(raw.get("No."))
            if not record_id:
                continue
            grouped.setdefault(record_id, []).append(raw)

        items = []
        for record_id, group in grouped.items():
            item = self._group_to_item(record_id, group)
            if item:
                items.append(item)
        return items

    def _group_to_item(
        self, record_id: str, group: list[dict[str, str]]
    ) -> MuseumItem | None:
        raw = group[0]
        name = clean_text(raw.get("Name"))
        location = clean_text(raw.get("Location (nearest village or city)"))
        country = clean_text(raw.get("Country"))
        preservation = clean_text(raw.get("Preservation/completeness"))
        if name:
            title = name
        elif location:
            title = f"{location} bog body"
        else:
            title = f"Bog body {record_id}"
        find_year = _clean_year(raw.get("Find year"))
        sex = clean_text(raw.get("Sex"))
        age = clean_text(raw.get("Age"))
        age_group = clean_text(raw.get("Age group"))
        cause = clean_text(raw.get("Assumed cause of death"))

        subtitle_parts = [part for part in (country, preservation) if part]
        if find_year:
            subtitle_parts.append(f"found {find_year}")

        tags = ["bog body", "morbid history", country.lower(), preservation.lower()]
        if sex and sex != "unknown":
            tags.append(sex.lower())
        if cause and cause != "unknown":
            tags.append("violent death" if cause.startswith("violent") else cause.lower())

        dating = [_dating_row(row) for row in group]
        dating = [row for row in dating if any(row.values())]
        full_description = clean_text(raw.get("Concise description"))

        return MuseumItem(
            title=title,
            subtitle=", ".join(subtitle_parts) or None,
            description=_short_description(full_description),
            category="morbid_history",
            subcategory="bog_body",
            era=_era_label(group),
            region=country,
            lat=_clean_float(raw.get("Latitude")),
            lon=_clean_float(raw.get("Longitude")),
            source_url=None,
            rarity=clean_text(raw.get("Site category")),
            mood="solemn",
            template="memorial",
            theme="quiet",
            metadata={
                "record_id": record_id,
                "phase": clean_text(raw.get("Phase")),
                "location": location,
                "bog": clean_text(raw.get("Bog")),
                "sex": sex,
                "age": age,
                "age_group": age_group,
                "pathology": clean_text(raw.get("Pathology")),
                "assumed_cause_of_death": cause,
                "general_trauma": clean_text(raw.get("General trauma (cause/timing unknown)")),
                "ante_mortem_trauma": clean_text(raw.get("Ante-mortem trauma (violence-related)")),
                "peri_mortem_trauma": clean_text(raw.get("Peri-mortem trauma (violence-related)")),
                "post_mortem_trauma": clean_text(raw.get("Post-mortem trauma (body treatment)")),
                "clothing": clean_text(raw.get("Clothing")),
                "associated_finds": clean_text(raw.get("Associated finds")),
                "find_year": find_year,
                "full_description": full_description,
                "dating": dating,
                "reference": clean_text(raw.get("Reference")),
                "source_file": self.xlsx_path.name,
            },
            tags=[tag for tag in tags if tag],
        )


def _dating_row(raw: dict[str, str]) -> dict[str, str | None]:
    return {
        "lab_no": clean_text(raw.get("Lab no.")) or None,
        "material": clean_text(raw.get("Dating material")) or None,
        "method": clean_text(raw.get("Dating method")) or None,
        "radiocarbon_age_bp": _clean_year(raw.get("Radiocarbon Age (BP)")),
        "radiocarbon_error_bp": _clean_year(raw.get("Radiocarbon Error (BP)")),
        "estimated_age": clean_text(raw.get("Estimated age (non-radiocarbon)")) or None,
        "remarks": clean_text(raw.get("Remarks on performed dates")) or None,
    }


def _era_label(group: list[dict[str, str]]) -> str | None:
    first_estimate = next(
        (
            clean_text(row.get("Estimated age (non-radiocarbon)"))
            for row in group
            if clean_text(row.get("Estimated age (non-radiocarbon)"))
        ),
        "",
    )
    if first_estimate:
        return first_estimate

    ages = [
        int(age)
        for age in (_clean_year(row.get("Radiocarbon Age (BP)")) for row in group)
        if age and age.isdigit()
    ]
    if not ages:
        return None
    if len(ages) == 1:
        return f"{ages[0]} BP"
    return f"{min(ages)}-{max(ages)} BP"


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


def _short_description(value: str, max_sentences: int = 4, max_chars: int = 620) -> str | None:
    if not value:
        return None

    protected = (
        value.replace("c. ", "c~ ")
        .replace("approx. ", "approx~ ")
        .replace("AD. ", "AD~ ")
    )
    sentences = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", protected)
    sentences = [sentence.replace("c~ ", "c. ").replace("approx~ ", "approx. ").replace("AD~ ", "AD. ").strip() for sentence in sentences if sentence.strip()]

    summary = " ".join(sentences[:max_sentences]).strip()
    if len(summary) <= max_chars:
        return summary

    clipped = summary[:max_chars].rsplit(" ", 1)[0].rstrip(",;:")
    return f"{clipped}..."
