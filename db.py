from datetime import datetime

from pymongo import MongoClient, ASCENDING
from config import settings

client = MongoClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]

# Single collection for news
news_collection = db["news"]


def init_indexes() -> None:
    """
    Create indexes once on startup.
    """
    news_collection.create_index("link", unique=True)
    news_collection.create_index([("published_at", ASCENDING)])
    news_collection.create_index("category")


def get_db():
    """
    Kept for backward compatibility if anything imports get_db().
    """
    return db


def upsert_article(
    *,
    title: str,
    link: str,
    summary: str,
    source: str,
    category: str | None,
    image_url: str | None,
    published_at,
) -> None:
    """
    Insert or update a news article by link.
    """
    now = datetime.utcnow()
    news_collection.update_one(
        {"link": link},
        {
            "$set": {
                "title": title,
                "summary": summary,
                "source": source,
                "category": category,
                "image_url": image_url,
                "published_at": published_at,
                "updated_at": now,
            },
            "$setOnInsert": {"created_at": now},
        },
        upsert=True,
    )
