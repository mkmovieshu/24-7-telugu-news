from __future__ import annotations

from datetime import datetime, timezone
from typing import List

import feedparser

from config import (
    RSS_FEEDS,
    MAX_ITEMS_PER_FEED,
    MAX_ITEMS_PER_RUN,
    logger,
)
from db import news_collection
from summarize import gemini_summarize, needs_ai, clean_text


# English + Telugu hype keywords
HYPE_KEYWORDS = [
    # English
    "breaking",
    "live",
    "big",
    "shocking",
    "sensational",
    "exclusive",
    "viral",
    "update",
    "alert",
    # Telugu
    "బ్రేకింగ్",
    "లైవ్",
    "తాజా",
    "తీవ్ర",
    "సెన్సేషన్",
    "షాకింగ్",
    "వైరల్",
    "అత్యవసరం",
]


def _hype_score(title: str, summary: str) -> int:
    """
    చాలా సింపుల్ స్కోరింగ్ – keywords + కొంచెం heuristics.
    """
    title_l = title.lower()
    summary_l = summary.lower()
    score = 0

    for kw in HYPE_KEYWORDS:
        kw_l = kw.lower()
        if kw_l in title_l:
            score += 3
        if kw_l in summary_l:
            score += 2

    # Numbers ఉంటే (ఎన్నికలు, స్కోర్లు వంటివి) కొంచెం weight
    if any(ch.isdigit() for ch in title_l):
        score += 1

    # title ఎక్కువ లెంగ్త్ ఉంటే చిన్న బోనస్
    if len(title_l) > 50:
        score += 1

    return score


def _parse_rss_urls() -> List[str]:
    return [u.strip() for u in RSS_FEEDS.split(",") if u.strip()]


def _get_published_at(entry) -> datetime:
    dt_struct = (
        getattr(entry, "published_parsed", None)
        or getattr(entry, "updated_parsed", None)
        or entry.get("published_parsed")
        or entry.get("updated_parsed")
    )
    if dt_struct:
        return datetime(
            dt_struct.tm_year,
            dt_struct.tm_mon,
            dt_struct.tm_mday,
            dt_struct.tm_hour,
            dt_struct.tm_min,
            dt_struct.tm_sec,
            tzinfo=timezone.utc,
        )
    return datetime.now(timezone.utc)


def _pick_top_hype_items(feed_url: str) -> List[dict]:
    """
    ఒక్క feed లో నుంచి hype score ఆధారంగా top N (MAX_ITEMS_PER_FEED) items తీసుకుంటాం.
    """
    parsed = feedparser.parse(feed_url)
    items = []

    for entry in parsed.entries:
        title = clean_text(getattr(entry, "title", "") or entry.get("title", ""))
        summary = clean_text(
            getattr(entry, "summary", "")
            or entry.get("summary", "")
            or entry.get("description", "")
        )

        link = getattr(entry, "link", "") or entry.get("link", "")
        if not link:
            continue

        score = _hype_score(title, summary)
        items.append(
            {
                "entry": entry,
                "title": title,
                "summary": summary,
                "link": link,
                "score": score,
            }
        )

    # Hype ఎక్కువ ఉన్నవి మొదట
    items.sort(key=lambda x: x["score"], reverse=True)

    # ఒక్క feed నుంచి గరిష్టంగా MAX_ITEMS_PER_FEED మాత్రమే
    return items[:MAX_ITEMS_PER_FEED]


def _store_item(item: dict, source_url: str) -> bool:
    """
    ఒక్క వార్తని DB లో save చెయ్యడం.
    ఇప్పటికే ఉంటే skip => False
    కొత్తది అయితే insert చేసి True రిటర్న్.
    """
    link = item["link"]

    if news_collection.find_one({"link": link}):
        return False

    entry = item["entry"]
    title = item["title"]
    summary = item["summary"]

    content = summary or title

    if needs_ai(content):
        final_summary = gemini_summarize(content, title=title)
    else:
        final_summary = content

    doc = {
        "title": title,
        "summary": final_summary,
        "link": link,
        "source": source_url,
        "published_at": _get_published_at(entry),
        "created_at": datetime.now(timezone.utc),
    }

    news_collection.insert_one(doc)
    return True


def fetch_and_store_all_feeds() -> int:
    """
    మొత్తం ఫీడ్స్ నుంచి హైప్ ఉన్న న్యూస్ మాత్రమే తీసుకుని,
    MAX_ITEMS_PER_RUN కి మించినవి insert చెయ్యకుండా stop అవుతుంది.
    """
    urls = _parse_rss_urls()
    if not urls:
        logger.warning("No RSS_FEEDS configured")
        return 0

    total_inserted = 0

    for url in urls:
        if total_inserted >= MAX_ITEMS_PER_RUN:
            break

        try:
            logger.info("Fetching feed: %s", url)
            items = _pick_top_hype_items(url)
            logger.info(
                "Feed %s -> selected %d hype items", url, len(items)
            )

            for item in items:
                if total_inserted >= MAX_ITEMS_PER_RUN:
                    break
                if _store_item(item, url):
                    total_inserted += 1

        except Exception as e:
            logger.exception("Failed to process feed %s: %s", url, e)

    logger.info("RSS fetch complete. Inserted %d items", total_inserted)
    return total_inserted


if __name__ == "__main__":
    inserted = fetch_and_store_all_feeds()
    print(f"Inserted {inserted} news items")
