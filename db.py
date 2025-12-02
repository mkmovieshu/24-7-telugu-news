from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

# connect Mongo
client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]

# collections
news = db["news"]       # async collection
users = db["users"]
likes = db["likes"]

# create indexes at startup (called by app.py)
async def init_indexes():
    await news.create_index("link", unique=True)
    await news.create_index([("created_at", -1)])
