import logging
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from datetime import datetime

from config import ADMIN_SECRET, DUMMY_MODE
from db import NewsDatabase
from fetch_rss import fetch_all_feeds
from summarize import refine_summary

app = FastAPI()

# Logging
logger = logging.getLogger("short-news-api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
logger.addHandler(handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB
db = NewsDatabase()


@app.get("/", response_class=HTMLResponse)
def index():
    """
    Serve static HTML from /static/app.html
    """
    template_path = Path(__file__).parent / "static" / "app.html"

    if not template_path.exists():
        raise HTTPException(
            status_code=500,
            detail=f"Template not found: {template_path}"
        )

    with open(template_path, "r", encoding="utf-8") as f:
        html = f.read()

    return HTMLResponse(content=html, status_code=200)


@app.get("/news")
def get_news(limit: int = 20):
    """
    Fetch news items from MongoDB
    """
    items = db.get_latest_news(limit)
    return JSONResponse(items)


@app.get("/update")
def update_news(request: Request):
    """
    Pull new items from RSS feeds and store in DB
    """
    secret = request.headers.get("X-Admin-Secret")
    if secret != ADMIN_SECRET:
        return JSONResponse({"error": "Invalid secret key"}, status_code=401)

    logger.info("Manual update triggered.")

    # Fetch RSS items
    items = fetch_all_feeds()

    inserted = 0
    errors = []

    for item in items:
        try:
            if DUMMY_MODE:
                # Dummy mode summary
                item["summary"] = refine_summary(item.get("raw_summary", ""))
            else:
                # Real-time summary
                item["summary"] = refine_summary(item.get("raw_summary", ""))

            db.insert_news_item(item)
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    return {
        "status": "updated",
        "timestamp": datetime.utcnow().isoformat(),
        "inserted": inserted,
        "errors": errors,
    }
