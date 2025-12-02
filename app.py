import logging
from pathlib import Path
from typing import List, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pymongo.collection import Collection

from config import settings
from db import news_collection, init_indexes, get_db
from fetch_rss import fetch_and_store_all_feeds

# ----- Logging -----
logger = logging.getLogger("short-news-api")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logging.basicConfig(level=logger.level)

# ----- App init -----
app = FastAPI(title="24-7 Telugu News API")

# Static files (for app.html if you want to move later)
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


# CORS – allow all for now (mobile/web clients)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_news_collection() -> Collection:
    return news_collection


@app.on_event("startup")
def startup_event() -> None:
    logger.info("MongoDB connected, initializing indexes")
    init_indexes()
    logger.info("Startup complete")


# ----- Routes -----


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    """
    Serve SPA HTML (current app.html in root).
    """
    html_path = Path(__file__).parent / "app.html"
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="app.html missing")
    return html_path.read_text(encoding="utf-8")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.get("/api/news")
async def list_news(
    category: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    collection: Collection = Depends(get_news_collection),
):
    """
    Get paginated list of news.
    """
    query = {}
    if category:
        query["category"] = category

    cursor = (
        collection.find(query)
        .sort("published_at", -1)
        .skip(skip)
        .limit(limit)
    )

    items: List[dict] = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        items.append(doc)

    return {"items": items, "count": len(items)}


@app.post("/admin/fetch")
async def admin_fetch(request: Request):
    """
    Manually trigger RSS fetch + summarize.
    """
    data = await request.json()
    secret = data.get("secret")
    if secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    await fetch_and_store_all_feeds()
    return {"status": "ok"}
@app.get("/news")
async def read_first_news():
    news = await get_first_news_from_db()
    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "title": news["title"], "summary": news["summary"], "link": news["link"], "id": news["_id"]}
    )
