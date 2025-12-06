# ~/project/app.py - పూర్తి సరిచేసిన కోడ్
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
# FastAPI & Templates
# -----------------------

app = FastAPI(title="24/7 Telugu Short News")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# -----------------------
# MongoDB
# -----------------------

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    raise RuntimeError("MONGO_URL environment variable not set")

client = AsyncIOMotorClient(MONGO_URL)
db = client[MONGO_DB_NAME]
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
        "likes": doc.get("likes", 0),
        "dislikes": doc.get("dislikes", 0),
        # created_at is only used for TTL index, don't expose it to API
    }


# -----------------------
# Endpoints
# -----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    # render the single-page application entry point
    return templates.TemplateResponse("app.html", {"request": request})


@app.get("/news", response_class=JSONResponse)
async def list_news(limit: int = 100):
    """
    Return list of news items. ADDED CACHE CONTROL.
    """
    # use a projection to potentially improve performance/reduce network load
    projection = {"title": 1, "summary": 1, "link": 1, "likes": 1, "dislikes": 1, "source": 1}
    cursor = news_col.find({}, sort=[("created_at", -1)], projection=projection).limit(limit)
    items = [serialize_news(doc) async for doc in cursor]

    # **FIXED:** Add Cache-Control header to prevent client-side caching of news list
    return JSONResponse(
        content={"items": items},
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )


@app.post("/news/{news_id}/reaction", response_class=JSONResponse)
async def react_to_news(news_id: str, payload: dict):
    action = (payload.get("action") or "").lower()
    if action not in ["like", "dislike"]:
        raise HTTPException(status_code=400, detail="Invalid action: must be 'like' or 'dislike'")

    try:
        oid = ObjectId(news_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid news id")

    # Update the likes/dislikes count atomically
    update_field = "likes" if action == "like" else "dislikes"
    
    result = await news_col.update_one(
        {"_id": oid},
        {"$inc": {update_field: 1}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="News item not found")

    # Fetch the updated counts
    updated_doc = await news_col.find_one(
        {"_id": oid},
        projection={"likes": 1, "dislikes": 1}
    )
    
    return {
        "likes": updated_doc.get("likes", 0),
        "dislikes": updated_doc.get("dislikes", 0)
    }


@app.get("/news/{news_id}/comments", response_class=JSONResponse)
async def list_comments(news_id: str):
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
async def startup_db_client():
    log.info(f"Connecting to MongoDB at {MONGO_URL.split('@')[-1]}")
    # We rely on TTL index for deletion, no extra cron job needed here.
    pass

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
    log.info("Closed MongoDB connection")

# End of file: app.py
