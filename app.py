import os
import logging
import re
from datetime import datetime
from fastapi import FastAPI, Query, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
import feedparser

from config import (
    MONGO_URL,
    MONGO_DB_NAME,
    RSS_FEEDS,
    ADMIN_SECRET,
    GOOGLE_API_KEY,
    GEMINI_MODEL,
)

from gemini_client import summarize_text


# -----------------------------------------------------------------------------
# LOGGING
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO)
log = logging.getLogger("short-news-api")


# -----------------------------------------------------------------------------
# DB INIT
# -----------------------------------------------------------------------------
client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
news_col = db["news"]

log.info("MongoDB connected")


# -----------------------------------------------------------------------------
# SMART SUMMARY CLEANER (Stage-3)
# -----------------------------------------------------------------------------
def smart_clean_summary(text: str) -> str:
    """
    Telugu-focused cleaner:
    - Keep Telugu fully
    - Keep meaningful English (AP, ED, CBI, Rapido, Skill Development…)
    - Remove useless English sentences
    - Remove long English lines
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Break by sentences
    parts = re.split(r'([.!?])', text)
    sentences = ["".join(parts[i:i+2]).strip()
                 for i in range(0, len(parts), 2)]

    cleaned = []

    for s in sentences:

        # Telugu exists → keep
        if re.search(r'[\u0C00-\u0C7F]', s):
            cleaned.append(s)
            continue

        # Long English sentence → remove
        if len(s.split()) > 4:
            continue

        # Short proper English words allowed
        if re.match(r'^[A-Za-z0-9\-\(\) ]{1,30}$', s):
            cleaned.append(s)
            continue

    result = " ".join(cleaned)
    result = re.sub(r"\s+", " ", result).strip()

    return result


# -----------------------------------------------------------------------------
# FASTAPI APP
# -----------------------------------------------------------------------------
app = FastAPI(title="Short News API", version="3.0")

# CORS for UI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


# -----------------------------------------------------------------------------
# INDEX ROUTE (UI)
# -----------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    with open("app.html", "r", encoding="utf-8") as f:
        return f.read()


# -----------------------------------------------------------------------------
# /update  → Fetch RSS + Summaries + Store
# -----------------------------------------------------------------------------
@app.get("/update")
def update_news(x_admin_secret: str = Header(None)):

    if x_admin_secret != ADMIN_SECRET:
        return {"error": "Invalid secret key"}

    inserted = []
    errors = []

    for feed_url in RSS_FEEDS:
        log.info("Fetching feed: %s", feed_url)
        data = feedparser.parse(feed_url)

        for entry in data.entries:
            link = entry.link
            title = entry.title
            published = entry.get("published", "")
            summary_raw = entry.get("summary", "")

            if news_col.find_one({"link": link}):
                continue

            # Fetch full summary from Gemini
            ai_summary = summarize_text(
                title=title,
                content=summary_raw,
                model=GEMINI_MODEL,
                max_output_tokens=180,
            )

            # Store raw + clean version
            doc = {
                "title": title,
                "link": link,
                "published": published,
                "raw_summary": summary_raw,
                "summary": ai_summary,
                "source": feed_url,
                "created_at": datetime.utcnow(),
            }

            try:
                news_col.insert_one(doc)
                inserted.append(link)
            except Exception as e:
                log.error("Insert error: %s", e)
                errors.append(str(e))

    return {
        "status": "updated",
        "timestamp": datetime.utcnow().isoformat(),
        "inserted": len(inserted),
        "errors": errors,
    }


# -----------------------------------------------------------------------------
# /news → Cleaned, Telugu-focused output for mobile UI
# -----------------------------------------------------------------------------
@app.get("/news")
def get_news(limit: int = 10):

    docs = list(news_col.find().sort("created_at", -1).limit(limit))

    final = []
    for d in docs:
        d["_id"] = str(d["_id"])

        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()

        # CLEAN HERE — Stage-3 magic
        if "summary" in d and isinstance(d["summary"], str):
            d["summary"] = smart_clean_summary(d["summary"])

        final.append(d)

    return final
