# fetch_rss.py
import os
import feedparser
from datetime import datetime
from urllib.parse import urlparse
from db import news_collection
from summarize import summarize_item
from bson.objectid import ObjectId
import logging

logger = logging.getLogger("short-news-api")

# వాస్తవ తెలుగు న్యూస్ RSS ఫీడ్స్
FEEDS = [
    # ప్రముఖ తెలుగు వార్తా సైట్లు
    "https://www.eenadu.net/rss/rssfeed/andhrapradesh-news.xml",
    "https://www.sakshi.com/rss-feed/andhra-pradesh",
    "https://telugu.samayam.com/rssfeeds/telugu-news.xml",
    "https://www.ntnews.com/rss/latest-news",
    "https://www.andhrajyothy.com/rssfeed/andhra-pradesh",
    "https://www.hmtvlive.com/rss/latest-news",
    "https://telugu.news18.com/rss/andhra-pradesh.xml",
    "https://www.v6news.tv/rss/latest-news",
    "https://www.tupaki.com/rss/latest-news",
    "https://www.abc.net.au/news/feed/5290372/rss.xml",  # తెలుగు వార్తలు
]

def normalize_item(entry):
    """RSS ఎంట్రీని మా ఫార్మాట్‌కు మార్చడం"""
    title = entry.get("title", "").strip()
    link = entry.get("link", "").strip()
    summary = entry.get("summary") or entry.get("description") or ""
    
    # HTML ట్యాగ్‌లను తొలగించడం
    import re
    summary = re.sub(r'<[^>]+>', '', summary)
    
    published = None
    try:
        published = entry.get("published_parsed")
        if published:
            published = datetime(*published[:6])
        elif entry.get("updated_parsed"):
            published = datetime(*entry.get("updated_parsed")[:6])
    except Exception as e:
        logger.debug(f"Date parsing error: {e}")
        published = datetime.utcnow()
    
    # ఇమేజ్ URL ని పొందడం
    image = ""
    if "media_content" in entry and entry["media_content"]:
        image = entry["media_content"][0].get("url", "")
    elif "links" in entry:
        for link_obj in entry["links"]:
            if link_obj.get("type", "").startswith("image"):
                image = link_obj.get("href", "")
                break
    elif "enclosures" in entry:
        for enc in entry["enclosures"]:
            if enc.get("type", "").startswith("image"):
                image = enc.get("href", "")
                break
    
    return {
        "title": title,
        "link": link,
        "raw_summary": summary[:500],  # పొడవును పరిమితం చేయడం
        "published": published,
        "image": image,
        "source_domain": urlparse(link).netloc if link else ""
    }

def is_duplicate_entry(link, title):
    """డూప్లికేట్ న్యూస్ తనిఖీ"""
    try:
        existing = news_collection.find_one({
            "$or": [
                {"link": link},
                {"title": {"$regex": f"^{re.escape(title[:50])}", "$options": "i"}}
            ]
        })
        return existing is not None
    except Exception as e:
        logger.error(f"Duplicate check error: {e}")
        return False

def upsert_entry(entry):
    """న్యూస్ ఎంట్రీని డేటాబేస్‌లో నవీకరించడం లేదా జోడించడం"""
    if not entry.get("link") or not entry.get("title"):
        logger.warning(f"Skipping entry without link/title: {entry.get('title')}")
        return None
    
    # డూప్లికేట్ తనిఖీ
    if is_duplicate_entry(entry["link"], entry["title"]):
        logger.info(f"Duplicate found: {entry['title'][:50]}...")
        return None
    
    now = datetime.utcnow()
    
    # డాక్యుమెంట్ ని తయారు చేయడం
    doc = {
        "title": entry.get("title", ""),
        "link": entry.get("link", ""),
        "raw_summary": entry.get("raw_summary", ""),
        "published": entry.get("published") or now,
        "image": entry.get("image", ""),
        "source": entry.get("source_domain", ""),
        "created_at": now,
        "likes": 0,
        "dislikes": 0,
        "comment_count": 0,
        "language": "te",  # తెలుగు
        "category": "general"
    }
    
    try:
        # AI సమ్మరీ జనరేట్ చేయడం
        summary_text = summarize_item(doc)
        doc["summary"] = summary_text
        
        # డేటాబేస్‌లో ఇన్సర్ట్ చేయడం
        result = news_collection.insert_one(doc)
        logger.info(f"Inserted news: {doc['title'][:50]}... (ID: {result.inserted_id})")
        
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error inserting entry: {e}")
        return None

def fetch_all_feeds(max_items=30):
    """అన్ని RSS ఫీడ్స్ నుండి న్యూస్ పొందడం"""
    total_inserted = 0
    
    for feed_url in FEEDS:
        if total_inserted >= max_items:
            break
            
        try:
            logger.info(f"Fetching feed: {feed_url}")
            feed = feedparser.parse(feed_url)
            
            if feed.bozo and feed.bozo_exception:
                logger.warning(f"Feed error for {feed_url}: {feed.bozo_exception}")
                continue
            
            items_added = 0
            for entry in feed.entries[:10]:  # ప్రతి ఫీడ్ నుండి 10 మాత్రమే
                if total_inserted >= max_items:
                    break
                    
                try:
                    normalized = normalize_item(entry)
                    if upsert_entry(normalized):
                        items_added += 1
                        total_inserted += 1
                        
                        if items_added >= 3:  # ప్రతి ఫీడ్ నుండి గరిష్టంగా 3
                            break
                except Exception as e:
                    logger.error(f"Error processing entry: {e}")
                    continue
            
            logger.info(f"Added {items_added} items from {feed_url}")
            
        except Exception as e:
            logger.error(f"Failed to fetch feed {feed_url}: {e}")
            continue
    
    logger.info(f"Total news fetched: {total_inserted}")
    return total_inserted

if __name__ == "__main__":
    # రోజుకు ఒకసారి రన్ చేయడానికి
    fetch_all_feeds(max_items=50)
