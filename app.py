from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pathlib import Path
from datetime import datetime
import logging

from config import ADMIN_SECRET
from db import news_collection, usage_collection
from fetch_rss import fetch_all_feeds
from summarize import generate_summary

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("short-news-api")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------
# HOME PAGE  (FIXED - app.html loading)
# ------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    html_path = Path("static/app.html")
    if not html_path.exists():
        return HTMLResponse(
            "<h1>ERROR: static/app.html NOT FOUND</h1>",
            status_code=500
        )
    return html_path.read_text(encoding="utf-8")

# ------------------------------
# FETCH NEWS API
# ------------------------------
@app.get("/news")
async def get_news(limit: int = 20):
    cursor = news_collection.find().sort("created_at", -1).limit(limit)
    items = list(cursor)

    # Convert ObjectId → string
    for item in items:
        item["_id"] = str(item["_id"])

    return JSONResponse(items)

# ------------------------------
# MANUAL UPDATE API (protected)
# ------------------------------
@app.get("/update")
async def update_news(request: Request):
    secret = request.headers.get("X-Admin-Secret")
    if secret != ADMIN_SECRET:
        return JSONResponse({"error": "Invalid secret key"}, status_code=401)

    log.info("Fetching RSS feeds...")
    inserted, errors = fetch_all_feeds()

    return {
        "status": "updated",
        "timestamp": str(datetime.utcnow()),
        "inserted": inserted,
        "errors": errors,
    }


# ------------------------------
#  SUMMARIZE ENDPOINT (dummy mode)
# ------------------------------
@app.get("/summarize")
async def test_summary():
    text = "Dummy text for testing"
    summary = generate_summary(text)
    return {"input": text, "summary": summary}


# ------------------------------
# HEALTH CHECK
# ------------------------------
@app.get("/health")
def health():
    return {"status": "ok"}
