# config.py - తెలుగు న్యూస్ యాప్ కాన్ఫిగ్
import os

# మాంగోడీబీ
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "telugu_news")

# RSS ఫీడ్స్
RSS_FEEDS = [
    "https://www.eenadu.net/rss/rssfeed/andhrapradesh-news.xml",
    "https://www.sakshi.com/rss-feed/andhra-pradesh"
]

# AI
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# అప్లికేషన్
APP_NAME = "24/7 తెలుగు న్యూస్"
PORT = int(os.getenv("PORT", "8000"))

print(f"✅ {APP_NAME} కాన్ఫిగ్ లోడ్ అయింది")
