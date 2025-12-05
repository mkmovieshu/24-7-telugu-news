# config.py
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Core Database
    MONGO_URL: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "telugu_news"
    
    # Security
    ADMIN_SECRET: str = "change-this-in-production"
    
    # RSS Feeds (comma separated)
    RSS_FEEDS: str = (
        "https://www.eenadu.net/rss/rssfeed/andhrapradesh-news.xml,"
        "https://www.sakshi.com/rss-feed/andhra-pradesh,"
        "https://telugu.samayam.com/rssfeeds/telugu-news.xml,"
        "https://www.ntnews.com/rss/latest-news,"
        "https://www.andhrajyothy.com/rssfeed/andhra-pradesh"
    )
    
    # AI Configuration
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    USE_GROQ: bool = True
    
    # Fetch Limits
    MAX_ITEMS_PER_FEED: int = 3
    MAX_ITEMS_PER_RUN: int = 30
    
    # Application Settings
    LOG_LEVEL: str = "INFO"
    AUTO_FETCH_ON_START: bool = True
    FETCH_INTERVAL_MINUTES: int = 30
    
    # Frontend Settings
    SITE_NAME: str = "24/7 తెలుగు చిన్న వార్తలు"
    SITE_DESCRIPTION: str = "AI-పవర్డ్ తెలుగు న్యూస్ సమ్మరీస్"
    SITE_URL: str = "http://localhost:8000"
    
    # Cache Settings
    CACHE_TTL_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Parse RSS feeds from string to list
def parse_rss_feeds(feeds_str: str) -> List[str]:
    """Parse comma-separated RSS feeds string to list"""
    if not feeds_str:
        return []
    
    feeds = [feed.strip() for feed in feeds_str.split(",") if feed.strip()]
    return feeds


# Exported configuration
MONGO_URL = settings.MONGO_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME
ADMIN_SECRET = settings.ADMIN_SECRET
RSS_FEEDS_LIST = parse_rss_feeds(settings.RSS_FEEDS)

# AI Configuration
GROQ_API_KEY = settings.GROQ_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
USE_GROQ = settings.USE_GROQ and bool(settings.GROQ_API_KEY)

# Application Settings
MAX_ITEMS_PER_FEED = settings.MAX_ITEMS_PER_FEED
MAX_ITEMS_PER_RUN = settings.MAX_ITEMS_PER_RUN
LOG_LEVEL = settings.LOG_LEVEL.upper()
AUTO_FETCH_ON_START = settings.AUTO_FETCH_ON_START
FETCH_INTERVAL_MINUTES = settings.FETCH_INTERVAL_MINUTES

# Site Info
SITE_NAME = settings.SITE_NAME
SITE_DESCRIPTION = settings.SITE_DESCRIPTION
SITE_URL = settings.SITE_URL
CACHE_TTL_HOURS = settings.CACHE_TTL_HOURS

# Configure Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger("telugu-news")

# Validate configuration on import
def validate_config():
    """Validate critical configuration"""
    if not RSS_FEEDS_LIST:
        logger.warning("No RSS feeds configured! The app won't fetch any news.")
    
    if not GROQ_API_KEY and USE_GROQ:
        logger.warning("GROQ_API_KEY not set. AI summarization will be disabled.")
    
    if ADMIN_SECRET == "change-this-in-production":
        logger.warning("Using default ADMIN_SECRET. Change this in production!")


# Run validation
validate_config()
