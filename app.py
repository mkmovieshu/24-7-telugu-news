# app.py - మెరుగుపరచబడిన వెర్షన్
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from bson.errors import InvalidId

import os
from datetime import datetime, timedelta
import logging
import asyncio
from typing import List, Optional

# మా కస్టమ్ మాడ్యూల్స్
from config import settings, logger
from fetch_rss import fetch_all_feeds

# -----------------------
# FastAPI అప్లికేషన్
# -----------------------

app = FastAPI(
    title="24/7 తెలుగు చిన్న వార్తలు",
    description="AI-పవర్డ్ తెలుగు న్యూస్ సమ్మరీ సేవ",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# మిడిల్‌వేర్లు
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ప్రొడక్షన్ లో మార్చండి
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# స్టాటిక్ ఫైల్స్ & టెంప్లేట్స్
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="ui")

# -----------------------
# MongoDB కనెక్షన్
# -----------------------

client = AsyncIOMotorClient(settings.MONGO_URL)
db = client[settings.MONGO_DB_NAME]
news_col = db["news"]
comments_col = db["comments"]
likes_col = db["likes"]

# ఇండెక్స్‌లను సృష్టించడం
async def create_indexes():
    try:
        await news_col.create_index([("created_at", -1)])
        await news_col.create_index([("published", -1)])
        await news_col.create_index([("source", 1)])
        await news_col.create_index("link", unique=True, sparse=True)
        
        await comments_col.create_index([("news_id", 1), ("created_at", -1)])
        await likes_col.create_index([("news_id", 1), ("user_ip", 1)], unique=True)
        
        # TTL ఇండెక్స్ (48 గంటలు)
        await news_col.create_index("created_at", expireAfterSeconds=172800)
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")

# -----------------------
# హెల్పర్ ఫంక్షన్స్
# -----------------------

def serialize_news(doc) -> Optional[dict]:
    """MongoDB డాక్యుమెంట్‌ని JSON కి మార్చడం"""
    if not doc:
        return None
    
    try:
        created_at = doc.get("created_at")
        if isinstance(created_at, datetime):
            created_at_str = created_at.isoformat()
        else:
            created_at_str = str(created_at) if created_at else ""
        
        published = doc.get("published")
        if isinstance(published, datetime):
            published_str = published.isoformat()
        else:
            published_str = str(published) if published else ""
        
        return {
            "id": str(doc.get("_id")),
            "title": doc.get("title") or "",
            "summary": doc.get("summary") or doc.get("raw_summary", "")[:300],
            "link": doc.get("link") or "",
            "image": doc.get("image") or "",
            "source": doc.get("source") or "",
            "likes": int(doc.get("likes", 0)),
            "dislikes": int(doc.get("dislikes", 0)),
            "comment_count": int(doc.get("comment_count", 0)),
            "created_at": created_at_str,
            "published": published_str,
            "language": doc.get("language", "te"),
            "category": doc.get("category", "general")
        }
    except Exception as e:
        logger.error(f"Serialization error: {e}")
        return None

# -----------------------
# బ్యాక్‌గ్రౌండ్ టాస్క్స్
# -----------------------

async def periodic_fetch():
    """స్వయంచాలకంగా RSS ఫీడ్స్ ని ఫెచ్ చేయడం"""
    while True:
        try:
            logger.info("Starting periodic RSS fetch...")
            count = await asyncio.to_thread(fetch_all_feeds, max_items=30)
            logger.info(f"Periodic fetch completed: {count} items")
        except Exception as e:
            logger.error(f"Periodic fetch error: {e}")
        
        # ప్రతి 30 నిమిషాలకు ఒకసారి
        await asyncio.sleep(1800)  # 30 నిమిషాలు

# -----------------------
# పేజీస్
# -----------------------

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """మెయిన్ హోమ్ పేజీ"""
    return templates.TemplateResponse("app.html", {
        "request": request,
        "title": "24/7 తెలుగు చిన్న వార్తలు",
        "description": "AI-పవర్డ్ తెలుగు న్యూస్ సమ్మరీస్"
    })

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    """అబౌట్ పేజీ"""
    return templates.TemplateResponse("about.html", {
        "request": request,
        "title": "About - 24/7 తెలుగు వార్తలు"
    })

# -----------------------
# NEWS API
# -----------------------

@app.get("/api/news", response_class=JSONResponse)
async def list_news(
    limit: int = 50,
    skip: int = 0,
    category: Optional[str] = None,
    source: Optional[str] = None
):
    """న్యూస్ ఐటెమ్స్ లిస్ట్"""
    try:
        query = {}
        if category and category != "all":
            query["category"] = category
        if source and source != "all":
            query["source"] = source
        
        cursor = news_col.find(query).sort("created_at", -1).skip(skip).limit(limit)
        items = []
        
        async for doc in cursor:
            serialized = serialize_news(doc)
            if serialized:
                items.append(serialized)
        
        total = await news_col.count_documents(query)
        
        return {
            "success": True,
            "items": items,
            "total": total,
            "limit": limit,
            "skip": skip,
            "has_more": (skip + len(items)) < total
        }
    except Exception as e:
        logger.error(f"Error listing news: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"}
        )

@app.get("/api/news/{news_id}", response_class=JSONResponse)
async def get_news_detail(news_id: str):
    """స్పెసిఫిక్ న్యూస్ ఐటెమ్"""
    try:
        oid = ObjectId(news_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid news ID")
    
    try:
        doc = await news_col.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=404, detail="News not found")
        
        return {
            "success": True,
            "item": serialize_news(doc)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching news detail: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/news/{news_id}/reaction", response_class=JSONResponse)
async def add_reaction(
    news_id: str,
    request: Request,
    payload: dict,
    background_tasks: BackgroundTasks
):
    """లైక్ / డిస్లైక్"""
    action = payload.get("action")
    if action not in ("like", "dislike"):
        raise HTTPException(status_code=400, detail="Invalid action")
    
    try:
        oid = ObjectId(news_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid news ID")
    
    # యూజర్ IP ను ట్రాక్ చేయడం (ఒకేసారి ఒక్క రియాక్షన్ మాత్రమే)
    user_ip = request.client.host if request.client else "unknown"
    
    try:
        # ముందుగా లైక్ చెయ్యబడిందా చెక్ చేయడం
        existing_like = await likes_col.find_one({
            "news_id": oid,
            "user_ip": user_ip
        })
        
        field = "likes" if action == "like" else "dislikes"
        opposite_field = "dislikes" if action == "like" else "likes"
        
        update_operations = {"$inc": {field: 1}}
        
        if existing_like:
            # యూజర్ ముందు రియాక్ట్ చేసినట్లయితే
            if existing_like.get("action") == action:
                raise HTTPException(status_code=400, detail="Already reacted")
            else:
                # రియాక్షన్ మార్పు
                update_operations["$inc"][opposite_field] = -1
        
        # న్యూస్ ని అప్‌డేట్ చేయడం
        result = await news_col.update_one({"_id": oid}, update_operations)
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="News not found")
        
        # లైక్ రికార్డ్ ని నవీకరించడం లేదా సృష్టించడం
        like_record = {
            "news_id": oid,
            "user_ip": user_ip,
            "action": action,
            "created_at": datetime.utcnow()
        }
        
        await likes_col.update_one(
            {"news_id": oid, "user_ip": user_ip},
            {"$set": like_record},
            upsert=True
        )
        
        # అప్‌డేట్ చేయబడిన న్యూస్ ని పొందడం
        updated_doc = await news_col.find_one({"_id": oid})
        
        return {
            "success": True,
            "likes": int(updated_doc.get("likes", 0)),
            "dislikes": int(updated_doc.get("dislikes", 0))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Reaction error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# -----------------------
# COMMENTS API
# -----------------------

@app.get("/api/news/{news_id}/comments", response_class=JSONResponse)
async def get_comments(news_id: str, limit: int = 50, skip: int = 0):
    """కామెంట్స్ ను పొందడం"""
    try:
        oid = ObjectId(news_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid news ID")
    
    try:
        cursor = comments_col.find({"news_id": oid}).sort("created_at", -1).skip(skip).limit(limit)
        
        items = []
        async for doc in cursor:
            created_at = doc.get("created_at")
            if isinstance(created_at, datetime):
                created_at_str = created_at.isoformat()
            else:
                created_at_str = str(created_at) if created_at else ""
            
            items.append({
                "id": str(doc.get("_id")),
                "text": doc.get("text", ""),
                "created_at": created_at_str
            })
        
        total = await comments_col.count_documents({"news_id": oid})
        
        return {
            "success": True,
            "items": items,
            "total": total,
            "has_more": (skip + len(items)) < total
        }
        
    except Exception as e:
        logger.error(f"Error fetching comments: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/news/{news_id}/comments", response_class=JSONResponse)
async def add_comment(news_id: str, payload: dict, request: Request):
    """కొత్త కామెంట్ జోడించడం"""
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Comment text cannot be empty")
    
    if len(text) > 1000:
        raise HTTPException(status_code=400, detail="Comment too long (max 1000 chars)")
    
    try:
        oid = ObjectId(news_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid news ID")
    
    try:
        # న్యూస్ ఉందో లేదో తనిఖీ
        news_exists = await news_col.find_one({"_id": oid})
        if not news_exists:
            raise HTTPException(status_code=404, detail="News not found")
        
        # కామెంట్ డాక్యుమెంట్
        comment_doc = {
            "news_id": oid,
            "text": text,
            "user_ip": request.client.host if request.client else "unknown",
            "created_at": datetime.utcnow(),
            "approved": True  # ప్రోడక్షన్ లో మార్చండి
        }
        
        # కామెంట్ ని ఇన్సర్ట్ చేయడం
        result = await comments_col.insert_one(comment_doc)
        
        # కామెంట్ కౌంట్ ని నవీకరించడం
        comment_count = await comments_col.count_documents({"news_id": oid})
        await news_col.update_one({"_id": oid}, {"$set": {"comment_count": comment_count}})
        
        return {
            "success": True,
            "id": str(result.inserted_id),
            "comment_count": comment_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding comment: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# -----------------------
# ADMIN & UTILITY ENDPOINTS
# -----------------------

@app.post("/api/admin/fetch-news", response_class=JSONResponse)
async def trigger_fetch(background_tasks: BackgroundTasks, secret: str = ""):
    """మాన్యువల్‌గా RSS ఫీడ్ ఫెచ్చింగ్"""
    if secret != settings.ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    background_tasks.add_task(fetch_all_feeds, max_items=30)
    
    return {"success": True, "message": "News fetch started in background"}

@app.get("/api/stats", response_class=JSONResponse)
async def get_stats():
    """సిస్టమ్ స్టాటిస్టిక్స్"""
    try:
        total_news = await news_col.count_documents({})
        total_comments = await comments_col.count_documents({})
        total_likes = await likes_col.count_documents({})
        
        # చివరి 24 గంటల న్యూస్
        day_ago = datetime.utcnow() - timedelta(days=1)
        recent_news = await news_col.count_documents({"created_at": {"$gte": day_ago}})
        
        return {
            "success": True,
            "stats": {
                "total_news": total_news,
                "total_comments": total_comments,
                "total_reactions": total_likes,
                "recent_news_24h": recent_news,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"}
        )

# -----------------------
# HEALTH CHECK
# -----------------------

@app.get("/health")
async def health_check():
    """హెల్త్ చెక్ ఎండ్‌పాయింట్"""
    try:
        # డేటాబేస్ కనెక్టివిటీ తనిఖీ
        await db.command("ping")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

# -----------------------
# STARTUP & SHUTDOWN
# -----------------------

@app.on_event("startup")
async def startup_event():
    """అప్లికేషన్ స్టార్ట్ అయినప్పుడు"""
    logger.info("Starting 24/7 Telugu News application...")
    
    # ఇండెక్స్‌లను సృష్టించడం
    await create_indexes()
    
    # ప్రారంభ RSS ఫీడ్ ఫెచ్చింగ్
    if os.getenv("AUTO_FETCH_ON_START", "true").lower() == "true":
        asyncio.create_task(periodic_fetch())
    
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    """అప్లికేషన్ షట్‌డౌన్ అయినప్పుడు"""
    logger.info("Shutting down application...")
    client.close()
    logger.info("Application shutdown complete")
