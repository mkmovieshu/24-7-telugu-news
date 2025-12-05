# app.py - మెయిన్ FastAPI అప్లికేషన్
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from datetime import datetime
from config import MONGO_URL, DB_NAME, APP_NAME, RSS_FEEDS

# FastAPI అప్లికేషన్
app = FastAPI(title=APP_NAME)

# స్టాటిక్ ఫైల్స్
app.mount("/static", StaticFiles(directory="static"), name="static")

# మాంగోడీబీ కనెక్షన్
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
news_col = db["news"]

# ==================== HELPER FUNCTIONS ====================
async def get_news_count():
    """మొత్తం న్యూస్ కౌంట్"""
    return await news_col.count_documents({})

# ==================== ROUTES ====================
@app.get("/", response_class=HTMLResponse)
async def home():
    """హోమ్ పేజీ"""
    html = """
    <!DOCTYPE html>
    <html lang="te">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>24/7 తెలుగు న్యూస్</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .stats { background: #3498db; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }
            .api-link { background: #2ecc71; color: white; padding: 10px; display: inline-block; margin: 10px 5px; border-radius: 5px; text-decoration: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 24/7 తెలుగు న్యూస్</h1>
            <p>AI-పవర్డ్ తెలుగు న్యూస్ సమ్మరీస్</p>
            
            <div class="stats">
                <h3>స్టాటస్: <span id="status">లోడ్ అవుతోంది...</span></h3>
                <p>న్యూస్ కౌంట్: <span id="count">0</span></p>
            </div>
            
            <h3>API ఎండ్‌పాయింట్స్:</h3>
            <a class="api-link" href="/news">/news - అన్ని న్యూస్</a>
            <a class="api-link" href="/health">/health - హెల్త్ చెక్</a>
            <a class="api-link" href="/stats">/stats - స్టాటిస్టిక్స్</a>
            
            <h3 style="margin-top: 30px;">రియల్-టైమ్ న్యూస్ వెబ్‌సైట్ త్వరలో...</h3>
        </div>
        
        <script>
            async function loadStats() {
                try {
                    const res = await fetch('/stats');
                    const data = await res.json();
                    document.getElementById('count').textContent = data.total_news;
                    document.getElementById('status').textContent = 'కనెక్ట్ అయింది ✅';
                } catch (error) {
                    document.getElementById('status').textContent = 'ఎర్రర్ ❌';
                }
            }
            loadStats();
        </script>
    </body>
    </html>
    """
    return html

@app.get("/news")
async def get_news():
    """అన్ని న్యూస్ పొందడం"""
    try:
        cursor = news_col.find({}).sort("created_at", -1).limit(50)
        news_list = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            news_list.append(doc)
        return {"success": True, "count": len(news_list), "news": news_list}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/health")
async def health_check():
    """హెల్త్ చెక్"""
    try:
        await db.command("ping")
        return {
            "status": "healthy",
            "service": APP_NAME,
            "timestamp": datetime.now().isoformat(),
            "database": "connected"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_stats():
    """స్టాటిస్టిక్స్"""
    try:
        total_news = await get_news_count()
        return {
            "success": True,
            "total_news": total_news,
            "rss_feeds": len(RSS_FEEDS),
            "app_name": APP_NAME,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/test")
async def test_api():
    """టెస్ట్ API"""
    return {"message": "API పనిచేస్తోంది!", "language": "తెలుగు"}

# ==================== STARTUP ====================
@app.on_event("startup")
async def startup_event():
    """అప్లికేషన్ స్టార్ట్ అయినప్పుడు"""
    print(f"🚀 {APP_NAME} స్టార్ట్ అయింది")
    print(f"📡 RSS ఫీడ్స్: {len(RSS_FEEDS)}")
    print(f"🗄️ డేటాబేస్: {DB_NAME}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
