import os
import logging
import time
import subprocess
from pymongo import MongoClient
import feedparser
from datetime import datetime
from google import genai
from google.genai.errors import APIError

# ==============================================================================
# 1. సెటప్ (Setup)
# ==============================================================================

# లాగింగ్ సెటప్
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger('shortnews')

# RSS ఫీడ్ URLలు
RSS_FEEDS = [
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/andhra-pradesh.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/international.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/national.xml",
    "https://telugu.news18.com/commonfeeds/v1/tel/rss/telangana.xml",
    "https://www.teluguone.com/news/tonefeeds/latestnews/latestnews-25.rss",
]

# ------------------------------------------------------------------
# ✅ GEMINI API సెటప్
# ------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY environment variable not set.")
    # API key లేకుండా కోడ్ నడపడం ఆపడం
    exit(1)

try:
    # Gemini clientను సెట్ చేయండి
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    logger.error(f"Gemini Client initialization error: {e}")
    exit(1)

# ------------------------------------------------------------------
# MongoDB కనెక్షన్
# ------------------------------------------------------------------
try:
    MONGO_URI = os.getenv("MONGO_URI") 
    
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable not found.")
        
    MONGO_DB = os.getenv("MONGO_DB", "shortnews_db")
    client = MongoClient(MONGO_URI)
    client.admin.command('ping') 
    
    db = client[MONGO_DB]
    news_collection = db.news
    
    # లింక్ ద్వారా డూప్లికేట్‌లను నివారించడానికి ఇండెక్స్ సెట్ చేయండి
    news_collection.create_index("link", unique=True)
    
    # TTL ఇండెక్స్ సెటప్ (12 గంటల = 43200 సెకన్ల తర్వాత తొలగించడానికి)
    try:
        news_collection.create_index(
            "created_at", 
            expireAfterSeconds=43200, 
            background=True
        )
        logger.info("TTL index for 12-hour expiration set successfully on 'created_at'.")
    except Exception as e:
        logger.warning(f"TTL index creation failed (may already exist): {e}")
        
    logger.info("MongoDB కనెక్షన్ విజయవంతం.")

except Exception as e:
    logger.error(f"MongoDB కనెక్షన్ లోపం: {e}")
    exit(1)


# ==============================================================================
# 2. సహాయక ఫంక్షన్ (Helper Function)
# ==============================================================================

def generate_summary(content: str, title: str) -> str:
    """
    Gemini APIని ఉపయోగించి వార్త యొక్క సారాంశాన్ని (Summary) జనరేట్ చేస్తుంది.
    """
    prompt = f"""
    మీరు తెలుగు వార్తా సారాంశం రాసే నిపుణులు. 
    ఈ కింది వార్తా కంటెంట్ ఆధారంగా, 50 పదాలలో మించకుండా (కచ్చితంగా 3-4 వాక్యాలలో) ఒక ఆకర్షణీయమైన, స్పష్టమైన తెలుగు సారాంశాన్ని మాత్రమే రాయండి.
    
    వార్త శీర్షిక (Title): {title}
    వార్త కంటెంట్ (Content): {content[:1000]}... (పరిమితం చేయబడింది)
    
    సారాంశం (Summary):
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', # వేగవంతమైన సారాంశం కోసం
            contents=prompt,
            config={"temperature": 0.2} # స్థిరమైన ఫలితాల కోసం తక్కువ ఉష్ణోగ్రత
        )
        return response.text.strip()
    
    except APIError as e:
        logger.error(f"Gemini API లోపం: {e}")
        return "Gemini ద్వారా సారాంశం జనరేట్ చేయడంలో లోపం."
    except Exception as e:
        logger.error(f"సారాంశం జనరేట్ చేయడంలో ఊహించని లోపం: {e}")
        return "సారాంశం జనరేట్ చేయడంలో అంతర్గత లోపం."


# ==============================================================================
# 3. RSS ఫీడ్‌లను ఫెచ్ చేసి, స్టోర్ చేసే ఫంక్షన్
# ==============================================================================

def fetch_and_store():
    logger.info("Fetching %d RSS feeds...", len(RSS_FEEDS))
    
    # ------------------------------------------------------------------
    # ✅ పూర్తి కలెక్షన్ క్లీనింగ్
    # ------------------------------------------------------------------
    logger.info("Starting database cleanup: Deleting all existing news.")
    try:
        result = news_collection.delete_many({}) 
        logger.info(f"Successfully deleted {result.deleted_count} existing news items before fetching new ones.")
    except Exception as e:
        logger.error(f"Failed to delete old news: {e}")
    
    # ------------------------------------------------------------------

    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"Feed parsing error for {feed_url}: {feed.bozo_exception}")
                continue
            
            for entry in feed.entries:
                
                published_date = entry.published if hasattr(entry, 'published') else None
                
                # పూర్తి వార్త కంటెంట్‌ను సంగ్రహించడం
                content = entry.get('content', [{}])[0].get('value', entry.get('summary', ''))
                
                # ------------------------------------------------------------------
                # ✅ Gemini ద్వారా సారాంశాన్ని జనరేట్ చేయడం
                # ------------------------------------------------------------------
                summary_text = generate_summary(content, entry.title)
                
                # న్యూస్ ఐటమ్ డాక్యుమెంట్
                news_item = {
                    "title": entry.title,
                    "summary": summary_text,  # Gemini సారాంశం
                    "link": entry.link,
                    "source": feed_url,
                    "published": published_date, 
                    "likes": 0,
                    "dislikes": 0,
                    "created_at": datetime.utcnow() # TTL కొరకు జనరేషన్ టైమ్‌స్టాంప్
                }
                
                # డేటాబేస్‌లో ఇన్సర్ట్ చేయడం
                try:
                    news_collection.insert_one(news_item)
                    logger.info(f"కొత్త న్యూస్ ఇన్సర్ట్ చేయబడింది: {entry.title[:30]}... | సారాంశం: {summary_text[:30]}...")
                    
                except Exception as e:
                    if "duplicate key error" in str(e):
                        logger.debug(f"న్యూస్ ఇప్పటికే ఉంది, స్కిప్ చేయబడింది: {entry.title[:50]}...")
                    else:
                        logger.error(f"డేటాబేస్ లోపం: {e}")
                        
            logger.info(f"Successfully fetched and processed feed: {feed_url}")

        except Exception as e:
            logger.error(f"Error fetching/processing feed {feed_url}: {e}")

    logger.info("RSS ఫీడ్ ఫెచింగ్ పూర్తయింది.")
    client.close() 

# ==============================================================================
# 4. స్క్రిప్ట్ ఎగ్జిక్యూషన్
# ==============================================================================

if __name__ == "__main__":
    fetch_and_store()
    
