# db.py - MongoDB కనెక్షన్ పరిష్కరించబడింది
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# ✅ FIX 1: 'MONGO_URL' ను ఉపయోగించండి (app.py మరియు Render తో స్థిరత్వం కోసం)
MONGO_URI = os.getenv("MONGO_URL") 
DB_NAME = os.getenv("MONGO_DB_NAME") or "shortnews" 

# ✅ FIX 2: MONGO_URL సెట్ చేయకపోతే కనెక్షన్ ఆగిపోవాలి, లోకల్ అడ్రస్ వాడకూడదు
if not MONGO_URI:
    raise ValueError("MONGO_URL environment variable is not set. Cannot connect to MongoDB.")

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

