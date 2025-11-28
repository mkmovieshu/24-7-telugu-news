import logging
import re
from typing import Optional

import requests

# NOTE: config.py exposes GOOGLE_API_KEY and GEMINI_MODEL.
from config import GOOGLE_API_KEY, GEMINI_MODEL

logger = logging.getLogger("short-news-api")


def _keep_telugu_only(text: str) -> str:
    """
    Summaryలో ఉన్న English letters, symbols వగైరా తీసేసి
    తెలుగు + basic punctuation మాత్రమే ఉంచుతుంది.
    """
    if not text:
        return ""

    # తెలుగు unicode range: \u0C00-\u0C7F
    # digits + basic punctuation కూడా allow చేస్తున్నాం
    cleaned = re.sub(
        r"[^0-9\u0C00-\u0C7F\s\.\,\?\!\-\:\;\"\'\(\)]",
        " ",
        text,
    )

    # ఎక్కువ spaces/newlines ని normalize చేయడం
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def summarize_text(
    title: str,
    content: str,
    model: Optional[str] = None,
    max_output_tokens: int = 140,
) -> Optional[str]:
    """
    Gemini‌తో తెలుగు short summary తీసుకొచ్చే helper.

    - Output pure Telugu కావాలి (English words లేకుండా).
    - 2–3 sentences max.
    """
    api_key = GOOGLE_API_KEY
    if not api_key:
        logger.warning("Gemini API key (GOOGLE_API_KEY) not set; skipping summarization")
        return None

    model_name = model or GEMINI_MODEL
    url = (
        f"https://generativelanguage.googleapis.com/v1/models/"
        f"{model_name}:generateContent?key={api_key}"
    )

    # PROMPT: pure Telugu summary only
    prompt = (
        "క్రింద ఇచ్చిన తెలుగు వార్తను చాలా చిన్న సమరీగా మార్చండి.\n"
        "RULES:\n"
        "1. సమరీ పూర్తిగా తెలుగు లోనే ఉండాలి.\n"
        "2. English words, English sentences, transliteration (ఉదా: 'job mela', "
        "'Chief Minister', 'AP Skill Development Corporation') వాడకండి.\n"
        "3. 2 లేదా 3 వాక్యాలు, గరిష్టం 4 వాక్యాలు దాటకూడదు.\n"
        "4. బులెట్ పాయింట్లు, హ్యాష్‌ట్యాగ్లు, emojis, quotes పెట్టకండి.\n"
        "5. WhatsApp status లా natural conversational తెలుగు లో రాయండి.\n\n"
        f"శీర్షిక: {title}\n\n"
        "వార్త మొత్తం:\n"
        f"{content}\n\n"
        "ఇప్పుడు పైన ఉన్న సమాచారాన్ని బట్టి చివరి output గా **చిన్న తెలుగు సమరీ** మాత్రమే రాయండి."
    )

    body = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "text": prompt,
                    }
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.6,
            "topP": 0.9,
            "topK": 40,
            "maxOutputTokens": max_output_tokens,
        },
    }

    try:
        resp = requests.post(url, json=body, timeout=25)
    except Exception as e:
        logger.exception("Gemini summarize request failed: %s", e)
        return None

    logger.info("Gemini status: %s", resp.status_code)

    if resp.status_code != 200:
        try:
            text_preview = resp.text[:400]
        except Exception:
            text_preview = "<unreadable>"
        logger.error(
            "Gemini summarize failed (status %s): %s",
            resp.status_code,
            text_preview,
        )
        return None

    data = resp.json()
    logger.info("Gemini raw response (trimmed): %s", str(data)[:400])

    try:
        raw_summary = (
            data["candidates"][0]["content"]["parts"][0]["text"].strip()
        )
    except (KeyError, IndexError, TypeError) as e:
        logger.error("Unexpected Gemini response format: %s (%s)", data, e)
        return None

    telugu_only = _keep_telugu_only(raw_summary)

    # clean చేసిన తర్వాత text ఖాళీ అయ్యితే raw summary fallback
    final_summary = telugu_only or raw_summary.strip()

    logger.info(
        "Gemini summary lengths: raw=%d, telugu_only=%d",
        len(raw_summary),
        len(final_summary),
    )

    return final_summary
