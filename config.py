import os
import logging
from dotenv import load_dotenv

# Load .env if present (local dev), Koyeb/Render use real env vars
load_dotenv()

log = logging.getLogger("short-news-api")

# MongoDB
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    log.warning("MONGO_URL not set. Mongo connection will fail.")

# Admin secret (for /update)
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "9xV!pG72Qr3mK")

# RSS feeds (comma separated)
_raw_feeds = os.getenv("RSS_FEEDS", "").strip()
if _raw_feeds:
    RSS_FEEDS = [u.strip() for u in _raw_feeds.split(",") if u.strip()]
else:
    RSS_FEEDS = []

# Gemini / Google AI
# IMPORTANT: we read GOOGLE_API_KEY from env,
# but also expose it as GEMINI_API_KEY for old code.
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_API_KEY = GOOGLE_API_KEY  # alias so old imports still work

# Default model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

# Optional log level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.getLogger().setLevel(LOG_LEVEL)
