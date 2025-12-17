# config.py - Gemini API (GOOGLE_API_KEY) కోసం సెటప్ చేయబడింది

import logging
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Core env vars
    MONGO_URL: str
    MONGO_DB_NAME: str
    ADMIN_SECRET: str
    SECRET_FETCHER_PATH: str = "/secret-fetcher-endpoint-3453456"
    
    # ✅ Gemini API Key ను ఉపయోగించండి
    GOOGLE_API_KEY: str | None = None  
    RSS_FEEDS: str  # కామా సెపరేటెడ్ RSS URLs

    # ❌ Groq settings - వీటిని నిలిపివేయండి
    GROQ_API_KEY: str | None = None
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    USE_GROQ: bool = False # ✅ Groq వాడకూడదు కాబట్టి False

    # Summarization & fetch limits
    MAX_ITEMS_PER_FEED: int = 3   
    MAX_ITEMS_PER_RUN: int = 30   

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    """సెట్టింగుల ఆబ్జెక్ట్‌ను ఒకసారి మాత్రమే లోడ్ చేస్తుంది."""
    return Settings()


settings = get_settings()

# Exported variables (ఇవి ఇతర ఫైళ్లలో import అవుతాయి)
MONGO_URL = settings.MONGO_URL
MONGO_DB_NAME = settings.MONGO_DB_NAME
ADMIN_SECRET = settings.ADMIN_SECRET
SECRET_FETCHER_PATH = settings.SECRET_FETCHER_PATH
GOOGLE_API_KEY = settings.GOOGLE_API_KEY # ఇది Gemini API Key గా పనిచేస్తుంది
RSS_FEEDS = settings.RSS_FEEDS

# ❌ Groq లాజిక్‌ను ఇక్కడ తొలగిస్తున్నాము/నిర్లక్ష్యం చేస్తున్నాము
GROQ_API_KEY = settings.GROQ_API_KEY 
GROQ_MODEL = settings.GROQ_MODEL
USE_GROQ = settings.USE_GROQ # ఇది ఇప్పుడు False

MAX_ITEMS_PER_FEED = settings.MAX_ITEMS_PER_FEED
MAX_ITEMS_PER_RUN = settings.MAX_ITEMS_PER_RUN

LOG_LEVEL = settings.LOG_LEVEL.upper()

# లాగింగ్ సెటప్
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("short-news-api")

