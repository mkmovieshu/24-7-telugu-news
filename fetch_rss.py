import feedparser
import hashlib
import logging
import os
from pymongo import MongoClient
from datetime import datetime
from summarize import summarize_news

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("fetch_rss")

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
news_col = db["news"]

RSS_FEEDS = [
    "https://telugu.hindustantimes.com/rss",
    "https://www.andhrajyothy.com/rss",
    "https://www.eenadu.net/rss"
]

def make_hash(title: str, source: str) -> str:
    base = f"{source}|{title.strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def fetch():
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            source = feed.feed.get("title", "unknown")

            if not title or not link:
                continue

            h = make_hash(title, source)

            # 🔒 HARD STOP: DUPLICATE
            if news_col.find_one({"hash": h}):
                log.info("SKIP (cached): %s", title)
                continue

            content = entry.get("summary", "") or entry.get("description", "")

            # 🧠 AI only if really needed
            summary, ai_used = summarize_news(title, content)

            doc = {
                "title": title,
                "summary": summary,
                "source": source,
                "link": link,
                "hash": h,
                "ai_used": ai_used,
                "created_at": datetime.utcnow()
            }

            news_col.insert_one(doc)
            log.info("INSERTED: %s | AI=%s", title, ai_used)

if __name__ == "__main__":
    fetch()
