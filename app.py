from fastapi import FastAPI
from db import news_collection
from fetch_rss import process_rss
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Short News API Running"}

@app.get("/news")
def get_news(limit: int = 50, category: str = None):
    q = {}
    if category:
        q["category"] = category
    
    data = list(news_collection.find(q).sort("_id", -1).limit(limit))
    for x in data:
        x["_id"] = str(x["_id"])
    return data

@app.get("/update")
def manual_update():
    process_rss()
    return {"status": "Updated"}
