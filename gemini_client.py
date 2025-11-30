import logging
from typing import Optional
import requests

from config import GOOGLE_API_KEY, GEMINI_MODEL

log = logging.getLogger("short-news-api")

# FIXED ENDPOINT (VERY IMPORTANT)
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta"


def summarize_text(
    title: str,
    content: str,
    model: Optional[str] = None,
    max_output_tokens: int = 160,
) -> str:

    api_key = GOOGLE_API_KEY
    model_name = model or GEMINI_MODEL

    if not api_key:
        log.warning("Gemini API key not configured, skipping summarize.")
        return ""

    url = f"{GEMINI_ENDPOINT}/models/{model_name}:generateContent?key={api_key}"

    system_prompt = (
        "నీ పని Telugu short news editorలా పనిచేయడం. "
        "ఇచ్చిన title, content చూడి clean, pure Teluguలో short summary ఇవ్వాలి. "
        "అవసరం అయితే తప్ప English words వాడకూడదు. "
        "ఫేక్ facts create చేయకూడదు."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {"text": f"TITLE:\n{title}\n\nCONTENT:\n{content}\n\nOUTPUT: Telugu summary only."},
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.3,
            "topP": 0.8,
            "topK": 40,
            "maxOutputTokens": max_output_tokens,
        },
    }

    try:
        resp = requests.post(url, json=payload, timeout=20)
        log.info("Gemini status: %s", resp.status_code)
        resp.raise_for_status()
        data = resp.json()

        parts = (
            data.get("candidates", [{}])[0]
            .get("content", {})
            .get("parts", [])
        )
        summary = "".join(p.get("text", "") for p in parts).strip()
        return " ".join(summary.split())
    except Exception as exc:
        log.error("Gemini summarize failed: %s", exc, exc_info=True)
        return ""
