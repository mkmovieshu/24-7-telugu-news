import os
from dotenv import load_dotenv

# Local development కోసం .env నుంచి load అవుతుంది.
# Render / Koyeb లాంటివి అయితే అక్కడి ENV నే వాడుకుంటుంది.
load_dotenv()

# === Core settings (ఇవి ఇప్పటికీ వాడుతున్నవి – పేర్లు మార్చొద్దు) ===
MONGO_URL = os.getenv("MONGO_URL")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "shortnews")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

DEFAULT_RSS = "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml"
RSS_FEEDS = [
    u.strip()
    for u in os.getenv("RSS_FEEDS", DEFAULT_RSS).split(",")
    if u.strip()
]

# Gemini model పేరు – future లో ENV నుంచి మార్చుకోవచ్చు
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

# === Dummy / Real mode switch ===
# USE_GEMINI=false  => Dummy summary మాత్రమే, API call ZERO
# USE_GEMINI=true   => నిజమైన Gemini API కి కాల్
USE_GEMINI = os.getenv("USE_GEMINI", "false").lower() in ("1", "true", "yes", "on")
