import feedparser
import hashlib
import logging
import os
from pymongo import errors as mongo_errors # MongoDB లోపం కోసం
from datetime import datetime
from summarize import summarize_news

# Import DB connection and collection from db.py
from db import news_collection as news_col, client, DB_NAME

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger("fetch_rss")

try:
    # కనెక్షన్‌ను తనిఖీ చేయడానికి ఒక చిన్న ఆపరేషన్ చేయండి
    client.admin.command('ping') 
    log.info("MongoDB కనెక్షన్ విజయవంతం: DB='%s'", DB_NAME)

except mongo_errors.ConnectionFailure as e:
    log.error("MongoDB కనెక్షన్ లోపం: %s", e)
    exit(1)
except Exception as e:
    log.error("సాధారణ కనెక్షన్ లోపం: %s", e)
    exit(1)


# ✅ మెరుగైన RSS ఫీడ్ URLలు
RSS_FEEDS = [
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/andhra-pradesh.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/international.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/national.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/telangana.xml",
]

# ... make_hash ఫంక్షన్ మీ కోడ్ నుండి ...
def make_hash(title: str, source: str) -> str:
    base = f"{source}|{title.strip().lower()}"
    return hashlib.sha256(base.encode("utf-8")).hexdigest()

def fetch():
    for feed_url in RSS_FEEDS:
        log.info("ఫెచింగ్: %s", feed_url)
        feed = feedparser.parse(feed_url)

        if feed.status not in (200, 301, 302) and feed.status != 304:
            log.warning("ఫీడ్ లోడ్ కాలేదు (Status: %s): %s", feed.status, feed_url)
            continue
            
        source = feed.feed.get("title", "unknown")

        for entry in feed.entries:
            try:
                title = entry.get("title", "").strip()
                link = entry.get("link", "").strip()

                if not title or not link:
                    continue

                h = make_hash(title, source)

                # 🔒 HARD STOP: DUPLICATE
                if news_col.find_one({"hash": h}):
                    log.info("SKIP (cached): %s", title)
                    continue

                content = entry.get("summary", "") or entry.get("description", "")

                # 🧠 AI only if really needed
                # 🚨 గమనిక: summarize_news ఫంక్షన్ మీ summarize.py ఫైల్‌లో ఉండాలి
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
                log.info("INSERTED: %s | AI=%s", title[:50], ai_used)

            except Exception as e:
                log.error("న్యూస్ ఎంట్రీ ప్రాసెసింగ్‌లో లోపం: %s", e)


if __name__ == "__main__":
    fetch()
