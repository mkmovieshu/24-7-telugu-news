from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from bson import ObjectId
from db import get_db
from fetch_rss import fetch_and_store_all_feeds
from summarize import needs_ai, clean_text
from groq_client import summarize_text

app = FastAPI()

# Static files
app.mount("/static", StaticFiles(directory="statics"), name="static")

# Templates (UI)
templates = Jinja2Templates(directory="ui")


# -------------------------------
# HOME PAGE → REDIRECT TO /news
# -------------------------------
@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "app.html",
        {"request": request}
    )


# ------------------------------------
# FETCH NEWS LIST (One news per page)
# ------------------------------------
def serialize_news(n):
    return {
        "id": str(n["_id"]),
        "title": n["title"],
        "summary": n.get("summary", ""),
        "link": n["link"],
        "likes": n.get("likes", 0),
        "dislikes": n.get("dislikes", 0),
        "comments": n.get("comments", [])
    }

# ------------------------------------
# /news → First news
# ------------------------------------
@app.get("/news")
async def first_news(request: Request):
    db = get_db()
    doc = await db.news.find_one(sort=[("_id", 1)])

    if not doc:
        raise HTTPException(404, "No news found")

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ------------------------------------
# /news/{id} → Specific news
# ------------------------------------
@app.get("/news/{news_id}")
async def get_news(request: Request, news_id: str):
    db = get_db()
    doc = await db.news.find_one({"_id": ObjectId(news_id)})

    if not doc:
        raise HTTPException(404, "News not found")

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ------------------------------------
# Swipe NEXT → /news/next/{id}
# ------------------------------------
@app.get("/news/next/{news_id}")
async def next_news(request: Request, news_id: str):
    db = get_db()
    doc = await db.news.find_one({"_id": {"$gt": ObjectId(news_id)}}, sort=[("_id", 1)])

    if not doc:
        # Go to first
        doc = await db.news.find_one(sort=[("_id", 1)])

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ------------------------------------
# Swipe PREVIOUS → /news/prev/{id}
# ------------------------------------
@app.get("/news/prev/{news_id}")
async def prev_news(request: Request, news_id: str):
    db = get_db()
    doc = await db.news.find_one({"_id": {"$lt": ObjectId(news_id)}}, sort=[("_id", -1)])

    if not doc:
        # Go to last
        doc = await db.news.find_one(sort=[("_id", -1)])

    return templates.TemplateResponse(
        "news_item.html",
        {"request": request, "news": serialize_news(doc)}
    )


# ------------------------------------
# Like
# ------------------------------------
@app.post("/api/like/{news_id}")
async def like_news(news_id: str):
    db = get_db()
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$inc": {"likes": 1}})
    doc = await db.news.find_one({"_id": ObjectId(news_id)})
    return {"likes": doc.get("likes", 0), "dislikes": doc.get("dislikes", 0)}


# ------------------------------------
# Dislike
# ------------------------------------
@app.post("/api/dislike/{news_id}")
async def dislike_news(news_id: str):
    db = get_db()
    await db.news.update_one({"_id": ObjectId(news_id)}, {"$inc": {"dislikes": 1}})
    doc = await db.news.find_one({"_id": ObjectId(news_id)})
    return {"likes": doc.get("likes", 0), "dislikes": doc.get("dislikes", 0)}


# ------------------------------------
# Add Comment
# ------------------------------------
@app.post("/api/comment/{news_id}")
async def add_comment(news_id: str, request: Request):
    data = await request.json()
    text = data.get("comment")

    db = get_db()
    await db.news.update_one(
        {"_id": ObjectId(news_id)},
        {"$push": {"comments": text}}
    )

    return {"status": "ok"}
