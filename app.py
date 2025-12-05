# app.py — Stage 1 Original Code

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from bson import ObjectId
from db import news_collection, comments_collection
from summarize import summarize_text
from fetch_rss import fetch_and_store_rss

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


def serialize_news(doc):
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title"),
        "summary": doc.get("summary"),
        "image_url": doc.get("image_url"),
        "source": doc.get("source"),
        "url": doc.get("url"),
        "created_at": doc.get("created_at"),
        "likes": doc.get("likes", 0),
        "dislikes": doc.get("dislikes", 0),
    }


@app.get("/", response_class=HTMLResponse)
async def serve_app():
    with open("ui/app.html", "r", encoding="utf-8") as f:
        return f.read()


@app.get("/news")
async def list_news(limit: int = 50):
    cursor = news_collection.find().sort("created_at", -1).limit(limit)
    return [serialize_news(doc) for doc in cursor]


@app.get("/news/{news_id}")
async def get_single_news(news_id: str):
    doc = news_collection.find_one({"_id": ObjectId(news_id)})
    if not doc:
        raise HTTPException(404, "News not found")
    return serialize_news(doc)


@app.post("/news/{news_id}/reaction")
async def post_reaction(news_id: str, req: Request):
    body = await req.json()
    reaction = body.get("reaction")

    if reaction not in ["like", "dislike"]:
        raise HTTPException(400, "Invalid reaction")

    field = "likes" if reaction == "like" else "dislikes"
    news_collection.update_one({"_id": ObjectId(news_id)}, {"$inc": {field: 1}})

    updated = news_collection.find_one({"_id": ObjectId(news_id)})
    return serialize_news(updated)


@app.get("/news/{news_id}/comments")
async def list_comments(news_id: str):
    comments = comments_collection.find({"news_id": news_id}).sort("created_at", -1)
    return [
        {
            "id": str(c["_id"]),
            "news_id": c["news_id"],
            "text": c["text"],
            "created_at": c["created_at"],
        }
        for c in comments
    ]


@app.post("/news/{news_id}/comments")
async def post_comment(news_id: str, req: Request):
    body = await req.json()
    text = body.get("text")

    if not text:
        raise HTTPException(400, "Text required")

    doc = {
        "news_id": news_id,
        "text": text,
        "created_at": body.get("created_at"),
    }

    comments_collection.insert_one(doc)
    return {"status": "ok", "comment": doc}


@app.get("/fetch-rss")
async def fetch_rss():
    await fetch_and_store_rss()
    return {"status": "RSS updated"}
