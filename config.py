import os
from dotenv import load_dotenv

# Load .env locally; on Render, env panel values will override
load_dotenv()

# === MongoDB ===
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "news_db")

# === Admin auth ===
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

# === Gemini / Google Generative Language ===
# OFFICIAL ENV VAR NAME – DON'T CHANGE
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Python-side alias for backwards compatibility
GEMINI_API_KEY = GOOGLE_API_KEY

# Model to use for summaries
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")

# === RSS feeds ===
RSS_FEEDS = os.getenv(
    "RSS_FEEDS",
    "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml",
).split(",")
