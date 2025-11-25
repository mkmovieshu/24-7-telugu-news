import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PORT = int(os.getenv("PORT", "10000"))
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "change_this")
FREE_MODE = os.getenv("FREE_MODE", "false").lower() in ("1","true","yes")
RSS_FEEDS = [
    "https://www.eenadu.net/rss",
    "https://www.sakshi.com/rss",
    "https://www.hindu.com/rss",
    "https://www.indiatoday.in/rss/home",
    "https://www.bbc.com/telugu/index.xml",
    "https://www.amaravathipost.com/rss",
]
