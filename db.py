import logging
from pymongo import MongoClient
from config import settings

logger = logging.getLogger("short-news-api")

# Create a single global Mongo client
client = MongoClient(settings.MONGO_URL)

# Select database
db = client[settings.MONGO_DB_NAME]

# Main collection for news
news_collection = db["news"]  # <-- ఇదే ఇప్పుడు fetch_rss.py import చేసే పేరు

def get_db():
    """
    FastAPI dependency helper – returns the database instance.
    """
    return db

# Optional: create useful indexes at startup
try:
    news_collection.create_index("link", unique=True)
    news_collection.create_index("created_at")
    logger.info("MongoDB connected and indexes ensured")
except Exception as e:
    logger.error(f"Error creating indexes or connecting to MongoDB: {e}")
