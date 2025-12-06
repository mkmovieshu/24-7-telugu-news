# fetch_rss.py - RSS ఫీడ్స్ లోడ్ చేయడానికి మరియు ప్రాసెస్ చేయడానికి
import os
import feedparser
from datetime import datetime
from urllib.parse import urlparse
from db import news_collection
from summarize import summarize_item
from bson.objectid import ObjectId

# ✅ FIX 1: ENVIRONMENT VARIABLE నుండి ఫీడ్‌లను లోడ్ చేయండి
RSS_FEEDS_ENV = os.getenv("RSS_FEEDS")

if RSS_FEEDS_ENV:
    FEEDS = [f.strip() for f in RSS_FEEDS_ENV.split(',') if f.strip()]
else:
    # Environment variable సెట్ చేయకపోతే, ఈ డిఫాల్ట్ ఫీడ్‌లను వాడుతుంది.
    FEEDS = [
        "https://www.hindustantimes.com/feeds/rss/entertainment/telugu-cinema/rssfeed.xml",
        "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml",
        "https://www.teluguone.com/news/tonefeeds/latestnews/latestnews-25.rss"
    ]

# ----------------------------------------------------------------------
# normalize_item, upsert_entry, fetch_all ఫంక్షన్లు పాతవే

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
        news_collection.update_one({"_id": existing["_id"]}, {"$set": doc})
        return existing["_id"]
    else:
        # create summary via AI or fallback
        doc["summary"] = summarize_item(doc)
        res = news_collection.insert_one(doc)
        return res.inserted_id

def fetch_all():
    # ✅ FIX 2: ఫీడ్స్ లిస్ట్ ఖాళీగా ఉంటే ఆగిపోవాలి
    if not FEEDS:
        print("Warning: FEEDS list is empty. Cannot fetch any news.")
        return

    print(f"Fetching {len(FEEDS)} RSS feeds...")
    for feed in FEEDS:
        try:
            d = feedparser.parse(feed)
            inserted_count = 0
            for entry in d.get("entries", []):
                e = normalize_item(entry)
                if upsert_entry(e):
                    inserted_count += 1
            print(f"Successfully fetched and processed feed: {feed}")
        except Exception as e:
            print(f"Error fetching feed {feed}: {e}")

if __name__ == "__main__":
    fetch_all()
    
