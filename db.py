import logging
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import settings

logger = logging.getLogger("short-news-api")

# Global client and DB
_client: MongoClient | None = None
_db = None


def _init_client() -> None:
    """
    Internal: create Mongo client and cache the DB object.
    Called on first use.
    """
    global _client, _db

    if _client is not None and _db is not None:
        return

    if not settings.MONGO_URL:
        raise RuntimeError("MONGO_URL is not configured")

    if not settings.MONGO_DB_NAME:
        raise RuntimeError("MONGO_DB_NAME is not configured")

    logger.info("Connecting to MongoDB...")
    _client = MongoClient(settings.MONGO_URL)
    _db = _client[settings.MONGO_DB_NAME]

    # simple ping to fail fast if something is wrong
    try:
        _client.admin.command("ping")
        logger.info("MongoDB connected")
    except ConnectionFailure as e:
        logger.error("MongoDB ping failed: %s", e)
        raise


def get_db():
    """
    Public helper used by the rest of the app.

    Usage:
        db = get_db()
        news_col = db["news"]
    """
    if _db is None:
        _init_client()
    return _db


def get_collection(name: str):
    """
    Shortcut to get a collection by name.

    Usage:
        news_col = get_collection("news")
    """
    db = get_db()
    return db[name]
