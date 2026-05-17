from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.db import fetch_categories, fetch_items, init_db
from app.randomizer import choose_item, parse_csv, parse_int_csv
from app.settings import APP_NAME, FRONTEND_DIR, MEDIA_DIR

app = FastAPI(title=APP_NAME)


@app.on_event("startup")
def startup() -> None:
    init_db()


app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/api/random")
def random_item(
    category: str | None = None,
    recent_item_ids: str | None = Query(default=None),
    recent_categories: str | None = Query(default=None),
    recent_subcategories: str | None = Query(default=None),
    recent_moods: str | None = Query(default=None),
    disable_smart_random: bool = False,
    include_morbid: bool = True,
) -> dict:
    item = choose_item(
        fetch_items(category=category, include_morbid=include_morbid),
        recent_item_ids=parse_int_csv(recent_item_ids),
        recent_categories=parse_csv(recent_categories),
        recent_subcategories=parse_csv(recent_subcategories),
        recent_moods=parse_csv(recent_moods),
        disable_smart_random=disable_smart_random,
    )
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="The cabinet is empty. Ingest some curiosities first.",
        )
    return item


@app.get("/api/categories")
def categories() -> list[dict]:
    return fetch_categories()
