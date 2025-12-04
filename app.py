# app.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import os
from datetime import datetime
import logging
import asyncio

# try motor import (async mongo client)
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    has_motor = True
except Exception:
    AsyncIOMotorClient = None
    has_motor = False

# basic config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("shortnews")

app = FastAPI(title="24/7 Telugu Short News")

# static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# Mongo config (optional)
MONGO_URL = os.getenv("MONGO_URL", "")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

# if Mongo present and motor available, connect; else fallback to in-memory store
db_client = None
news_col = None
comments_col = None
use_in_memory = False
_inmemory_news = []

if MONGO_URL and has_motor:
    try:
        db_client = AsyncIOMotorClient(MONGO_URL)
        db = db_client[MONGO_DB_NAME]
        news_col = db["news"]
        comments_col = db["comments"]
        logger.info("Connected to MongoDB")
    except Exception as e:
        logger.exception("Failed connecting to MongoDB, falling back to in-memory: %s", e)
        use_in_memory = True
else:
    logger.warning("MONGO_URL not set or motor not available. Using in-memory store.")
    use_in_memory = True

# helper serialiser for docs (works for both)
def serialize_news_doc(doc):
    if not doc:
        return None
    return {
        "id": str(doc.get("_id", doc.get("id"))),
        "title": doc.get("title", ""),
        "summary": doc.get("summary", ""),
        "link": doc.get("link", ""),
        "likes": int(doc.get("likes", 0)),
        "dislikes": int(doc.get("dislikes", 0)),
        "created_at": doc.get("created_at")
    }

# demo endpoint: serve index page
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # render UI template (ui/app.html expected)
    return templates.TemplateResponse("app.html", {"request": request})

# API: get news list
@app.get("/news")
async def api_news(limit: int = 20):
    if use_in_memory:
        # return last items
        items = list(reversed(_inmemory_news[-limit:]))
        return {"items": items}
    else:
        cursor = news_col.find().sort("created_at", -1).limit(limit)
        docs = []
        async for d in cursor:
            docs.append(serialize_news_doc(d))
        return {"items": docs}

# API: add news (for fetcher script to post processed news)
@app.post("/news")
async def add_news(payload: dict):
    payload.setdefault("likes", 0)
    payload.setdefault("dislikes", 0)
    payload.setdefault("created_at", datetime.utcnow().isoformat())

    if use_in_memory:
        # make simple id
        nid = str(len(_inmemory_news) + 1)
        item = {"id": nid, **payload}
        _inmemory_news.append(item)
        return JSONResponse({"ok": True, "item": item})
    else:
        res = await news_col.insert_one(payload)
        inserted = await news_col.find_one({"_id": res.inserted_id})
        return JSONResponse({"ok": True, "item": serialize_news_doc(inserted)})

# simple health
@app.get("/health")
async def health():
    return {"status": "ok", "time": datetime.utcnow().isoformat()}

# static route for news items if you want direct html render
@app.get("/news/{news_id}", response_class=HTMLResponse)
async def news_view(request: Request, news_id: str):
    if use_in_memory:
        for n in _inmemory_news:
            if str(n.get("id")) == news_id:
                return templates.TemplateResponse("news_item.html", {"request": request, "news": n})
        raise HTTPException(status_code=404, detail="Not found")
    else:
        doc = await news_col.find_one({"_id": news_id}) if False else await news_col.find_one({"_id": news_id})  # real apps convert id
        # for simplicity, try lookup by string id field too:
        if not doc:
            doc = await news_col.find_one({"id": news_id})
        if not doc:
            raise HTTPException(status_code=404, detail="Not found")
        return templates.TemplateResponse("news_item.html", {"request": request, "news": serialize_news_doc(doc)})
