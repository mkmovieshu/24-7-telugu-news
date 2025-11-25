# fetch_rss.py (replace existing)
import feedparser, requests, logging, traceback
from db import news_collection, db
from summarize import gemini_summarize, needs_ai, clean_text
from config import RSS_FEEDS
from datetime import datetime, timezone
import time

logging.basicConfig(level=logging.INFO)

def fetch_full_text(link):
    try:
        resp = requests.get(link, timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logging.warning("fetch_full_text failed for %s : %s", link, e)
        return ""

def process_rss(max_items_per_feed=20):
    try:
        total_inserted = 0
        for url in RSS_FEEDS:
            logging.info("Processing feed: %s", url)
            try:
                feed = feedparser.parse(url)
            except Exception as e:
                logging.exception("feedparser failed for %s", url)
                db["errors"].insert_one({
                    "stage":"feed_parse",
                    "feed":url,
                    "error": str(e),
                    "trace": traceback.format_exc(),
                    "ts": datetime.utcnow()
                })
                continue

            count = 0
            for entry in feed.entries:
                if count >= max_items_per_feed:
                    break
                title = entry.get("title","").strip()
                link = entry.get("link")
                if not link:
                    continue
                # dedupe by link
                if news_collection.find_one({"link": link}):
                    continue

                # prepare raw content
                raw = entry.get("summary", "") or (entry.get("content",[{}])[0].get("value","") if entry.get("content") else "")
                if needs_ai(raw):
                    html = fetch_full_text(link)
                    raw = (raw + " " + html)[:6000]

                try:
                    summary = gemini_summarize(title, raw)
                except Exception as e:
                    logging.exception("summarize failed for %s", link)
                    db["errors"].insert_one({
                        "stage":"summarize",
                        "link": link,
                        "title": title,
                        "error": str(e),
                        "trace": traceback.format_exc(),
                        "ts": datetime.utcnow()
                    })
                    summary = (title + " " + (raw[:250] if raw else ""))[:300]

                doc = {
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "category": entry.get("category", "General"),
                    "published": entry.get("published", datetime.utcnow().isoformat()),
                    "created_at": datetime.utcnow()
                }
                try:
                    news_collection.insert_one(doc)
                    logging.info("Inserted: %s", title)
                    total_inserted += 1
                except Exception as e:
                    logging.exception("mongo insert failed for %s", link)
                    db["errors"].insert_one({
                        "stage":"mongo_insert",
                        "link": link,
                        "title": title,
                        "error": str(e),
                        "trace": traceback.format_exc(),
                        "ts": datetime.utcnow()
                    })
                count += 1
                time.sleep(0.2)  # gentle throttle
        logging.info("process_rss complete. total_inserted=%d", total_inserted)
        return total_inserted
    except Exception as e:
        logging.exception("process_rss top-level exception")
        db["errors"].insert_one({
            "stage":"process_rss_top",
            "error": str(e),
            "trace": traceback.format_exc(),
            "ts": datetime.utcnow()
        })
        return 0

if __name__ == "__main__":
    process_rss()
