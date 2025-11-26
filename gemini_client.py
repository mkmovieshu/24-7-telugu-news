# gemini_client.py
import os
import requests
import json
import logging

logger = logging.getLogger("short-news-api")

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")

def summarize_text(title: str, content: str, model: str = None, max_output_tokens: int = 120) -> str:
    """
    Call Gemini 2.x via REST using generateContent.
    Returns short Telugu summary ~250–300 characters.
    """
    if not GOOGLE_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set in environment")

    model = model or DEFAULT_MODEL

    url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GOOGLE_KEY}"

    prompt_text = (
        "క్రింది వార్తను తెలుగులో 250–300 అక్షరాల చిన్న సమ్మరీగా రాయ్. "
        "న్యూట్రల్ టోన్, క్లిక్‌బైట్ లేకుండా. టైటిల్ రిపీట్ చేయకూడదు. "
        "పాయింట్స్ కాదు, చిన్న పారాగ్రాఫ్‌గా రాయ్.\n\n"
        f"TITLE: {title}\n\nCONTENT:\n{content}"
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": max_output_tokens
        }
    }

    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, json=body, timeout=25)
    logger.info("Gemini status: %s", resp.status_code)
    resp.raise_for_status()
    j = resp.json()

    # ---- extract text from Gemini 2.x response ----
    summary = ""

    try:
        candidates = j.get("candidates") or []
        if candidates:
            first = candidates[0]
            content_obj = first.get("content") or {}
            parts = content_obj.get("parts") or []
            texts = []
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    texts.append(part["text"])
            summary = " ".join(texts).strip()
    except Exception as e:
        logger.exception("Gemini parse failed: %s", str(e))

    # Fallbacks if above fails
    if not summary and isinstance(j, dict):
        # Sometimes APIs return top-level 'output_text' or 'output'
        summary = j.get("output_text") or j.get("output") or ""
        if isinstance(summary, dict):
            summary = json.dumps(summary)

    summary = (summary or "").strip()

    # log a bit for debug
    if not summary:
        logger.warning("Gemini returned empty summary for title: %s", title)

    return summary
