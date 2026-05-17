import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, delete_dataset, fetch_dataset_slugs, init_db, replace_dataset_items
from ingestors.handcrafted_json import DEFAULTS, handcrafted_slugs
from ingestors.registry import get_ingestors


def main() -> None:
    conn = connect()
    init_db(conn)
    total = 0
    try:
        seen_slugs = set()
        for ingestor in get_ingestors():
            seen_slugs.add(ingestor.dataset.slug)
            items = ingestor.load()
            count = replace_dataset_items(conn, ingestor.dataset, items)
            total += count
            print(f"{ingestor.dataset.slug}: {count} items")
        expected_handcrafted = set(DEFAULTS) | handcrafted_slugs()
        for slug in fetch_dataset_slugs(conn):
            is_handcrafted = slug in expected_handcrafted or slug.startswith("_")
            if is_handcrafted and slug not in seen_slugs:
                delete_dataset(conn, slug)
                print(f"{slug}: removed stale dataset")
    finally:
        conn.close()
    print(f"Imported {total} items.")


if __name__ == "__main__":
    main()
