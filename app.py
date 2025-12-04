# app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shortnews")

# -----------------------
# FastAPI & Templates
# -----------------------

app = FastAPI(title="24/7 Telugu Short News")

# serve static files from ./static
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# -----------------------
# MongoDB
# -----------------------

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    # if you want local dev, set MONGO_URL env var in Render / GitHub Actions / local.
    raise RuntimeError("MONGO_URL environment variable not set")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
news_col = db["news"]
comments_col = db["comments"]

logger.info("Connected to MongoDB")

# -----------------------
# Helpers
# -----------------------

def serialize_news(doc):
    """Convert mongodb doc to frontend-friendly dict"""
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title") or "",
        "summary": doc.get("summary") or "",
        "link": doc.get("link") or doc.get("source") or "",
        "likes": int(doc.get("likes", 0) or 0),
        "dislikes": int(doc.get("dislikes", 0) or 0),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
    }

def parse_objectid(s: str):
    try:
        return ObjectId(s)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")

# -----------------------
# Pages
# -----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the single-page frontend (app.html).
    Frontend fetches /news?limit=... and other APIs.
    """
    return templates.TemplateResponse("app.html", {"request": request})

# -----------------------
# News APIs
# -----------------------

@app.get("/news", response_class=JSONResponse)
async def list_news(limit: int = 100):
    """
    Return list of news items (most-recent first).
    Frontend uses this once and then manages swipe locally.
    """
    cursor = news_col.find({}, sort=[("created_at", -1)]).limit(limit)
    items = [serialize_news(doc) async for doc in cursor]
    return {"items": items}

@app.get("/news/{news_id}", response_class=JSONResponse)
async def get_news(news_id: str):
    """Return a single news item by id (used by some frontends)."""
    oid = parse_objectid(news_id)
    doc = await news_col.find_one({"_id": oid})
    if not doc:
        raise HTTPException(status_code=404, detail="Not found")
    return {"item": serialize_news(doc)}

@app.post("/news/{news_id}/reaction", response_class=JSONResponse)
async def add_reaction(news_id: str, payload: dict):
    """
    Legacy route: payload = { "action": "like" | "dislike" }
    """
    action = (payload.get("action") or "").strip().lower()
    if action not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Invalid action")
    field = "likes" if action == "like" else "dislikes"
    oid = parse_objectid(news_id)
    result = await news_col.update_one({"_id": oid}, {"$inc": {field: 1}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="News not found")
    doc = await news_col.find_one({"_id": oid})
    data = serialize_news(doc)
    return {"likes": data["likes"], "dislikes": data["dislikes"]}

# Provide simpler endpoints the frontend seems to call (/likes/<id>, /dislikes/<id>)
@app.post("/likes/{news_id}", response_class=JSONResponse)
async def post_like(news_id: str):
    oid = parse_objectid(news_id)
    result = await news_col.update_one({"_id": oid}, {"$inc": {"likes": 1}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="News not found")
    doc = await news_col.find_one({"_id": oid})
    data = serialize_news(doc)
    return {"likes": data["likes"], "dislikes": data["dislikes"]}

@app.post("/dislikes/{news_id}", response_class=JSONResponse)
async def post_dislike(news_id: str):
    oid = parse_objectid(news_id)
    result = await news_col.update_one({"_id": oid}, {"$inc": {"dislikes": 1}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="News not found")
    doc = await news_col.find_one({"_id": oid})
    data = serialize_news(doc)
    return {"likes": data["likes"], "dislikes": data["dislikes"]}

# -----------------------
# Comments APIs
# -----------------------

@app.get("/news/{news_id}/comments", response_class=JSONResponse)
async def get_comments(news_id: str):
    oid = parse_objectid(news_id)
    cursor = comments_col.find({"news_id": oid}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append(
            {
                "id": str(doc["_id"]),
                "text": doc.get("text", ""),
                "created_at": doc.get("created_at", datetime.utcnow()).isoformat(),
            }
        )
    return {"items": items}

@app.post("/news/{news_id}/comments", response_class=JSONResponse)
async def add_comment(news_id: str, payload: dict):
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty comment")
    oid = parse_objectid(news_id)
    doc = {
        "news_id": oid,
        "text": text,
        "created_at": datetime.utcnow(),
    }
    res = await comments_col.insert_one(doc)
    return {"id": str(res.inserted_id)}

# -----------------------
# Utility endpoints (optional)
# -----------------------

@app.get("/healthz")
async def health():
    return {"status": "ok"}

# -----------------------
# Startup / Shutdown hooks (optional logging)
# -----------------------

@app.on_event("startup")
async def on_start():
    logger.info("App startup complete")

@app.on_event("shutdown")
async def on_stop():
    logger.info("App shutdown")
