# db.py - FINAL CORRECTED CODE
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# .env file ఉంటే లోడ్ చేయండి (Render లో ఇది అవసరం లేదు, కానీ లోకల్ టెస్టింగ్ కోసం మంచిది)
load_dotenv()

# ✅ FIX 1: MONGO_URL ను ఉపయోగించండి (app.py తో స్థిరత్వం కోసం)
MONGO_URI = os.getenv("MONGO_URL") 
DB_NAME = os.getenv("MONGO_DB_NAME") or "shortnews" # ✅ app.py లో ఉన్న DB పేరును వాడండి

# ✅ FIX 2: MONGO_URI సెట్ చేయకపోతే లోపం చూపించాలి, లోకల్ అడ్రస్ ను వాడకూడదు
if not MONGO_URI:
    # Render లో MONGO_URL సెట్ చేయకపోతే, ఫెచింగ్ ఆగిపోవాలి.
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
    
