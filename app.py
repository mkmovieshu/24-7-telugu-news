import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config import ADMIN_SECRET
from db import get_latest_news, insert_news_items
from fetch_rss import fetch_all_feeds
from summarize import generate_summary_for_item

log = logging.getLogger("short-news-api")

# -----------------------------------------------------------------------------------
# FastAPI App Setup
# -----------------------------------------------------------------------------------

app = FastAPI(title="24/7 Telugu News API")

# Static folder mount (animations / css / js)
app.mount("/static", StaticFiles(directory="static"), name="static")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent


# -----------------------------------------------------------------------------------
# Homepage Route (Reads app.html from root; fallback to static/app.html)
# -----------------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """
    Serves app.html — tries root/app.html first, fallback to static/app.html.
    """
    # First try root
    html_path = BASE_DIR / "app.html"

    # If not found → static/app.html
    if not html_path.exists():
        html_path = BASE_DIR / "static" / "app.html"

    # Final safety check
    if not html_path.exists():
        return HTMLResponse("<h1>app.html file missing!</h1>", status_code=500)

    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


# -----------------------------------------------------------------------------------
# API: Fetch Latest News
# -----------------------------------------------------------------------------------
@app.get("/news")
def list_news(limit: int = 50):
    """
    Returns latest N news items from DB
    """
    data = get_latest_news(limit)
    return JSONResponse(data)


# -----------------------------------------------------------------------------------
# API: Manual Update Trigger
# -----------------------------------------------------------------------------------
@app.get("/update")
def update_feed(request: Request):
    """
    Admin-only update trigger.
    """
    secret = request.headers.get("X-Admin-Secret")
    if secret != ADMIN_SECRET:
        return JSONResponse({"error": "Invalid secret key"}, status_code=403)

    log.info("Fetching feeds...")

    items = fetch_all_feeds()

    inserted, errors = 0, []

    for item in items:
        try:
            # summary generation (dummy or real)
            generate_summary_for_item(item)
            insert_news_items([item])
            inserted += 1
        except Exception as e:
            errors.append(str(e))

    return {
        "status": "updated",
        "timestamp": str(request.scope.get("time", "")),
        "inserted": inserted,
        "errors": errors
    }
