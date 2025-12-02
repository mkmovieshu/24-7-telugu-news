from datetime import datetime
from typing import List

import feedparser

from config import settings
from db import upsert_article
from summarize import summarize_article


def _parse_published(entry) -> datetime:
    try:
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
    except Exception:  # noqa: BLE001
        pass
    return datetime.utcnow()


def _get_text(entry) -> str:
    parts: List[str] = []
    title = getattr(entry, "title", "")
    summary = getattr(entry, "summary", "") or getattr(
        entry, "description", ""
    )
    content = ""

    if hasattr(entry, "content") and entry.content:
        try:
            content = entry.content[0].value
        except Exception:  # noqa: BLE001
            content = ""

    for piece in (title, summary, content):
        if piece:
            parts.append(str(piece))

    return "\n\n".join(parts)


def _get_image(entry) -> str | None:
    # Very rough: look for media_thumbnail or media_content
    media = getattr(entry, "media_thumbnail", None) or getattr(
        entry, "media_content", None
    )
    if media and isinstance(media, list):
        url = media[0].get("url")
        if url:
            return url
    return None


async def fetch_and_store_all_feeds() -> None:
    """
    Fetch all feeds from RSS_FEEDS and store+summarize them.
    """
    feeds_raw = settings.RSS_FEEDS.strip()
    if not feeds_raw:
        print("[WARN] No RSS_FEEDS configured")
        return

    feed_urls = [u.strip() for u in feeds_raw.split(",") if u.strip()]

    print(f"[INFO] Fetching {len(feed_urls)} RSS feeds")

    for feed_url in feed_urls:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed to parse feed {feed_url}: {exc}")
            continue

        source_title = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            link = getattr(entry, "link", None)
            title = getattr(entry, "title", "Untitled")
            if not link:
                continue

            text = _get_text(entry)
            published_at = _parse_published(entry)
            image_url = _get_image(entry)

            # Summarize using Groq (async)
            summary = await summarize_article(text)

            upsert_article(
                title=title,
                link=link,
                summary=summary,
                source=source_title,
                category=None,
                image_url=image_url,
                published_at=published_at,
            )

        print(f"[INFO] Finished feed {feed_url}")
