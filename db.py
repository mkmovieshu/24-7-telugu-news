from pymongo import MongoClient
from config import MONGO_URL, MONGO_DB_NAME

client = MongoClient(MONGO_URL)
db = client[MONGO_DB_NAME]
news_collection = db["news"]
