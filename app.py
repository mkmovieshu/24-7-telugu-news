import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from db import get_db
from fetch_rss import fetch_and_store_all_feeds
from config import ADMIN_SECRET

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("short-news-api")

app = FastAPI(title="short-news-api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to app.html (must be beside app.py)
BASE_DIR = Path(__file__).resolve().parent
APP_HTML = BASE_DIR / "app.html"


def serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB doc to JSON serializable format."""
    doc = dict(doc)
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve UI"""
    if not APP_HTML.exists():
        logger.error(f"app.html NOT FOUND at {APP_HTML}")
        return HTMLResponse(
            content=f"<h2>Error:</h2> app.html missing at {APP_HTML}",
            status_code=500,
        )

    try:
        content = APP_HTML.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to read app.html: {e}")
        raise HTTPException(status_code=500, detail="Cannot read app.html")

    return HTMLResponse(content)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "time": datetime.utcnow().isoformat() + "Z",
    }


@app.get("/news")
def get_news(limit: int = 20, skip: int = 0, source: Optional[str] = None):
    db = get_db()

    query = {}
    if source:
        query["source"] = source

    cursor = (
        db.news.find(query)
        .sort("created_at", -1)
        .skip(skip)
        .limit(limit)
    )

    return [serialize(doc) for doc in cursor]


@app.get("/update")
def update_news(request: Request):
    if ADMIN_SECRET:
        header_secret = request.headers.get("X-Admin-Secret")
        if header_secret != ADMIN_SECRET:
            logger.warning("Unauthorized access attempt to /update")
            raise HTTPException(status_code=401, detail="Unauthorized")

    logger.info("Manual update triggered")
    result = fetch_and_store_all_feeds()
    return JSONResponse(result)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
