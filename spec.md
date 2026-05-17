# Curiosity Museum - Technical Specification (V1)

## Project Vision

A tiny web experience at `curiosity.halycon.systems`.

User opens site.
Black background.
A mysterious box appears.
User clicks.
A strange thing is revealed.
User can read more or ask for another.
Repeat forever.

This is **not** a productivity app.
This is **not** a dashboard.
This is a curated digital cabinet of curiosities.

Core vibe:
- weird
- atmospheric
- elegant
- occult velvet
- low friction
- infinite curiosity dopamine

Examples of content:
- bog bodies
- historical monasteries
- obsolete household objects
- weird place names
- ancient jobs
- mushrooms
- superstitions
- castles
- folklore motifs

---

# Tech Stack

## Backend
- Python
- FastAPI
- SQLite

## Frontend
- Plain HTML
- CSS
- Vanilla JavaScript

No frontend framework.
No library hell.

## Hosting
Existing self-host environment:
- Debian server
- Cloudflare tunnel
- `halycon.systems`

Deployment assumption:
- run the FastAPI app behind the existing Cloudflare tunnel
- no special deployment platform required for V1

---

# Project Structure

```text
Curio/
  app/
    main.py
    db.py
    models.py
    randomizer.py
    settings.py

  ingestors/
    base.py
    registry.py
    handcrafted_json.py
    bog_bodies.py
    monasteries.py

  data/
    museum.db

  raw/
    handcrafted/
      obsolete_household_objects.json
      superstitions.json
      weird_place_names.json
    downloaded/
      bog_bodies.json
      monasteries.json

  data/
    raw/
      Monistaries/
        Monistary1.xlsx
        Monistary2.xlsx

  frontend/
    index.html
    css/
      base.css
      themes.css
      components.css
      cards.css
    js/
      app.js
      api.js
      renderers.js
      settings.js

  media/
    backgrounds/
    category_art/
    icons/
    item_images/

  scripts/
    ingest.py
    reset_db.py

  README.md
```

---

# Database Design

## One Database Only

Use a single SQLite database:

```text
museum.db
```

Do NOT create:
- one DB per dataset
- one DB per category
- fragmented data silos

Reason:
- easier querying
- simpler backups
- cleaner architecture
- avoids chaotic sprawl

---

## Core Tables

### datasets
Metadata about imported content packs.

```sql
id
slug
name
source_url
category
enabled
imported_at
item_count
version
```

Examples:
- bog_bodies
- monasteries
- weird_place_names

---

### items
Unified renderable museum objects.

Every source becomes the same frontend-friendly structure.

```sql
id
dataset_id
title
subtitle
description
category
subcategory
era
region
lat
lon
source_url
image_url
rarity
mood
template
theme
metadata_json
```

Examples:

Historical monastery:
```json
{
  "title": "Whitby Abbey",
  "category": "sacred_history",
  "template": "archive",
  "theme": "candlelit"
}
```

Bog body:
```json
{
  "title": "Tollund Man",
  "category": "morbid_history",
  "template": "archive",
  "theme": "quiet"
}
```

---

### tags

```sql
id
name
```

Examples:
- spooky
- cute
- victorian
- ancient
- cosy
- creature
- systems
- folklore

---

### item_tags

```sql
item_id
tag_id
```

---

# Ingestion Architecture

## Modular Ingestors

DO NOT build one giant smart ingestor.

That becomes an unreadable god-function.

Instead:
One ingestor per source type.

Examples:
```text
ingestors/
  bog_bodies.py
  monasteries.py
  handcrafted_json.py
```

Each ingestor:

```python
raw weird source -> normalized museum items
```

This keeps the system modular and expandable.

---

## Handcrafted JSON Support

Some content will be manually curated.

Example:

```json
[
  {
    "title": "Antimacassar",
    "subtitle": "Victorian household object",
    "summary": "Decorative cloth used to protect furniture from hair oil.",
    "tags": ["victorian", "domestic", "object"]
  }
]
```

This should ingest through a generic handcrafted JSON ingestor.

Existing curated JSON files are expected and should be supported without forcing one rigid schema. The handcrafted ingestor should accept common aliases such as `summary` for `description`, while still normalizing everything into the unified `items` table.

---

# API Design

## V1 Endpoints

### Random item

```http
GET /api/random
```

Returns one smart-random museum item.

---

### Random by category

```http
GET /api/random?category=creatures
```

---

### Categories

```http
GET /api/categories
```

---

## Future Endpoints
Not V1, but architecture should allow:

```http
GET /api/item/{id}
GET /api/nearby?lat=x&lon=y
GET /api/search
```

---

# Randomization Logic

## Smart Random Required

Pure randomness is emotionally bad.

Example bad experience:
- bog body
- bog body
- another bog body

Instead implement smart random.

Rules:

### Hard rules
Avoid:
- exact repeat
- same item twice
- same category immediately
- same subcategory immediately

Cooldown window:
5-10 recent items.

---

### Soft rules
Weight against:
- tonal repetition
- excessive morbidity streaks
- repetitive creature types

Encourage variety.

Example healthy sequence:
- bog body
- historical monastery
- weird place name
- superstition
- obsolete object

---

### Session Memory
Track in browser session storage:

```text
recent_item_ids
recent_categories
recent_moods
```

No account system required.

---

# Frontend UX

## Core Experience

User lands on:
black screen.
minimal UI.
centered mysterious box.
occult velvet atmosphere.

Text:

```text
What's inside?
```

Click opens box.
Reveal weird item.

Buttons:
- Read more
- Another

Infinite loop.

---

# Frontend Architecture

Frontend remains dumb.

Responsibilities:
- call API
- render item
- animate transitions
- maintain session history
- optional dev controls

No business logic in frontend.

---

# Rendering System

Different content types should NOT look identical.

Historical monasteries should not visually resemble bog bodies.

Do NOT create separate frontend apps per category.

Instead:
metadata-driven rendering.

Each item includes:

```json
{
  "template": "specimen",
  "tone": "light",
  "theme": "naturalist"
}
```

---

## Template Types

Examples:

### specimen
For:
- animals
- plants
- mushrooms

Style:
- natural history specimen label

---

### archive
For:
- objects
- historical entries
- bog bodies

Style:
- museum archive card

---

### memorial
For:
- serious human content

Style:
- restrained
- respectful
- minimal animation

---

### tale
For:
- folklore
- superstitions
- myths

Style:
- atmospheric / candlelit

---

### incident
For:
- plane crashes
- system failures
- maritime incidents

Style:
- technical / structured

---

## Renderer Pattern

Single renderer registry:

```javascript
const templates = {
  specimen: renderSpecimenCard,
  archive: renderArchiveCard,
  memorial: renderMemorialCard,
  tale: renderTaleCard,
  incident: renderIncidentCard,
};
```

Avoid per-category frontend chaos.

---

# Theme System

Must be themeable from day one.

Use CSS variables.

Example:

```css
:root {
  --bg: #050505;
  --text: #f3ead7;
  --muted: #a99d89;
  --accent: #c6a15b;
  --card-bg: #111;
  --card-border: rgba(198, 161, 91, 0.35);
}
```

Theme overrides:

```css
.theme-naturalist
.theme-quiet
.theme-arsenic-green
.theme-candlelit
.theme-systems
```

---

# Media Strategy

DO NOT require exact per-item images.

Many datasets will not have images.

Supported visual strategies:

## Category art
Shared illustration per category.

Examples:
- creatures
- folklore
- architecture
- history

---

## Typography-first cards
Elegant text-led design.
Museum placard style.

---

## Optional item images
Used when available.
Fallback gracefully.

---

# Dev Settings

Hidden dev settings required.

Access:
secret button / hidden trigger.

Examples:
- triple click
- long press
- shift click

---

## Dev options

- show item ID
- show dataset source
- show raw JSON
- clear session history
- disable smart random
- force category
- force template
- toggle morbid content visibility in dev/testing

Morbid content is allowed by default in V1.

---

# V1 Scope Lock

STRICT.

Do NOT build full museum empire immediately.

V1 content sources:
- 2 real imported datasets
- 3 handcrafted packs

Examples:

Imported:
- bog bodies
- historical monasteries

Historical monastery source notes:
- `Monistary2.xlsx` contains individual monastery rows and is ingested for V1.
- `Monistary1.xlsx` is a region/year analytical panel and is kept as reference data unless a future view needs aggregate historical scores.

Handcrafted:
- obsolete household objects
- weird place names
- superstitions

Goal:
prove architecture + UX.

---

# Non-Goals (V1)

NO:
- auth
- user accounts
- favourites
- search UI
- ratings
- recommendations
- AI curator companion
- nearby geo explorer
- content editor UI
- giant admin dashboard

Keep the weird box sacred.
