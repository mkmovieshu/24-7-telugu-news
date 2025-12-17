# db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# MONGO_URL ను app.py మరియు Render తో స్థిరత్వం కోసం ఉపయోగించండి
MONGO_URI = os.getenv("MONGO_URL") 
# DB పేరు MONGO_DB_NAME (Render లో సెట్ చేయకపోతే 'shortnews' డిఫాల్ట్)
DB_NAME = os.getenv("MONGO_DB_NAME") or "shortnews" 

# MONGO_URL సెట్ చేయకపోతే, లోపం చూపించి ఆగిపోవాలి.
if not MONGO_URI:
    raise ValueError("MONGO_URL environment variable is not set. Cannot connect to MongoDB.")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
news_collection = db.get_collection("news")
likes_collection = db.get_collection("likes")
comments_collection = db.get_collection("comments")

# ensure TTL is set (12 hours) — created_at must be datetime
try:
    news_collection.create_index("created_at", expireAfterSeconds=43200, background=True)
except Exception as e:
    # Index creation might fail if it already exists with different options.
    # In a real production setup, we might want to log this or handle migration.
    print(f"Warning: Could not create TTL index: {e}")
    
