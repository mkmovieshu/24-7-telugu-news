# ~/project/app.py - పూర్తిగా సరిచేసిన కోడ్
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

import os
from datetime import datetime
import logging
import subprocess
import threading

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("shortnews")

# -----------------------
# FastAPI & Templates
# -----------------------

app = FastAPI(title="24/7 Telugu Short News")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# -----------------------
# MongoDB (Async Motor)
# -----------------------

# MONGO_URL ని MONGO_URI గా మార్చాము
MONGO_URI = os.getenv("MONGO_URI") #
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews") #

# MONGO_URL బదులు MONGO_URI ని తనిఖీ చేస్తాము
if not MONGO_URI: #
    log.error("MONGO_URI environment variable not set") #
    # WARNING: Not raising error here to allow local testing without env var

# కనెక్షన్ కోసం MONGO_URI ని వాడుతున్నాం
client = AsyncIOMotorClient(MONGO_URI) #
db = client[MONGO_DB_NAME] #
news_col = db["news"] # Async collection used by web endpoints #
comments_col = db["comments"] #

# -----------------------
# Helpers
# -----------------------

def serialize_news(doc): #
    """Simple serializer."""
    if not doc: #
        return None #
    return { #
        "id": str(doc.get("_id")), #
        "title": doc.get("title") or "", #
        "summary": doc.get("summary") or "", #
        "link": doc.get("link") or doc.get("source") or "", #
        "likes": int(doc.get("likes", 0) or 0), #
        "dislikes": int(doc.get("dislikes", 0) or 0), #
    } #

# -----------------------
# RSS Fetching Trigger (for External Cron Service)
# -----------------------

def run_fetch_rss_script(): #
    """Runs the synchronous fetch_rss.py script in a separate process/thread."""
    # MONGO_URL బదులు MONGO_URI ని తనిఖీ చేస్తాము
    if not MONGO_URI: #
        log.warning("Skipping fetch: MONGO_URI not set.") #
        return #
        
    log.info("Starting fetch_rss.py via subprocess...") #
    try: #
        result = subprocess.run( #
            ["python", "fetch_rss.py"], 
            capture_output=True, 
            text=True, 
            check=True
        ) #
        log.info(f"fetch_rss.py completed. Output:\n{result.stdout}") #
    except subprocess.CalledProcessError as e: #
        log.error(f"fetch_rss.py failed! Stderr:\n{e.stderr}") #
    except Exception as e: #
        log.error(f"Error running fetch_rss.py: {e}") #

@app.get("/secret-fetcher-endpoint-3453456", status_code=202) #
async def trigger_fetch(): #
    """
    Triggers the fetch_rss.py script in a background thread to avoid blocking the main web server.
    NOTE: Use a long, hard-to-guess URL for security.
    """ #
    threading.Thread(target=run_fetch_rss_script).start() #
    log.info("Fetch triggered by external source.") #
    return {"status": "accepted", "message": "News fetch started in background."} #

# -----------------------
# Endpoints (Cache Fix)
# -----------------------

@app.get("/", response_class=HTMLResponse) #
async def home(request: Request): #
    return templates.TemplateResponse("app.html", {"request": request}) #

@app.get("/news", response_class=JSONResponse) #
async def list_news(limit: int = 100): #
    """
    Return list of news items. ADDED CACHE CONTROL.
    """ #
    cursor = news_col.find({}, sort=[("created_at", -1)]).limit(limit) #
    items = [serialize_news(doc) async for doc in cursor] #
    
    # FIXED: Cache-Control హెడర్‌ను జతచేయండి
    return JSONResponse( #
        content={"items": items}, #
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"} #
    ) #

@app.post("/news/{news_id}/reaction", response_class=JSONResponse) #
async def add_reaction(news_id: str, payload: dict): #
    action = payload.get("action") #
    if action not in ("like", "dislike"): #
        raise HTTPException(status_code=400, detail="Invalid action") #

    field = "likes" if action == "like" else "dislikes" #

    try: #
        oid = ObjectId(news_id) #
    except Exception: #
        raise HTTPException(status_code=400, detail="Invalid news id") #

    result = await news_col.update_one({"_id": oid}, {"$inc": {field: 1}}) #
    if result.matched_count == 0: #
        raise HTTPException(status_code=404, detail="News not found") #

    doc = await news_col.find_one({"_id": oid}) #
    data = serialize_news(doc) #
    return {"likes": data["likes"], "dislikes": data["dislikes"]} #

@app.get("/news/{news_id}/comments", response_class=JSONResponse) #
async def get_comments(news_id: str): #
    try: #
        oid = ObjectId(news_id) #
    except Exception: #
        raise HTTPException(status_code=400, detail="Invalid news id") #

    cursor = comments_col.find({"news_id": oid}).sort("created_at", -1) #
    items = [] #
    async for doc in cursor: #
        items.append( #
            { #
                "id": str(doc["_id"]), #
                "text": doc.get("text", ""), #
                "created_at": ( #
                    doc.get("created_at").isoformat()
                    if hasattr(doc.get("created_at"), "isoformat")
                    else str(doc.get("created_at") or "")
                ), #
            }
        ) #
    return {"items": items} #

@app.post("/news/{news_id}/comments", response_class=JSONResponse) #
async def add_comment(news_id: str, payload: dict): #
    text = (payload.get("text") or "").strip() #
    if not text: #
        raise HTTPException(status_code=400, detail="Empty comment") #

    try: #
        oid = ObjectId(news_id) #
    except Exception: #
        raise HTTPException(status_code=400, detail="Invalid news id") #

    doc = { #
        "news_id": oid, #
        "text": text, #
        "created_at": datetime.utcnow(), #
    } #
    res = await comments_col.insert_one(doc) #
    return {"id": str(res.inserted_id)} #

# -----------------------
# Startup / Shutdown
# -----------------------

@app.on_event("startup") #
async def startup(): #
    log.info("App startup complete.") #
    # Optional: Run fetch once on startup to ensure initial data load
    threading.Thread(target=run_fetch_rss_script).start() #
    
@app.on_event("shutdown") #
async def shutdown(): #
    if client: #
        client.close() # Close motor client #
    log.info("App shutdown.") #
