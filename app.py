import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from pymongo.errors import PyMongoError

from config import settings  # Settings object with env vars
from db import (
    news_collection,
    usage_collection,
    errors_collection,
)
from fetch_rss import fetch_and_store_latest

# -------------------------------------------------
# Logging setup
# -------------------------------------------------
logger = logging.getLogger("short-news-api")
logger.setLevel(settings.LOG_LEVEL)

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

# -------------------------------------------------
# FastAPI app
# -------------------------------------------------
app = FastAPI(
    title="24/7 Telugu Short News API",
    description="Short news API for Telugu RSS feeds with summaries",
    version="3.2-dummy-gemini",
)

# CORS for your app / future frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------
# Helpers
# -------------------------------------------------
def serialize_news(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert Mongo document to JSON-safe dict."""
    doc = dict(doc)
    _id = doc.get("_id")
    if _id is not None:
        doc["_id"] = str(_id)
    # datetime to isoformat
    for key in ("created_at", "updated_at"):
        if isinstance(doc.get(key), datetime):
            doc[key] = doc[key].isoformat()
    return doc


def log_usage(endpoint: str, extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        payload: Dict[str, Any] = {
            "endpoint": endpoint,
            "timestamp": datetime.utcnow(),
        }
        if extra:
            payload.update(extra)
        usage_collection.insert_one(payload)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to log usage: %s", exc)


def log_error(context: str, error: str, meta: Optional[Dict[str, Any]] = None) -> None:
    try:
        payload: Dict[str, Any] = {
            "context": context,
            "error": error,
            "timestamp": datetime.utcnow(),
        }
        if meta:
            payload["meta"] = meta
        errors_collection.insert_one(payload)
    except Exception:
        # Last-line defence; never crash app because of logging
        logger.exception("Failed to log error")


# -------------------------------------------------
# Events
# -------------------------------------------------
@app.on_event("startup")
def on_startup() -> None:
    logger.info("MongoDB connected")


# -------------------------------------------------
# UI (index)
# -------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    """
    Serve the app.html UI.

    We resolve the path relative to this file, so it works
    no matter where the working directory is in Koyeb.
    """
    base_dir = Path(__file__).resolve().parent
    html_path = base_dir / "app.html"  # <--- app.html must be in repo root

    if not html_path.exists():
        logger.error("app.html not found at %s", html_path)
        raise HTTPException(
            status_code=500,
            detail=f"app.html not found at {html_path.name}",
        )

    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


# -------------------------------------------------
# Public API
# -------------------------------------------------
@app.get("/news")
def get_news(
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Return latest news items."""
    try:
        query: Dict[str, Any] = {}
        if category:
            query["category"] = category

        cursor = (
            news_collection.find(query)
            .sort("published", -1)
            .limit(limit)
        )

        items = [serialize_news(doc) for doc in cursor]
        log_usage("/news", {"limit": limit, "category": category})
        return items

    except PyMongoError as exc:
        logger.exception("Mongo error in /news: %s", exc)
        log_error("/news", str(exc), {"limit": limit, "category": category})
        raise HTTPException(status_code=500, detail="Database error") from exc


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


# -------------------------------------------------
# Admin: force update
# -------------------------------------------------
@app.get("/update")
def update_news(request: Request) -> JSONResponse:
    """Fetch latest RSS, summarize & store.

    Protected with X-Admin-Secret header.
    """
    admin_secret = request.headers.get("X-Admin-Secret")
    if not admin_secret or admin_secret != settings.ADMIN_SECRET:
        logger.warning("Invalid admin secret for /update")
        raise HTTPException(status_code=401, detail="Invalid secret key")

    try:
        logger.info("Manual /update triggered")
        result = fetch_and_store_latest()
        # result: {"inserted": int, "errors": [...]}
        log_usage("/update", {"inserted": result.get("inserted", 0)})
        payload = {
            "status": "updated",
            "timestamp": datetime.utcnow().isoformat(),
            **result,
        }
        return JSONResponse(content=payload)
    except Exception as exc:  # noqa: BLE001
        logger.exception("Error during /update: %s", exc)
        log_error("/update", str(exc))
        raise HTTPException(status_code=500, detail="Update failed") from exc
