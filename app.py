from fastapi import FastAPI, Query
from db import news_collection
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from config import ADMIN_SECRET

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.get("/")
def home():
    return {"status":"Short News API Running", "timestamp": datetime.utcnow().isoformat()}

@app.get("/news")
def get_news(limit: int = Query(50), category: str = None):
    q = {}
    if category:
        q["category"] = category
    data = list(news_collection.find(q).sort("created_at", -1).limit(limit))
    for x in data:
        x["_id"] = str(x["_id"])
    return data

@app.get("/update")
def manual_update(secret: str = ""):
    if secret != ADMIN_SECRET:
        return {"error":"forbidden"}
    from fetch_rss import process_rss
    process_rss()
    return {"status":"updated"}
