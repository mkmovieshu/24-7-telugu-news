import os
import time
import re
import logging
from datetime import datetime
from typing import List

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from dotenv import load_dotenv
import feedparser
from pymongo import MongoClient

from gemini_client import summarize_text

# --- Load .env ---
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("short-news-api")

# === ENVIRONMENT (DON'T RENAME THESE KEYS) ===
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
RSS_FEEDS = os.getenv(
    "RSS_FEEDS",
    "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml"
)
MAX_ITEMS_PER_FEED = int(os.getenv("MAX_ITEMS_PER_FEED", "3"))
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")
USER_AGENT = os.getenv("FETCH_USER_AGENT", "Mozilla/5.0")

# === MongoDB CONNECTION ===
client = None
db = None
videos_col = None
errors_col = None
try:
    if MONGO_URL:
        client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=10000)
        db = client[MONGO_DB_NAME]
        videos_col = db["videos"]
        errors_col = db["errors"]
        client.admin.command("ping")
        logger.info("MongoDB connected")
    else:
        logger.warning("MONGO_URL not set")
except Exception as e:
    logger.exception("MongoDB connect failed: %s", str(e))


# === HELPERS ===

def _fetch_feed(url: str, max_items: int = 5) -> List[dict]:
    parsed = feedparser.parse(url, agent=USER_AGENT)
    entries = parsed.entries or []
    items = []
    for e in entries[:max_items]:
        items.append(
            {
                "title": e.get("title", "").strip(),
                "link": e.get("link", "").strip(),
                "published": e.get("published", ""),
                "summary": e.get("summary", "").strip(),
                "content": (e.get("content")[0].value if e.get("content") else ""),
            }
        )
    return items


def _already_exists(link: str) -> bool:
    if not videos_col:
        return False
    return videos_col.find_one({"link": link}) is not None


def _clean_telugu_summary(text: str) -> str:
    """
    summary లో ఉన్న English letters & ఇతర symbols తొలగించి
    తెలుగు + digits + basic punctuation మాత్రమే ఉంచుతుంది.
    """
    if not isinstance(text, str) or not text:
        return ""

    # తెలుగు unicode: \u0C00-\u0C7F
    cleaned = re.sub(
        r"[^0-9\u0C00-\u0C7F\s\.\,\?\!\-\:\;\"\'\(\)]",
        " ",
        text,
    )
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


# === FASTAPI APP ===

app = FastAPI(title="Short News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === ROUTES ===

@app.get("/")
def status():
    return {
        "status": "Short News API Running",
        "timestamp": datetime.utcnow().isoformat(),
    }


@app.get("/debug/ping_db")
def ping_db():
    if not client:
        return {"ok": False, "error": "client not configured"}
    try:
        info = client.server_info()
        return {"ok": True, "version": info.get("version")}
    except Exception as e:
        return {"ok": False, "error": str(e)}


@app.get("/debug/check_feed")
def check_feed():
    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    if not feeds:
        return {"ok": False, "error": "RSS_FEEDS empty"}
    url = feeds[0]
    items = _fetch_feed(url, max_items=1)
    return {
        "ok": True,
        "feed": url,
        "found": len(items),
        "item": items[0] if items else None,
    }


@app.get("/news")
def get_news(limit: int = 10):
    if not videos_col:
        raise HTTPException(status_code=500, detail="DB not configured")

    docs = list(videos_col.find().sort("created_at", -1).limit(limit))

    for d in docs:
        # stringify _id
        d["_id"] = str(d["_id"])
        # ISO format for created_at
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
        # CLEAN summary → Telugu only
        if "summary" in d and isinstance(d["summary"], str):
            d["summary"] = _clean_telugu_summary(d["summary"])

    return docs


@app.get("/update")
def update(request: Request):
    if request.headers.get("X-Admin-Secret") != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    if not feeds:
        logger.warning("RSS_FEEDS not set - update will error without feeds.")
        return {"status": "no_feeds", "inserted": 0, "errors": ["RSS_FEEDS empty"]}

    inserted = 0
    errors = []

    for f in feeds:
        logger.info("Fetching feed: %s", f)
        items = _fetch_feed(f, max_items=MAX_ITEMS_PER_FEED)
        logger.info("Found %d items in feed %s", len(items), f)

        for item in items:
            link = item["link"]
            if not link:
                continue

            if _already_exists(link):
                logger.info("Already exists — skip: %s", link)
                continue

            title = item["title"]
            content = item["content"] or item["summary"]

            summary = ""
            try:
                summary = summarize_text(
                    title=title,
                    content=content,
                    model=GEMINI_MODEL,
                    max_output_tokens=140,
                )
            except Exception as e:
                logger.exception("Gemini summarize exception: %s", e)
                errors.append(str(e))

            # DBలో raw_summary English తో ఉన్నా పర్వాలేదు
            doc = {
                "title": title,
                "link": link,
                "published": item["published"],
                "summary": summary,
                "source": f,
                "raw_summary": item["summary"],
                "created_at": datetime.utcnow(),
            }

            if videos_col:
                videos_col.insert_one(doc)
                inserted += 1
                logger.info("Inserted: %s", link)

            time.sleep(0.25)

    return {
        "status": "updated",
        "timestamp": datetime.utcnow().isoformat(),
        "inserted": inserted,
        "errors": errors,
    }


# === STATIC UI (Stage 3) ===

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/app")
def serve_app():
    return FileResponse("static/app.html")
