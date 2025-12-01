# db.py

from pymongo import MongoClient
from config import settings


_client: MongoClient | None = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.MONGO_URL)
    return _client


def get_db():
    client = get_client()
    return client[settings.MONGO_DB_NAME]
