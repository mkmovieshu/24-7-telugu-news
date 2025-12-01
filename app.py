import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from config import ADMIN_SECRET
from fetch_rss import fetch_and_store_news
from summarize import get_latest_news
from db import get_db

app = FastAPI(title="24/7 Telugu News API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------
#        FRONTEND
# --------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Load frontend page from static/app.html
    """
    file_path = os.path.join("static", "app.html")

    if not os.path.exists(file_path):
        return HTMLResponse(
            content=f"<h2>app.html not found at: {file_path}</h2>",
            status_code=404
        )

    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()

    return HTMLResponse(content=html, status_code=200)


# --------------------------
#        API ROUTES
# --------------------------

@app.get("/news")
def get_news(limit: int = 20):
    """
    Get latest news items from MongoDB
    """
    db = get_db()
    items = list(
        db.news.find({}, {"_id": 0})
        .sort("created_at", -1)
        .limit(limit)
    )
    return items


@app.get("/update")
def update_news(request: Request):
    """
    Admin-controlled RSS fetcher
    """
    secret = request.headers.get("X-Admin-Secret")
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")

    inserted, errors = fetch_and_store_news()
    return JSONResponse({
        "status": "updated",
        "timestamp": datetime.utcnow(),
        "inserted": inserted,
        "errors": errors
    })


# --------------------------
#      HEALTH CHECK
# --------------------------
@app.get("/health")
def health():
    return {"status": "ok", "time": datetime.utcnow()}
