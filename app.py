import os
import time
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

# --- Load .env ---
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
USER_AGENT = os.getenv("FETCH_USER_AGENT", "Mozilla/5.0")

# Mongo
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
except Exception as e:
    logger.exception("MongoDB connect failed: %s", str(e))

# Gemini
from gemini_client import summarize_text

app = FastAPI(title="Short News API")


@app.get("/")
def status():
    return {"status": "Short News API Running", "timestamp": datetime.utcnow().isoformat()}


@app.get("/debug/ping_db")
def ping_db():
    try:
        info = client.server_info()
        return {"ok": True, "version": info.get("version")}
    except:
        return {"ok": False, "error": "DB not reachable"}


@app.get("/debug/check_feed")
def check_feed():
    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    url = feeds[0]
    items = fetch_feed(url, max_items=1)
    return {"ok": True, "feed": url, "found": len(items), "item": items[0] if items else None}


def fetch_feed(url: str, max_items: int = 5) -> List[dict]:
    parsed = feedparser.parse(url, agent=USER_AGENT)
    entries = parsed.entries or []
    items = []
    for e in entries[:max_items]:
        items.append({
            "title": e.get("title", "").strip(),
            "link": e.get("link", "").strip(),
            "published": e.get("published", ""),
            "summary": e.get("summary", "").strip(),
            "content": (e.get("content")[0].value if e.get("content") else "")
        })
    return items


def already_exists(link: str) -> bool:
    return videos_col.find_one({"link": link}) is not None


@app.get("/news")
def get_news(limit: int = 10):
    docs = list(videos_col.find().sort("created_at", -1).limit(limit))
    for d in docs:
        d["_id"] = str(d["_id"])
        if isinstance(d.get("created_at"), datetime):
            d["created_at"] = d["created_at"].isoformat()
    return docs


@app.get("/update")
def update(request: Request):
    if request.headers.get("X-Admin-Secret") != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    feeds = [f.strip() for f in RSS_FEEDS.split(",") if f.strip()]
    inserted = 0
    errors = []

    for f in feeds:
        items = fetch_feed(f, max_items=MAX_ITEMS_PER_FEED)
        for item in items:
            link = item["link"]
            if already_exists(link):
                continue

            title = item["title"]
            content = item["content"] or item["summary"]

            try:
                summary = summarize_text(title, content, GEMINI_MODEL, 120)
            except Exception as e:
                summary = ""
                errors.append(str(e))

            doc = {
                "title": title,
                "link": link,
                "published": item["published"],
                "summary": summary,
                "source": f,
                "raw_summary": item["summary"],
                "created_at": datetime.utcnow(),
            }

            videos_col.insert_one(doc)
            inserted += 1
            time.sleep(0.25)

    return {"status": "updated", "inserted": inserted, "errors": errors}


# --- UI Serve (static folder) ---
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/app")
def serve_app():
    return FileResponse("static/app.html")
