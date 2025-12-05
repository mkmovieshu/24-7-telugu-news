# fetch_rss.py - సరిచేసిన పూర్తి కోడ్ (న్యూస్ ఫీడ్స్ జత చేయబడ్డాయి)
import os
import feedparser
from datetime import datetime
from urllib.parse import urlparse
from db import news_collection
from summarize import summarize_item
from bson.objectid import ObjectId

# put your feeds in environment or edit list
FEEDS = [
    # === మీ నిజమైన తెలుగు న్యూస్ RSS ఫీడ్ లింక్‌లను ఇక్కడ జత చేయండి ===
    # ఇక్కడ కొన్ని ఉదాహరణ లింక్‌లు ఇవ్వబడ్డాయి, వీటిని మీరు మీ అవసరాలకు అనుగుణంగా మార్చుకోవచ్చు.
    "https://telugu.samayam.com/rssfeedsdefault.cms", 
    "https://telugu.news18.com/rss/telugu-news.xml",
    "https://www.eenadu.net/rss_feed",  
    
    # పాత ఉదాహరణ లింక్:
    "https://www.ntnews.com/rss",   
]

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
    for feed in FEEDS:
        try:
            d = feedparser.parse(feed)
            for entry in d.get("entries", []):
                e = normalize_item(entry)
                upsert_entry(e)
        except Exception as e:
            # లోపం ఎందుకు వచ్చిందో తెలుసుకోవడానికి
            print(f"fetch error for {feed}: {e}") 

if __name__ == "__main__":
    fetch_all()
    
