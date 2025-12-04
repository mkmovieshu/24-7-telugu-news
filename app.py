# app.py
import os
import threading
import time
from datetime import datetime, timedelta
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, send_from_directory, abort
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv

# try to use summarize.summarize_item if present
try:
    from summarize import summarize_item
except Exception:
    def summarize_item(item):
        if not item:
            return ""
        s = item.get("summary") or item.get("raw_summary") or ""
        if s:
            return s if len(s) < 800 else s[:800] + "..."
        title = item.get("title") or ""
        return (title + " " + s)[:800]

load_dotenv()

MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI") or "mongodb://localhost:27017"
DB_NAME = os.getenv("DB_NAME") or "shortnews"
COL_NAME = os.getenv("COL_NAME") or "news"
CLEANUP_INTERVAL_MINUTES = int(os.getenv("CLEANUP_INTERVAL_MINUTES") or 30)

app = Flask(__name__, static_folder="static", template_folder="ui")
CORS(app)

# Mongo client
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COL_NAME]
likes_coll = db.get_collection("likes")
comments_coll = db.get_collection("comments")

# Ensure TTL index for auto-delete after 24h
try:
    # if created_at is datetime, expireAfterSeconds will auto-delete
    collection.create_index("created_at", expireAfterSeconds=86400)
except Exception as e:
    app.logger.info("Could not create TTL index or index exists: %s", e)

def doc_to_public(doc):
    if not doc:
        return None
    out = {
        "id": str(doc.get("_id")),
        "title": doc.get("title"),
        "summary": doc.get("summary") or doc.get("raw_summary") or "",
        "link": doc.get("link"),
        "published": doc.get("published"),
        "source": doc.get("source"),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "image": doc.get("image") if doc.get("image") else ""
    }
    return out

@app.route("/news", methods=["GET"])
def get_news():
    try:
        limit = int(request.args.get("limit", 50))
    except:
        limit = 50
    try:
        skip = int(request.args.get("skip", 0))
    except:
        skip = 0

    cursor = collection.find().sort("created_at", -1).skip(skip).limit(limit)
    items = []
    for d in cursor:
        p = doc_to_public(d)
        # ensure summary exists, else generate on the fly
        if not p["summary"]:
            p["summary"] = summarize_item(d)
        # likes/dislikes aggregated
        stat = likes_coll.find_one({"news_id": d["_id"]})
        p["likes"] = stat.get("likes", 0) if stat else 0
        p["dislikes"] = stat.get("dislikes", 0) if stat else 0
        items.append(p)
    return jsonify({"items": items})

@app.route("/news/<news_id>", methods=["GET"])
def get_single_news(news_id):
    try:
        doc = collection.find_one({"_id": ObjectId(news_id)})
    except Exception:
        return abort(404)
    if not doc:
        return abort(404)
    out = doc_to_public(doc)
    stat = likes_coll.find_one({"news_id": ObjectId(news_id)})
    out["likes"] = stat.get("likes", 0) if stat else 0
    out["dislikes"] = stat.get("dislikes", 0) if stat else 0
    comms = list(comments_coll.find({"news_id": ObjectId(news_id)}).sort("created_at", -1))
    out["comments"] = [{"text": c.get("text"), "created_at": c.get("created_at").isoformat() if c.get("created_at") else None} for c in comms]
    return jsonify(out)

@app.route("/likes/<news_id>", methods=["POST"])
def post_like(news_id):
    body = request.get_json() or {}
    t = body.get("type", "like")
    try:
        oid = ObjectId(news_id)
    except:
        return abort(400)
    stat = likes_coll.find_one({"news_id": oid})
    if not stat:
        likes_coll.insert_one({"news_id": oid, "likes": 0, "dislikes": 0})
        stat = likes_coll.find_one({"news_id": oid})
    if t == "like":
        likes_coll.update_one({"news_id": oid}, {"$inc": {"likes": 1}})
    else:
        likes_coll.update_one({"news_id": oid}, {"$inc": {"dislikes": 1}})
    stat = likes_coll.find_one({"news_id": oid})
    return jsonify({"likes": stat.get("likes", 0), "dislikes": stat.get("dislikes", 0)})

@app.route("/comments/<news_id>", methods=["POST"])
def post_comment(news_id):
    body = request.get_json() or {}
    text = body.get("text", "").strip()
    if not text:
        return abort(400)
    try:
        oid = ObjectId(news_id)
    except:
        return abort(400)
    doc = {"news_id": oid, "text": text, "created_at": datetime.utcnow()}
    comments_coll.insert_one(doc)
    return jsonify({"ok": True, "comment": {"text": text, "created_at": doc["created_at"].isoformat()}})

@app.route("/read/<news_id>")
def read_more(news_id):
    try:
        doc = collection.find_one({"_id": ObjectId(news_id)})
    except Exception:
        return abort(404)
    if not doc:
        return abort(404)
    link = doc.get("link")
    if link:
        return jsonify({"redirect": link})
    return abort(404)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path == "" or path == "news":
        return send_from_directory("ui", "app.html")
    if path.startswith("static/"):
        file_path = path[len("static/"):]
        return send_from_directory("static", file_path)
    try:
        return send_from_directory("ui", path)
    except Exception:
        return send_from_directory("ui", "app.html")

def cleanup_worker():
    while True:
        try:
            cutoff = datetime.utcnow() - timedelta(hours=24)
            # delete old news (TTL index handles this too)
            collection.delete_many({"created_at": {"$lt": cutoff}})
            # delete comments older than cutoff
            comments_coll.delete_many({"created_at": {"$lt": cutoff}})
            # optionally remove likes for non-existing news (non-critical)
        except Exception as e:
            app.logger.error("Cleanup error: %s", e)
        time.sleep(CLEANUP_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    t = threading.Thread(target=cleanup_worker, daemon=True)
    t.start()
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")

if not MONGO_URL:
    # Development fallback: allow process to start, but don't connect to DB.
    # This avoids process crash on start when env var not set (Render / local dev).
    # When MONGO_URL is not set, the endpoints that need DB will return meaningful errors.
    import logging
    logging.warning("MONGO_URL not set — running in 'no-db' fallback mode.")
    client = None
    db = None
    news_col = None
    comments_col = None
else:
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
    news_col = db["news"]
    comments_col = db["comments"]
