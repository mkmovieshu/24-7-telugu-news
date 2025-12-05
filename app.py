# ~/project/app.py
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
log = logging.getLogger("shortnews")

# -----------------------
# FastAPI & Templates - FIXED PATHS
# -----------------------

app = FastAPI(title="24/7 Telugu Short News")

# 1. BASE_DIR ను నిర్వచించడం (అప్లికేషన్ యొక్క రూట్ డైరెక్టరీ)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2. TEMPLATE_DIR కు ఖచ్చితమైన పాత్ ను సెట్ చేయడం
TEMPLATE_DIR = os.path.join(BASE_DIR, "ui")

# 3. STATIC_DIR కు ఖచ్చితమైన పాత్ ను సెట్ చేయడం
STATIC_DIR = os.path.join(BASE_DIR, "static")

# StaticFiles మౌంట్ చేయడం
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Jinja2Templates కు TEMPLATE_DIR ను పంపడం
templates = Jinja2Templates(directory=TEMPLATE_DIR) 

# -----------------------
# MongoDB
# -----------------------

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable not set")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_DB_NAME]
news_col = db["news"]
comments_col = db["comments"]

# -----------------------
# Helpers
# -----------------------

def serialize_news(doc):
    """
    Simple serializer WITHOUT created_at to avoid isoformat errors.
    This prevents server 500 when created_at is missing or malformed.
    """
    if not doc:
        return None
    return {
        "id": str(doc.get("_id")),
        "title": doc.get("title") or "",
        "summary": doc.get("summary") or "",
        "link": doc.get("link") or doc.get("source") or "",
        "likes": int(doc.get("likes", 0) or 0),
        "dislikes": int(doc.get("dislikes", 0) or 0),
    }

# -----------------------
# Pages
# -----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("app.html", {"request": request})

# -----------------------
# News API
# -----------------------

@app.get("/news", response_class=JSONResponse)
async def list_news(limit: int = 100):
    """
    Return list of news items. No created_at returned (keeps stable).
    """
    cursor = news_col.find({}, sort=[("created_at", -1)]).limit(limit)
    items = [serialize_news(doc) async for doc in cursor]
    return {"items": items}

@app.post("/news/{news_id}/reaction", response_class=JSONResponse)
async def add_reaction(news_id: str, payload: dict):
    """
    Like / Dislike endpoint.
    payload = { "action": "like" | "dislike" }
    """
    action = payload.get("action")
    if action not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Invalid action")

    field = "likes" if action == "like" else "dislikes"

    try:
        oid = ObjectId(news_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid news id")

    result = await news_col.update_one({"_id": oid}, {"$inc": {field: 1}})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="News not found")

    doc = await news_col.find_one({"_id": oid})
    data = serialize_news(doc)
    return {"likes": data["likes"], "dislikes": data["dislikes"]}

# -----------------------
# Comments API
# -----------------------

@app.get("/news/{news_id}/comments", response_class=JSONResponse)
async def get_comments(news_id: str):
    try:
        oid = ObjectId(news_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid news id")

    cursor = comments_col.find({"news_id": oid}).sort("created_at", -1)
    items = []
    async for doc in cursor:
        items.append(
            {
                "id": str(doc["_id"]),
                "text": doc.get("text", ""),
                # don't assume created_at has isoformat; convert to string safely
                "created_at": (
                    doc.get("created_at").isoformat()
                    if hasattr(doc.get("created_at"), "isoformat")
                    else str(doc.get("created_at") or "")
                ),
            }
        )
    return {"items": items}

@app.post("/news/{news_id}/comments", response_class=JSONResponse)
async def add_comment(news_id: str, payload: dict):
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty comment")

    try:
        oid = ObjectId(news_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid news id")

    doc = {
        "news_id": oid,
        "text": text,
        "created_at": datetime.utcnow(),
    }
    res = await comments_col.insert_one(doc)
    return {"id": str(res.inserted_id)}

# -----------------------
# Startup / Shutdown logs
# -----------------------

@app.on_event("startup")
async def startup():
    log.info("Connected to MongoDB")
    log.info("App startup complete")

@app.on_event("shutdown")
async def shutdown():
    log.info("App shutdown")
    
