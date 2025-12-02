from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bson import ObjectId

from db import news   # Correct import (your db.py exports this)
from groq_client import summarize_text

app = FastAPI()

# Static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# UI Templates
templates = Jinja2Templates(directory="ui")


# --------------------------
# HOME PAGE → Loads app.html
# --------------------------
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "app.html",
        {"request": request}
    )


# Serialize news document
def serialize_news(n):
    return {
        "id": str(n["_id"]),
        "title": n.get("title", ""),
        "summary": n.get("summary", ""),
        "link": n.get("link", ""),
        "likes": n.get("likes", 0),
        "dislikes": n.get("dislikes", 0),
        "comments": n.get("comments", [])
    }


# ----------------------------------
# FIRST NEWS → /news
# ----------------------------------
@app.get("/news")
async def first_news(request: Request):
    doc = await news.find_one(sort=[("_id", 1)])
    if not doc:
        raise HTTPException(404, "No news found")

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ----------------------------------
# SPECIFIC NEWS → /news/{id}
# ----------------------------------
@app.get("/news/{news_id}")
async def get_news(request: Request, news_id: str):
    doc = await news.find_one({"_id": ObjectId(news_id)})
    if not doc:
        raise HTTPException(404, "News not found")

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ----------------------------------
# NEXT NEWS (Swipe Up)
# ----------------------------------
@app.get("/news/next/{news_id}")
async def next_news(request: Request, news_id: str):
    doc = await news.find_one(
        {"_id": {"$gt": ObjectId(news_id)}},
        sort=[("_id", 1)]
    )

    if not doc:
        doc = await news.find_one(sort=[("_id", 1)])

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ----------------------------------
# PREVIOUS NEWS (Swipe Down)
# ----------------------------------
@app.get("/news/prev/{news_id}")
async def prev_news(request: Request, news_id: str):
    doc = await news.find_one(
        {"_id": {"$lt": ObjectId(news_id)}},
        sort=[("_id", -1)]
    )

    if not doc:
        doc = await news.find_one(sort=[("_id", -1)])

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ----------------------------------
# LIKE
# ----------------------------------
@app.post("/api/like/{news_id}")
async def like_news(news_id: str):
    await news.update_one({"_id": ObjectId(news_id)}, {"$inc": {"likes": 1}})
    doc = await news.find_one({"_id": ObjectId(news_id)})
    return {"likes": doc.get("likes", 0), "dislikes": doc.get("dislikes", 0)}


# ----------------------------------
# DISLIKE
# ----------------------------------
@app.post("/api/dislike/{news_id}")
async def dislike_news(news_id: str):
    await news.update_one({"_id": ObjectId(news_id)}, {"$inc": {"dislikes": 1}})
    doc = await news.find_one({"_id": ObjectId(news_id)})
    return {"likes": doc.get("likes", 0), "dislikes": doc.get("dislikes", 0)}


# ----------------------------------
# ADD COMMENT
# ----------------------------------
@app.post("/api/comment/{news_id}")
async def add_comment(news_id: str, request: Request):
    data = await request.json()
    text = data.get("comment")

    if not text:
        return {"error": "empty"}

    await news.update_one(
        {"_id": ObjectId(news_id)},
        {"$push": {"comments": text}}
    )

    return {"status": "ok"}
