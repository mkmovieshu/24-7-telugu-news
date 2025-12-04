from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import os
from datetime import datetime

# ---------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------
app = FastAPI(title="24/7 Telugu Short News")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# ---------------------------------------------------------
# MongoDB Setup
# ---------------------------------------------------------
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable not set")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
news_col = db["news"]
comments_col = db["comments"]

# ---------------------------------------------------------
# Helper to serialize MongoDB document
# ---------------------------------------------------------
def serialize_news(doc):
    if not doc:
        return None

    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "summary": doc.get("summary", ""),
        "image": doc.get("image", ""),
        "source_url": doc.get("source_url", ""),
        "timestamp": doc.get("timestamp"),
    }

# ---------------------------------------------------------
# Routes
# ---------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})


@app.get("/api/news")
async def get_news():
    try:
        docs = await news_col.find().sort("timestamp", -1).to_list(50)
        return {"news": [serialize_news(x) for x in docs]}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.get("/api/news/{news_id}")
async def get_single_news(news_id: str):
    try:
        doc = await news_col.find_one({"_id": ObjectId(news_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="News not found")
        return serialize_news(doc)
    except Exception:
        raise HTTPException(404, "Invalid ID")


@app.post("/api/comments/{news_id}")
async def post_comment(news_id: str, data: dict):
    text = data.get("text", "").strip()

    if not text:
        raise HTTPException(400, "Comment cannot be empty")

    comment_doc = {
        "news_id": news_id,
        "text": text,
        "timestamp": datetime.utcnow()
    }

    await comments_col.insert_one(comment_doc)

    return {"status": "ok"}


@app.get("/api/comments/{news_id}")
async def get_comments(news_id: str):
    comments = await comments_col.find({"news_id": news_id}).sort("timestamp", -1).to_list(50)

    return {
        "comments": [
            {
                "id": str(c["_id"]),
                "text": c.get("text", ""),
                "timestamp": c.get("timestamp")
            }
            for c in comments
        ]
    }


@app.get("/api/health")
async def health_check():
    return {"status": "running"}
