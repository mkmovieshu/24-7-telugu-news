#config.py
import logging
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core env vars (ముందు నుంచే ఉన్నవి – పేర్లు మార్చలేదు)
    MONGO_URL: str
    MONGO_DB_NAME: str
    ADMIN_SECRET: str
    GOOGLE_API_KEY: str | None = None  # క్రితం Gemini key – ఉంచుతున్నాం
    RSS_FEEDS: str  # కామా సెపరేటెడ్ RSS URLs

    # Groq settings
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    USE_GROQ: bool = True

    # Summarization & fetch limits
    MAX_ITEMS_PER_FEED: int = 3   # ఒక్క ఫీడ్ నుంచి గరిష్టంగా 3 న్యూస్
    MAX_ITEMS_PER_RUN: int = 30   # ఒక్క రన్‌లో మొత్తం 30 న్యూస్ వరకు

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Exported variables (ఇవి ఇతర ఫైళ్లలో import అవుతాయి)
MONGO_URL = settings.MONGO_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME
ADMIN_SECRET = settings.ADMIN_SECRET
GOOGLE_API_KEY = settings.GOOGLE_API_KEY
RSS_FEEDS = settings.RSS_FEEDS

# Groq – GROQ_API_KEY సెట్ చెయ్యకపోతే, తప్పనిసరి అయితే GOOGLE_API_KEY ని ఉపయోగిస్తాం
GROQ_API_KEY = settings.GROQ_API_KEY or settings.GOOGLE_API_KEY
GROQ_MODEL = settings.GROQ_MODEL
USE_GROQ = settings.USE_GROQ and bool(GROQ_API_KEY)

MAX_ITEMS_PER_FEED = settings.MAX_ITEMS_PER_FEED
MAX_ITEMS_PER_RUN = settings.MAX_ITEMS_PER_RUN

LOG_LEVEL = settings.LOG_LEVEL.upper()

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("short-news-api")
