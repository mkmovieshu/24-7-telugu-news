import re

from groq_client import async_summarize_text, GroqError


def clean_text(text: str) -> str:
    if not text:
        return ""
    # Remove HTML tags (very rough)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def needs_ai(text: str) -> bool:
    """
    Decide whether to call Groq or just use original text.
    We skip AI if text already very short.
    """
    if not text:
        return False
    return len(text) > 220  # characters


async def summarize_article(raw_text: str) -> str:
    """
    Main function used by fetch_rss.
    """
    text = clean_text(raw_text)

    if not text:
        return ""

    # If small text, don't waste tokens
    if not needs_ai(text):
        # Just return first 160 chars as "summary"
        return text[:160] + ("..." if len(text) > 160 else "")

    try:
        return await async_summarize_text(text, language="te")
    except GroqError as e:
        # On failure, fall back to trimmed original
        print(f"[WARN] Groq summarization failed: {e}")
        return text[:220] + ("..." if len(text) > 220 else "")
