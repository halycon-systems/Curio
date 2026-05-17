import json
import sqlite3
from collections.abc import Iterable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.models import Dataset, MuseumItem
from app.settings import DB_PATH


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> None:
    owns_conn = conn is None
    conn = conn or connect()
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS datasets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            slug TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            source_url TEXT,
            category TEXT NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 1,
            imported_at TEXT,
            item_count INTEGER NOT NULL DEFAULT 0,
            version TEXT
        );

        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dataset_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            subtitle TEXT,
            description TEXT,
            category TEXT NOT NULL,
            subcategory TEXT,
            era TEXT,
            region TEXT,
            lat REAL,
            lon REAL,
            source_url TEXT,
            image_url TEXT,
            rarity TEXT,
            mood TEXT,
            template TEXT NOT NULL DEFAULT 'archive',
            theme TEXT NOT NULL DEFAULT 'candlelit',
            metadata_json TEXT NOT NULL DEFAULT '{}',
            FOREIGN KEY (dataset_id) REFERENCES datasets(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS item_tags (
            item_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (item_id, tag_id),
            FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
        );

        CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
        CREATE INDEX IF NOT EXISTS idx_items_subcategory ON items(subcategory);
        CREATE INDEX IF NOT EXISTS idx_items_mood ON items(mood);
        """
    )
    conn.commit()
    if owns_conn:
        conn.close()


def reset_db() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    init_db()


def upsert_dataset(conn: sqlite3.Connection, dataset: Dataset) -> int:
    now = datetime.now(timezone.utc).isoformat()
    conn.execute(
        """
        INSERT INTO datasets (slug, name, source_url, category, enabled, imported_at, version)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(slug) DO UPDATE SET
            name = excluded.name,
            source_url = excluded.source_url,
            category = excluded.category,
            enabled = excluded.enabled,
            imported_at = excluded.imported_at,
            version = excluded.version
        """,
        (
            dataset.slug,
            dataset.name,
            dataset.source_url,
            dataset.category,
            int(dataset.enabled),
            now,
            dataset.version,
        ),
    )
    row = conn.execute("SELECT id FROM datasets WHERE slug = ?", (dataset.slug,)).fetchone()
    if row is None:
        raise RuntimeError(f"Dataset was not written: {dataset.slug}")
    conn.execute("DELETE FROM items WHERE dataset_id = ?", (row["id"],))
    return int(row["id"])


def insert_items(
    conn: sqlite3.Connection, dataset_id: int, items: Iterable[MuseumItem]
) -> int:
    count = 0
    for item in items:
        cursor = conn.execute(
            """
            INSERT INTO items (
                dataset_id, title, subtitle, description, category, subcategory, era,
                region, lat, lon, source_url, image_url, rarity, mood, template,
                theme, metadata_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                dataset_id,
                item.title,
                item.subtitle,
                item.description,
                item.category,
                item.subcategory,
                item.era,
                item.region,
                item.lat,
                item.lon,
                item.source_url,
                item.image_url,
                item.rarity,
                item.mood,
                item.template,
                item.theme,
                json.dumps(item.metadata, ensure_ascii=True),
            ),
        )
        item_id = int(cursor.lastrowid)
        for tag in item.tags:
            tag_name = str(tag).strip().lower()
            if not tag_name:
                continue
            conn.execute("INSERT OR IGNORE INTO tags (name) VALUES (?)", (tag_name,))
            tag_id = conn.execute("SELECT id FROM tags WHERE name = ?", (tag_name,)).fetchone()[
                "id"
            ]
            conn.execute(
                "INSERT OR IGNORE INTO item_tags (item_id, tag_id) VALUES (?, ?)",
                (item_id, tag_id),
            )
        count += 1

    conn.execute("UPDATE datasets SET item_count = ? WHERE id = ?", (count, dataset_id))
    conn.commit()
    return count


def row_to_item(row: sqlite3.Row) -> dict[str, Any]:
    metadata = json.loads(row["metadata_json"] or "{}")
    return {
        "id": row["id"],
        "dataset": {
            "id": row["dataset_id"],
            "slug": row["dataset_slug"],
            "name": row["dataset_name"],
            "source_url": row["dataset_source_url"],
        },
        "title": row["title"],
        "subtitle": row["subtitle"],
        "description": row["description"],
        "category": row["category"],
        "subcategory": row["subcategory"],
        "era": row["era"],
        "region": row["region"],
        "lat": row["lat"],
        "lon": row["lon"],
        "source_url": row["source_url"],
        "image_url": row["image_url"],
        "rarity": row["rarity"],
        "mood": row["mood"],
        "template": row["template"],
        "theme": row["theme"],
        "metadata": metadata,
    }


def fetch_items(
    category: str | None = None, include_morbid: bool = True
) -> list[dict[str, Any]]:
    conn = connect()
    query = """
        SELECT
            items.*,
            datasets.slug AS dataset_slug,
            datasets.name AS dataset_name,
            datasets.source_url AS dataset_source_url
        FROM items
        JOIN datasets ON datasets.id = items.dataset_id
        WHERE datasets.enabled = 1
    """
    params: list[Any] = []
    if category:
        query += " AND items.category = ?"
        params.append(category)
    if not include_morbid:
        query += " AND items.category != ?"
        params.append("morbid_history")
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [row_to_item(row) for row in rows]


def fetch_categories() -> list[dict[str, Any]]:
    conn = connect()
    rows = conn.execute(
        """
        SELECT category, COUNT(*) AS item_count
        FROM items
        GROUP BY category
        ORDER BY category
        """
    ).fetchall()
    conn.close()
    return [{"category": row["category"], "item_count": row["item_count"]} for row in rows]
