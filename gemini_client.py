import logging
from typing import Optional

import requests

from config import GEMINI_API_KEY, GEMINI_MODEL

log = logging.getLogger("short-news-api")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"


def summarize_text(
    title: str,
    content: str,
    model: Optional[str] = None,
    max_output_tokens: int = 160,
) -> str:
    """
    Call Gemini API and return Telugu short summary.
    If anything fails, return empty string so update() still works.
    """
    api_key = GEMINI_API_KEY
    model_name = model or GEMINI_MODEL

    if not api_key:
        log.warning("Gemini API key not configured, skipping summarize.")
        return ""

    url = f"{GEMINI_ENDPOINT}/{model_name}:generateContent?key={api_key}"

    system_prompt = (
        "నువ్వు Telugu short news editor. "
        "ఇచ్చిన title, content చూసి, క్లియర్‌గా, చదవడానికి కంఫర్ట్‌గా ఉండే "
        "సింగిల్ ప్యారాగ్రాఫ్‌లో తెలుగు సమరీ రాయాలి. "
        "ఇంగ్లీష్ words అవసరమైనప్పుడే ఉపయోగించు; possible అయితే pure తెలుగు లో రాయాలి. "
        "కొత్త sensational సమాచారం ఊహించి create చేయకూడదు. "
        "3–4 lines వరకూ natural length summary ఇవ్వాలి."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": system_prompt},
                    {
                        "text": (
                            f"TITLE:\n{title}\n\n"
                            f"CONTENT:\n{content}\n\n"
                            "OUTPUT:\nతెలుగులో మాత్రమే short summary రాయండి."
                        )
                    },
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
        if not summary:
            return ""

        # normalize whitespace
        summary = " ".join(summary.split())
        log.info("Gemini summary length: %d", len(summary))
        return summary
    except Exception as exc:
        log.error("Gemini summarize failed: %s", exc, exc_info=True)
        return ""
