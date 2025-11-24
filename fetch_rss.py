import feedparser
import requests
from db import news_collection
from summarize import summarize_text
from config import RSS_FEEDS
from datetime import datetime

def fetch_full_text(link):
    try:
        resp = requests.get(link, timeout=4)
        return resp.text
    except:
        return ""
    

def process_rss():
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            title = entry.title
            link = entry.link

            if news_collection.find_one({"link": link}):
                continue

            fulltext = fetch_full_text(link)
            summary = summarize_text(title, fulltext)

            doc = {
                "title": title,
                "summary": summary,
                "link": link,
                "category": entry.get("category", "General"),
                "published": entry.get("published", str(datetime.utcnow())),
            }

            news_collection.insert_one(doc)
            print("Added:", title)
