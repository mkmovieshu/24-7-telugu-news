# app.py
import os
import time
import logging
from datetime import datetime
from typing import List

import feedparser
import requests
from fastapi import FastAPI, Request, HTTPException
from pymongo import MongoClient
from dotenv import load_dotenv

# load local .env if present (helps local testing)
load_dotenv()

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("short-news-api")

# Environment variables (must exist in Render)
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
ADMIN_SECRET = os.getenv("ADMIN_SECRET") or os.getenv("X_ADMIN_SECRET") or os.getenv("API_ADMIN_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RSS_FEEDS = os.getenv("RSS_FEEDS", "")  # comma separated list of feed URLs
MAX_ITEMS_PER_FEED = int(os.getenv("MAX_ITEMS_PER_FEED", "5"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")
USER_AGENT = os.getenv("FETCH_USER_AGENT", "Mozilla/5.0 (X11; Linux x86_64)")

# Validate critical env
if not MONGO_URL:
    logger.warning("MONGO_URL not set in environment — DB operations will fail.")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not set in environment — Gemini calls will fail.")

# Mongo client
client = MongoClient(MONGO_URL) if MONGO_URL else None
db = client[MONGO_DB_NAME] if client else None

# Preserve exact collection names required by user
videos_col = db["videos"] if db else None
errors_col = db["errors"] if db else None

# Import gemini wrapper (the REST wrapper file we added)
from gemini_client import summarize_text

app = FastAPI(title="Short News API")

@app.get("/")
def status():
    return {"status": "Short News API Running", "timestamp": datetime.utcnow().isoformat()}

def fetch_feed(url: str, max_items: int = 5) -> List[dict]:
    headers = {"User-Agent": USER_AGENT}
    try:
        parsed = feedparser.parse(url, agent=USER_AGENT)
        items = []
        entries = parsed.entries or []
        for e in entries[:max_items]:
            item = {
                "title": e.get("title", "").strip(),
                "link": e.get("link", "").strip(),
                "published": e.get("published", "") or e.get("updated", ""),
                "summary": (e.get("summary") or e.get("description") or "").strip(),
                "content": (e.get("content")[0].get("value") if e.get("content") else "") if isinstance(e.get("content"), list) else (e.get("content") or ""),
            }
            items.append(item)
        return items
    except Exception as exc:
        logger.exception("Feed fetch failed for %s: %s", url, str(exc))
        if errors_col:
            errors_col.insert_one({"type":"feed_fetch", "url": url, "error": str(exc), "ts": datetime.utcnow()})
        return []

def already_exists(link: str) -> bool:
    if not videos_col:
        return False
    return videos_col.find_one({"link": link}) is not None

@app.get("/news")
def get_news(limit: int = 10):
    if not videos_col:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = list(videos_col.find().sort("created_at", -1).limit(limit))
    # convert ObjectId and datetime to serializable
    for d in docs:
        d["_id"] = str(d.get("_id"))
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
    return docs

@app.get("/update")
def update(request: Request):
    # auth via header X-Admin-Secret
    header_secret = request.headers.get("X-Admin-Secret")
    if not ADMIN_SECRET:
        logger.error("ADMIN_SECRET not configured in environment")
        raise HTTPException(status_code=500, detail="Admin secret not configured")
    if header_secret != ADMIN_SECRET:
        logger.warning("Unauthorized update attempt: header_secret mismatch")
        raise HTTPException(status_code=403, detail="Forbidden")

    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    if not feeds:
        logger.error("No RSS_FEEDS configured")
        raise HTTPException(status_code=400, detail="No feeds configured")

    inserted_count = 0
    errors = []

    for feed in feeds:
        logger.info("Fetching feed: %s", feed)
        items = fetch_feed(feed, max_items=MAX_ITEMS_PER_FEED)
        logger.info("Found %d items in feed %s", len(items), feed)

        for item in items:
            link = item.get("link")
            if not link:
                logger.info("Skipping item without link")
                continue
            if already_exists(link):
                logger.info("Already exists — skip: %s", link)
                continue

            title = item.get("title") or ""
            content = item.get("content") or item.get("summary") or ""

            # Safety: trim long content for cost control
            if len(content) > 5000:
                content = content[:5000]

            # Summarize with Gemini (via REST wrapper)
            try:
                summary = summarize_text(title=title, content=content, model=GEMINI_MODEL, max_output_tokens=120)
                logger.info("Summary length: %d", len(summary or ""))
            except Exception as exc:
                logger.exception("Gemini summarize failed for %s: %s", link, str(exc))
                if errors_col:
                    errors_col.insert_one({"type":"gemini", "link": link, "error": str(exc), "ts": datetime.utcnow()})
                summary = ""

            doc = {
                "title": title,
                "link": link,
                "published": item.get("published"),
                "summary": summary,
                "source": feed,
                "raw_summary": item.get("summary"),
                "created_at": datetime.utcnow()
            }

            try:
                if videos_col:
                    videos_col.insert_one(doc)
                    inserted_count += 1
                    logger.info("Inserted: %s", link)
                else:
                    logger.error("videos_col not configured — cannot insert")
                    errors.append({"link": link, "error": "db not configured"})
            except Exception as exc:
                logger.exception("Mongo insert failed for %s: %s", link, str(exc))
                if errors_col:
                    errors_col.insert_one({"type":"mongo_insert", "link": link, "error": str(exc), "ts": datetime.utcnow()})
                errors.append({"link": link, "error": str(exc)})

            # small delay to avoid bursting API
            time.sleep(0.25)

    return {"status":"updated", "timestamp": datetime.utcnow().isoformat(), "inserted": inserted_count, "errors": errors}
