# app.py (replace your existing app.py with this)
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from db import news_collection, db
from config import ADMIN_SECRET
import os, time

START_TIME = time.time()

app = FastAPI(title="24x7 Instant Telugu News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "Short News API Running", "timestamp": datetime.utcnow().isoformat()}

@app.get("/news")
def get_news(limit: int = Query(50), category: str = None):
    q = {}
    if category:
        q["category"] = category
    data = list(news_collection.find(q).sort("created_at", -1).limit(limit))
    for x in data:
        x["_id"] = str(x["_id"])
    return data

@app.get("/update")
def manual_update(x_admin_secret: str = Header(None, alias="X-Admin-Secret")):
    """
    Protected update endpoint.
    Use header: X-Admin-Secret: <your-secret>
    This prevents secret leakage in logs (querystrings get logged).
    """
    if not x_admin_secret or x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")

    # lazy import to minimize startup load
    from fetch_rss import process_rss
    # run the update job (blocking)
    process_rss()

    # log usage document in mongo (simple counter)
    try:
        db["usage"].insert_one({
            "event": "manual_update",
            "timestamp": datetime.utcnow(),
        })
    except Exception:
        pass

    return {"status": "updated", "timestamp": datetime.utcnow().isoformat()}

@app.get("/health")
def health():
    """
    Returns simple health info:
      - uptime
      - db reachable
      - counts for news collection (last 24h)
    """
    uptime_seconds = int(time.time() - START_TIME)
    # DB ping
    try:
        db.client.admin.command("ping")
        db_ok = True
    except Exception as e:
        db_ok = False

    # counts
    total = news_collection.count_documents({})
    last_24h = news_collection.count_documents({
        "created_at": {"$gte": datetime.utcnow() - timedelta(hours=24)}
    })

    return {
        "status": "ok" if db_ok else "db-error",
        "uptime_seconds": uptime_seconds,
        "total_news": total,
        "news_last_24h": last_24h,
        "timestamp": datetime.utcnow().isoformat()
    }

# optional: quick favicon to suppress 404 log noise
@app.get("/favicon.ico")
def favicon():
    return {}
