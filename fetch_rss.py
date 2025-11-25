import feedparser, requests, logging
from db import news_collection
from summarize import gemini_summarize, needs_ai, clean_text
from config import RSS_FEEDS
from datetime import datetime

def fetch_full_text(link):
    try:
        resp = requests.get(link, timeout=5, headers={"User-Agent":"Mozilla/5.0"})
        return resp.text
    except Exception as e:
        logging.warning("Failed fetch full text %s : %s", link, e)
        return ""

def process_rss():
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for entry in feed.entries:
            title = entry.get("title","").strip()
            link = entry.get("link")
            if not link or news_collection.find_one({"link": link}):
                continue
            raw = ""
            # try to get content snippet if available in feed
            raw = entry.get("summary", "") or entry.get("content",[{}])[0].get("value","")
            # fetch article HTML only if needed
            if needs_ai(raw):
                html = fetch_full_text(link)
                raw = raw + " " + (html[:3000] if html else "")
            # generate summary
            summary = gemini_summarize(title, raw)
            doc = {
                "title": title,
                "summary": summary,
                "link": link,
                "category": entry.get("category", "General"),
                "published": entry.get("published", datetime.utcnow().isoformat()),
                "created_at": datetime.utcnow()
            }
            news_collection.insert_one(doc)
            logging.info("Inserted: %s", title)

if __name__ == "__main__":
    process_rss()
