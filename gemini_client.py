import logging
from typing import Optional

import requests

from config import GOOGLE_API_KEY, GEMINI_MODEL, USE_GEMINI

log = logging.getLogger("short-news-api")

GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"


def _strip_english_letters(text: str) -> str:
    """
    Telugu-only summary కోసం అతి basic filtering.
    English A-Z, a-z letters తొలగిస్తాం. Digits, punctuation వదిలేస్తాం.
    """
    out_chars = []
    for ch in text:
        if "A" <= ch <= "Z" or "a" <= ch <= "z":
            continue
        out_chars.append(ch)
    return "".join(out_chars)


def _dummy_summary(title: str, content: str, max_output_tokens: int) -> str:
    """
    Dummy mode: ఎలాంటి HTTP call లేకుండా లోకల్‌గా summary తయారు చేస్తుంది.
    UI / App flow test చెయ్యడానికి ఇది చాలు.
    """
    # title + content నుంచి ఒక చిన్న text తయారు చెయ్యి
    base = f"{title.strip()} — {content.strip()}"

    # English letters తొలగించు (max pure Telugu look కోసం)
    base = _strip_english_letters(base)

    # Whitespace normalize
    base = " ".join(base.split())

    # max_output_tokens ~ words count అనుకుంటే, chars ని కొంచెం అంచనా వేయాలి
    # roughly 3 chars per token అనుకుని కట్ చేస్తాం
    max_chars = max_output_tokens * 3
    if len(base) > max_chars:
        base = base[:max_chars].rstrip() + "…"

    return base or "ఈ వార్తకు సమరీ అందుబాటులో లేదు."


def summarize_text(
    title: str,
    content: str,
    model: Optional[str] = None,
    max_output_tokens: int = 160,
) -> str:
    """
    Telugu short summary తయారు చెయ్యడానికి function.

    - USE_GEMINI == False అయితే: dummy summary (NO API CALL)
    - USE_GEMINI == True అయితే: Gemini API కి call
    - ఏదైనా error / quota issues వచ్చినా: "" return (raw_summary వాడుకోవచ్చు)
    """

    # 1️⃣ Dummy mode: API కి ఒక్క hit కూడా పెట్టకూడదనుకుంటే
    if not USE_GEMINI:
        log.info("Gemini dummy mode ON (USE_GEMINI is false). Using local summary.")
        return _dummy_summary(title, content, max_output_tokens)

    # 2️⃣ Real Gemini mode
    api_key = GOOGLE_API_KEY
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
        # quota / 429 / ఏదైనా error -> empty string
        log.error("Gemini summarize failed: %s", exc, exc_info=True)
        return ""
