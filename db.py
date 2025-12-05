# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGODB_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME") or "shortnews"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db.get_collection("news")
likes_collection = db.get_collection("likes")
comments_collection = db.get_collection("comments")

# ensure TTL is set (24 hours) — created_at must be datetime
try:
    news_collection.create_index("created_at", expireAfterSeconds=86400)
except Exception:
    pass
