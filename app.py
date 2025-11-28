# app.py
import os
import time
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
# ...నీ ఇతర imports 그대로...

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("short-news-api")

# Environment
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RSS_FEEDS = os.getenv("RSS_FEEDS", "")
MAX_ITEMS_PER_FEED = int(os.getenv("MAX_ITEMS_PER_FEED", "3"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")
USER_AGENT = os.getenv("FETCH_USER_AGENT", "Mozilla/5.0 (X11; Linux x86_64)")

if not MONGO_URL:
    logger.warning("MONGO_URL not set - DB operations will fail.")
if not GOOGLE_API_KEY:
    logger.warning("GOOGLE_API_KEY not set - Gemini calls will fail.")
if not RSS_FEEDS:
    logger.warning("RSS_FEEDS not set - update will error without feeds.")

# Mongo connection
client = None
db = None
videos_col = None
errors_col = None
try:
    if MONGO_URL is not None:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=10000)
        db = client[MONGO_DB_NAME]
        # IMPORTANT: don't use "if db" – compare with None
        if db is not None:
            videos_col = db["videos"]
            errors_col = db["errors"]
        client.admin.command("ping")
        logger.info("MongoDB connected")
except Exception as e:
    logger.exception("MongoDB connect failed: %s", str(e))
    client = None
    db = None
    videos_col = None
    errors_col = None

# Use our REST gemini wrapper
from gemini_client import summarize_text

app = FastAPI(title="Short News API")

@app.get("/")
def status():
    return {"status": "Short News API Running", "timestamp": datetime.utcnow().isoformat()}

# Debug helpers
@app.get("/debug/ping_db")
def ping_db():
    try:
        if client is None:
            return {"ok": False, "error": "Mongo client not configured"}
        info = client.server_info()
        return {"ok": True, "version": info.get("version")}
    except Exception as e:
        return {"ok": False, "error": str(e)}

@app.get("/debug/check_feed")
def check_feed():
    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    if not feeds:
        return {"ok": False, "error": "RSS_FEEDS empty"}
    sample = feeds[0]
    items = fetch_feed(sample, max_items=1)
    return {"ok": True, "feed": sample, "found": len(items), "item": items[0] if items else None}

def fetch_feed(url: str, max_items: int = 5) -> List[dict]:
    try:
        parsed = feedparser.parse(url, agent=USER_AGENT)
        entries = parsed.entries or []
        items = []
        for e in entries[:max_items]:
            item = {
                "title": e.get("title","").strip(),
                "link": e.get("link","").strip(),
                "published": e.get("published",""),
                "summary": (e.get("summary") or "").strip(),
                "content": (e.get("content")[0].get("value") if e.get("content") else "") if isinstance(e.get("content"), list) else (e.get("content") or "")
            }
            items.append(item)
        return items
    except Exception as exc:
        logger.exception("Feed fetch failed for %s: %s", url, str(exc))
        if errors_col is not None:
            errors_col.insert_one({"type":"feed_fetch", "url": url, "error": str(exc), "ts": datetime.utcnow()})
        return []

def already_exists(link: str) -> bool:
    if videos_col is None:
        return False
    return videos_col.find_one({"link": link}) is not None

@app.get("/news")
def get_news(limit: int = 10):
    if videos_col is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    docs = list(videos_col.find().sort("created_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d.get("_id"))
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
    return docs

@app.get("/update")
def update(request: Request):
    header_secret = request.headers.get("X-Admin-Secret")
    if ADMIN_SECRET is None:
        logger.error("ADMIN_SECRET not configured in environment")
        raise HTTPException(status_code=500, detail="Admin secret not configured")
    if header_secret != ADMIN_SECRET:
        logger.warning("Unauthorized update attempt")
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

            if len(content) > 5000:
                content = content[:5000]

            try:
                summary = summarize_text(title=title, content=content, model=GEMINI_MODEL, max_output_tokens=120)
                logger.info("Summary length: %d", len(summary or ""))
            except Exception as exc:
                logger.exception("Gemini summarize failed for %s: %s", link, str(exc))
                if errors_col is not None:
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
                if videos_col is not None:
                    videos_col.insert_one(doc)
                    inserted_count += 1
                    logger.info("Inserted: %s", link)
                else:
                    logger.error("videos_col not configured — cannot insert")
                    errors.append({"link": link, "error": "db not configured"})
            except Exception as exc:
                logger.exception("Mongo insert failed for %s: %s", link, str(exc))
                if errors_col is not None:
                    errors_col.insert_one({"type":"mongo_insert", "link": link, "error": str(exc), "ts": datetime.utcnow()})
                errors.append({"link": link, "error": str(exc)})

            time.sleep(0.25)

    return {
        "status": "updated",
        "timestamp": datetime.utcnow().isoformat(),
        "inserted": inserted_count,
        "errors": errors,
    }
    from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Route for UI
@app.get("/app")
def serve_ui():
    return FileResponse("static/app.html")
