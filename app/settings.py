from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = BASE_DIR / "raw"
FRONTEND_DIR = BASE_DIR / "frontend"
MEDIA_DIR = BASE_DIR / "media"
DB_PATH = DATA_DIR / "museum.db"

APP_NAME = "Curiosity Museum"
RECENT_WINDOW = 8
