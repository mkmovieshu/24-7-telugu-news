from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from bson import ObjectId
from db import db

app = FastAPI()

# UI Templates directory (must match your folder name)
templates = Jinja2Templates(directory="ui")


# --------------------------
# HOME PAGE
# --------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})


# --------------------------
# GET ALL NEWS (FOR APP.JS)
# --------------------------
@app.get("/news")
async def get_news():
    news_list = []

    # Read all news sorted by ID (ascending)
    async for doc in db.news.find({}).sort("_id", 1):
        news_list.append({
            "id": str(doc["_id"]),
            "title": doc.get("title", ""),
            "summary": doc.get("summary", ""),
            "link": doc.get("link", "#"),
            "likes": doc.get("likes", 0),
            "dislikes": doc.get("dislikes", 0)
        })

    return JSONResponse(news_list)


# --------------------------
# LIKE NEWS
# --------------------------
@app.post("/news/{news_id}/like")
async def like_news(news_id: str):
    await db.news.update_one(
        {"_id": ObjectId(news_id)},
        {"$inc": {"likes": 1}}
    )
    return {"status": "ok"}


# --------------------------
# DISLIKE NEWS
# --------------------------
@app.post("/news/{news_id}/dislike")
async def dislike_news(news_id: str):
    await db.news.update_one(
        {"_id": ObjectId(news_id)},
        {"$inc": {"dislikes": 1}}
    )
    return {"status": "ok"}
@app.get("/api/comments/{news_id}")
async def get_comments(news_id: str):
    doc = await db.news.find_one({"_id": ObjectId(news_id)})
    return {"comments": doc.get("comments", [])}


@app.post("/api/comments/{news_id}")
async def post_comment(news_id: str, body: dict):
    text = body.get("text", "").strip()
    if not text:
        return {"error": "empty"}

    await db.news.update_one(
        {"_id": ObjectId(news_id)},
        {"$push": {"comments": {"text": text}}}
    )

    return {"status": "ok"}
