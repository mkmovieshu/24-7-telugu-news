import os
import logging
import time
import subprocess
from pymongo import MongoClient
import feedparser

# ==============================================================================
# 1. సెటప్ (Setup)
# ==============================================================================

# లాగింగ్ సెటప్
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger('shortnews')

# RSS ఫీడ్ URLలు
# ఈ లిస్ట్‌ను మీ ప్రాజెక్ట్ అవసరాలకు అనుగుణంగా మార్చండి
RSS_FEEDS = [
    "https://www.hindustantimes.com/feeds/rss/entertainment/telugu-cinema/rssfeed.xml",
    "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml",
    "https://www.teluguone.com/news/tonefeeds/latestnews/latestnews-25.rss",
]

# MongoDB కనెక్షన్
try:
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB = os.getenv("MONGO_DB", "shortnews_db")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    news_collection = db.news
    
    # లింక్ ద్వారా డూప్లికేట్‌లను నివారించడానికి ఇండెక్స్ సెట్ చేయండి
    news_collection.create_index("link", unique=True)
    logger.info("MongoDB కనెక్షన్ విజయవంతం.")

except Exception as e:
    logger.error(f"MongoDB కనెక్షన్ లోపం: {e}")
    # కనెక్షన్ లేకపోతే స్క్రిప్ట్ ఆగిపోతుంది
    exit(1)


# ==============================================================================
# 2. RSS ఫీడ్‌లను ఫెచ్ చేసి, స్టోర్ చేసే ఫంక్షన్
# ==============================================================================

def fetch_and_store():
    logger.info("Fetching %d RSS feeds...", len(RSS_FEEDS))

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing error for {feed_url}: {feed.bozo_exception}")
                continue
            
            for entry in feed.entries:
                
                # 'pubDate' ఎలిమెంట్ RSS లో 'published' గా మారుతుంది
                published_date = entry.published if hasattr(entry, 'published') else None
                
                # న్యూస్ ఐటమ్ డాక్యుమెంట్
                news_item = {
                    "title": entry.title,
                    "summary": None, # సారాంశం మొదట్లో None ఉంటుంది
                    "link": entry.link,
                    "source": feed_url,
                    # ✅ ఇక్కడ కొత్త 'published' ఫీల్డ్‌ను జతచేశాం
                    "published": published_date, 
                    "likes": 0,
                    "dislikes": 0
                }
                
                # డూప్లికేట్‌లను నివారించడానికి, లింక్ ఆధారంగా ఒకే ఒక్కసారి ఇన్సర్ట్ చేయండి
                try:
                    # news_collection.insert_one(news_item)
                    # upsert=True: లింక్ ఉంటే అప్డేట్ చేస్తుంది, లేదంటే కొత్తది ఇన్సర్ట్ చేస్తుంది.
                    # అయితే ఇక్కడ కేవలం కొత్త వాటిని ఇన్సర్ట్ చేయడమే ఉత్తమం
                    news_collection.insert_one(news_item)
                    logger.info(f"కొత్త న్యూస్ ఇన్సర్ట్ చేయబడింది: {entry.title[:50]}...")
                    
                except Exception as e:
                    # DuplicateKeyError: లింక్ ఇప్పటికే డేటాబేస్‌లో ఉంది అని అర్థం
                    if "duplicate key error" in str(e):
                        logger.debug(f"న్యూస్ ఇప్పటికే ఉంది, స్కిప్ చేయబడింది: {entry.title[:50]}...")
                    else:
                        logger.error(f"డేటాబేస్ లోపం: {e}")
                        
            logger.info(f"Successfully fetched and processed feed: {feed_url}")

        except Exception as e:
            logger.error(f"Error fetching/processing feed {feed_url}: {e}")

    logger.info("RSS ఫీడ్ ఫెచింగ్ పూర్తయింది.")

# ==============================================================================
# 3. స్క్రిప్ట్ ఎగ్జిక్యూషన్
# ==============================================================================

if __name__ == "__main__":
    fetch_and_store()
    
