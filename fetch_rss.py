import os
import logging
import time
from pymongo import MongoClient, ASCENDING
import feedparser
from datetime import datetime, timedelta, timezone

# 🚨 కొత్తగా చేర్చబడింది: Gemini API
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

# MongoDB కనెక్షన్
try:
    MONGO_URI = os.getenv("MONGO_URI") 
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
    
    if not MONGO_URI:
        raise ValueError("MONGO_URI environment variable not found. Please set the MONGO_URI in your environment variables.")
    
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB_NAME]
    news_collection = db["news"]
    logger.info("MongoDB కనెక్షన్ విజయవంతం.")

except Exception as e:
    logger.error(f"MongoDB కనెక్షన్ లోపం: {e}")
    # కనెక్షన్ లోపం ఉంటే స్క్రిప్ట్‌ను ఆపివేయండి
    exit(1) 

# Gemini API సెటప్
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY environment variable not found. Summaries will be empty.")
    gemini_client = None
else:
    # 🚨 Gemini క్లయింట్‌ను సెటప్ చేయండి
    try:
        gemini_client = genai.Client(api_key=GEMINI_API_KEY)
        logger.info("Gemini API క్లయింట్ సెటప్ చేయబడింది.")
    except Exception as e:
        logger.error(f"Gemini క్లయింట్ ప్రారంభించడంలో లోపం: {e}")
        gemini_client = None


# ==============================================================================
# 2. ఫంక్షన్స్ (Functions)
# ==============================================================================

def generate_summary(text):
    """Gemini API ని ఉపయోగించి తెలుగులో సారాంశాన్ని జనరేట్ చేస్తుంది."""
    if not gemini_client:
        return "సారాంశం జనరేటర్ అందుబాటులో లేదు."

    # Gemini ప్రాంప్ట్
    prompt = f"""
    మీరు 24/7 తెలుగు షార్ట్ న్యూస్ ఛానెల్ కోసం పని చేసే AI అసిస్టెంట్‌గా వ్యవహరించండి.
    కింద ఇచ్చిన వార్త యొక్క కంటెంట్‌ను (content) **తెలుగులో** 30 నుండి 50 పదాలలో చదివేందుకు సులభంగా ఉండే **సారాంశాన్ని (summary)** మాత్రమే జనరేట్ చేయండి.
    
    వార్త కంటెంట్:
    ---
    {text}
    ---
    """
    
    try:
        response = gemini_client.models.generate_content(
            model='gemini-2.5-flash', # వేగవంతమైన, తక్కువ ఖర్చుతో కూడిన మోడల్
            contents=prompt
        )
        return response.text.strip()
    except APIError as e:
        logger.error(f"Gemini API లోపం: {e}")
        return "సారాంశం జనరేట్ చేయడంలో API లోపం సంభవించింది."
    except Exception as e:
        logger.error(f"సారాంశం జనరేట్ చేయడంలో ఊహించని లోపం: {e}")
        return "సారాంశం జనరేట్ చేయడంలో లోపం."

def fetch_and_store():
    """RSS ఫీడ్‌లను ఫెచ్ చేసి, సారాంశాలను జనరేట్ చేసి, డేటాబేస్‌లో సేవ్ చేస్తుంది."""
    logger.info("RSS ఫీడ్ ఫెచింగ్ ప్రారంభమైంది.")
    
    # 🚨 ముఖ్యమైన మార్పు 1: ప్రతిసారి పాత వార్తలను పూర్తిగా తొలగించండి
    # దీని వలన మీరు మునుపటి సమస్యను పరిష్కరించారు.
    try:
        news_collection.delete_many({})
        logger.info("డేటాబేస్ నుండి పాత వార్తలు విజయవంతంగా తొలగించబడ్డాయి.")
    except Exception as e:
        logger.error(f"పాత వార్తలను తొలగించడంలో లోపం: {e}")

    # 🚨 ముఖ్యమైన మార్పు 2: 12 గంటల తర్వాత ఆటో-డిలీట్ కోసం TTL ఇండెక్స్‌ను సెట్ చేయండి
    try:
        # expireAfterSeconds=43200 (12 గంటలు = 12 * 60 * 60 సెకన్లు)
        news_collection.create_index(
            [("created_at", ASCENDING)], 
            expireAfterSeconds=43200, 
            background=True
        )
        logger.info("TTL ఇండెక్స్ (12 గంటలు) విజయవంతంగా సెట్ చేయబడింది.")
    except Exception as e:
        logger.error(f"TTL ఇండెక్స్ సెట్ చేయడంలో లోపం: {e}")


    for feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # తేదీని పార్స్ చేయండి
                published_date = datetime.utcnow() # డిఫాల్ట్: ఇప్పుడు
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed), 
                        tz=timezone.utc
                    ).replace(tzinfo=None)

                # 🚨 ముఖ్యమైన మార్పు 3: Gemini API ని ఉపయోగించి సారాంశాన్ని జనరేట్ చేయండి
                full_text = getattr(entry, 'description', getattr(entry, 'summary', entry.title))
                
                # సారాంశాన్ని జనరేట్ చేయండి
                summary_text = generate_summary(full_text)

                news_item = {
                    "title": entry.title,
                    "summary": summary_text, # ✅ ఇక్కడ సారాంశం జత చేయబడింది
                    "link": entry.link,
                    "source": feed_url,
                    "published": published_date, 
                    "created_at": datetime.utcnow(), # TTL కోసం ఈ ఫీల్డ్ అవసరం
                    "likes": 0,
                    "dislikes": 0
                }
                
                # డూప్లికేట్‌లను నివారించడానికి
                # (మేము ఇప్పటికే కలెక్షన్‌ను క్లీన్ చేసాము, కాబట్టి ఈ డూప్లికేట్ చెక్ ఇక్కడ అనవసరం, కానీ ఉండటం మంచిది)
                try:
                    news_collection.insert_one(news_item)
                    logger.info(f"కొత్త న్యూస్ ఇన్సర్ట్ చేయబడింది: {entry.title[:50]}...")
                    
                except Exception as e:
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
    
