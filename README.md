# Curio

A tiny gothic cabinet of curiosities: black screen, mysterious box, strange reveal, repeat forever.

## Run Locally

```powershell
python -m pip install -r requirements.txt
python scripts/ingest.py
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000`.

## Raw Data

Raw files are ingestion inputs only. Run `python scripts/ingest.py` to normalize them into `data/museum.db`; the FastAPI app reads from SQLite at runtime and does not touch the cursed workbooks during normal browsing.

Drop JSON files here:

```text
raw/downloaded/bog_bodies.json
raw/downloaded/monasteries.json
raw/handcrafted/obsolete_household_objects.json
raw/handcrafted/superstitions.json
raw/handcrafted/weird_place_names.json
```

The monastery ingestor also reads the source workbook at:

```text
data/raw/Monistaries/Monistary2.xlsx
```

`Monistary1.xlsx` is a region/year analytical panel, not individual museum entries, so it is currently treated as reference material rather than ingested as cards.

The ingestors accept either a top-level list or a wrapper object with `items`, `data`, `records`, or `results`.

Common aliases are normalized:

- `name`, `label`, `site`, `object` -> `title`
- `summary`, `text`, `notes`, `body`, `details` -> `description`
- `location` -> `region`
- `period` or `date` -> `era`

## API

- `GET /api/random`
- `GET /api/random?category=sacred_history`
- `GET /api/categories`

## Dev Settings

Triple-click the invisible top-left corner of the page, or shift-click it, to open the dev panel.
