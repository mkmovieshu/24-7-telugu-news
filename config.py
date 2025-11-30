# config.py

import os
from dotenv import load_dotenv

# Load .env if present (local development)
load_dotenv()

# === Core settings ===
MONGO_URL = os.getenv("MONGO_URL", "").strip()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews").strip()
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "").strip()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()

# Comma-separated RSS feed URLs
RSS_FEEDS_RAW = os.getenv("RSS_FEEDS", "").strip()
RSS_FEEDS = [u.strip() for u in RSS_FEEDS_RAW.split(",") if u.strip()]

# === Gemini model config ===
# IMPORTANT: ఇక్కడ "models/" పెట్టకూడదు.
# Endpoint లో ఇప్పటికే /models ఉంది; కాబట్టి plain model id మాత్రమే.
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite").strip()

# Logging level
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper() or "INFO"
