import os
from functools import lru_cache


class Settings:
    # Mongo / app core
    MONGO_URL: str = os.getenv("MONGO_URL", "")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "short_news")
    ADMIN_SECRET: str = os.getenv("ADMIN_SECRET", "changeme")

    # RSS feeds – comma separated list of URLs
    RSS_FEEDS: str = os.getenv("RSS_FEEDS", "")

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # --- Groq summarizer config ---
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    # Latest fast-cheap Telugu-capable model; change if you want
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    # Toggle to disable Groq in emergencies
    USE_GROQ: bool = os.getenv("USE_GROQ", "true").lower() == "true"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

# Quick sanity checks (won't crash if missing, just warnings in logs)
if not settings.MONGO_URL:
    print("[WARN] MONGO_URL not set")
if not settings.GROQ_API_KEY:
    print("[WARN] GROQ_API_KEY not set - summaries will fail")
