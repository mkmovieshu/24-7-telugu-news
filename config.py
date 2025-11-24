import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DB_NAME = os.getenv("DB_NAME", "shortnews")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RSS_FEEDS = [
    "https://www.eenadu.net/rss",
    "https://www.sakshi.com/rss",
    "https://www.hindu.com/rss",
    "https://www.indiatoday.in/rss/home",
    "https://www.bbc.com/telugu/index.xml",
    "https://www.amaravathipost.com/rss",
]
