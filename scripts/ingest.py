import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import connect, init_db, insert_items, upsert_dataset
from ingestors.registry import get_ingestors


def main() -> None:
    conn = connect()
    init_db(conn)
    total = 0
    for ingestor in get_ingestors():
        items = ingestor.load()
        dataset_id = upsert_dataset(conn, ingestor.dataset)
        count = insert_items(conn, dataset_id, items)
        total += count
        print(f"{ingestor.dataset.slug}: {count} items")
    conn.close()
    print(f"Imported {total} items.")


if __name__ == "__main__":
    main()
