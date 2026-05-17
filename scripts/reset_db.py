import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db import reset_db


if __name__ == "__main__":
    reset_db()
    print("Reset data/museum.db")
