# fetch_rss.py - Final Corrected Code using user's db.py
import os
import feedparser
from datetime import datetime
from urllib.parse import urlparse

# New: Use collections and client from the user's provided db.py (synchronous)
from db import news_collection 
from db import client as db_client # The MongoClient object
from summarize import summarize_item 

# -----------------------------------------------------------
# RSS Feeds Configuration
# -----------------------------------------------------------
FEEDS = []
rss_feeds_env = os.getenv("RSS_FEEDS")

if rss_feeds_env:
    # కామా ద్వారా వేరు చేయబడిన URL ల జాబితా
    FEEDS = [f.strip() for f in rss_feeds_env.split(',') if f.strip()]

if not FEEDS:
    print("Warning: No RSS feeds configured in RSS_FEEDS environment variable. Exiting.")
    import sys
    sys.exit(0)
# -----------------------------------------------------------


def normalize_item(entry):
    title = entry.get("title", "")
    link = entry.get("link", "")
    summary = entry.get("summary") or entry.get("description") or ""
    published = None
    try:
        published = entry.get("published_parsed")
        if published:
            published = datetime(*published[:6])
    except Exception:
        published = None
    image = ""
    # try enclosure or media content
    if "media_content" in entry and entry["media_content"]:
        image = entry["media_content"][0].get("url", "")
    if not image and "links" in entry:
        for l in entry["links"]:
            if l.get("type", "").startswith("image"):
                image = l.get("href")
                break
    return {"title": title, "link": link, "raw_summary": summary, "published": published, "image": image}


def upsert_entry(e):
    if not e.get("link"):
        return None
    # Use 'link' to check for existing news to prevent duplicates
    existing = news_collection.find_one({"link": e["link"]})
    now = datetime.utcnow()
    doc = {
        "title": e.get("title"),
        "link": e.get("link"),
        "raw_summary": e.get("raw_summary"),
        "published": e.get("published") or now,
        "image": e.get("image", ""),
        "source": urlparse(e.get("link")).netloc,
        "created_at": now,
    }
    if existing:
        # update summary if missing
        if not existing.get("summary"):
            s = summarize_item(doc)
            doc["summary"] = s
        # Only update the existing document (keep likes/dislikes)
        news_collection.update_one({"_id": existing["_id"]}, {"$set": doc})
        return existing["_id"]
    else:
        # create summary via AI or fallback
        doc["summary"] = summarize_item(doc)
        doc["likes"] = 0
        doc["dislikes"] = 0
        res = news_collection.insert_one(doc)
        return res.inserted_id

def fetch_all():
    print(f"Fetching {len(FEEDS)} RSS feeds...")
    for feed in FEEDS:
        try:
            d = feedparser.parse(feed)
            for entry in d.get("entries", []):
                upsert_entry(normalize_item(entry))
            print(f"Successfully fetched and processed feed: {feed}")
        except Exception as e:
            print(f"fetch error for {feed}: {e}")
            
    # Close the synchronous MongoClient connection used by this script
    db_client.close() 

if __name__ == "__main__":
    fetch_all()
    
