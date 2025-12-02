import os
import logging
import re
from typing import Any

try:
    from groq import Groq
except ImportError:
    Groq = None  # type: ignore

# --- Logging ---
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=LOG_LEVEL)
logger = logging.getLogger("short-news-api")

# --- Groq client ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
_groq_client: Any = None
if GROQ_API_KEY and Groq is not None:
    _groq_client = Groq(api_key=GROQ_API_KEY)
    logger.info("Groq client initialized for summaries")
else:
    logger.warning(
        "GROQ_API_KEY missing or groq library not installed. "
        "Falling back to trimmed original text for summaries."
    )


def clean_text(text: str) -> str:
    """
    RSS లో వచ్చే HTML, scripts, extra whitespace తీసేసే ఫంక్షన్.
    """
    if not text:
        return ""

    # Remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)
    # Unescape basic HTML entities
    text = (
        text.replace("&nbsp;", " ")
        .replace("&amp;", "&")
        .replace("&quot;", '"')
        .replace("&#39;", "'")
    )
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def needs_ai(text: str) -> bool:
    """
    ఇప్పుడు కాపీ రైట్ టెన్షన్ తగ్గించేందుకు
    **ప్రతి న్యూస్‌కి** AI సమ్మరీ జనరేట్ చేస్తాం.
    """
    text = (text or "").strip()
    return bool(text)


def _fallback_short(text: str, max_words: int = 35) -> str:
    """
    Groq fail అయ్యినా లేదా API key లేకపోయినా, ఒరిజినల్
    టెక్స్ట్ నుంచి చిన్న snippet మాత్రమే ఉపయోగించే fallback.
    """
    words = clean_text(text).split()
    if len(words) <= max_words:
        return " ".join(words)
    return " ".join(words[:max_words]) + "…"


_SYSTEM_PROMPT = (
    "నువ్వు ఒక తెలుగు షార్ట్ న్యూస్ ఎడిటర్.\n\n"
    "క్రింద ఇచ్చిన వార్త ఆధారంగా 100% కొత్తగా, నీ మాటల్లో రాయాలి.\n"
    "అసలు వెబ్‌సైట్ లో ఉన్న వాక్యాలు లేదా పెద్ద పదబంధాలు "
    "మళ్లీ కాపీ చేయకూడదు.\n\n"
    "రూల్స్:\n"
    "- గరిష్టం 2 వాక్యాలు మాత్రమే.\n"
    "- మొత్తం పొడవు సుమారుని 25–35 పదాలు.\n"
    "- సింపుల్, క్లియర్ తెలుగు. క్లిక్‌బైట్ లాంటి మాటలు వద్దు.\n"
    "- వెబ్‌సైట్ పేరు, రిపోర్టర్ పేరు, తేదీ వంటివి అవసరంలేకుంటే mention చేయకూడదు.\n"
)


def gemini_summarize(*args, **kwargs) -> str:
    """
    పాత కోడ్ లో ఫంక్షన్ పేరు 'gemini_summarize' గా ఉన్నందుకు,
    అదే పేరు ఉంచి లోపల Groq ని యూజ్ చేస్తున్నాం.

    Signature ఎలాగైనా పాస్ అయినా first argument/text నుంచే
    summary తయారు చేస్తాం.
    """
    # --- figure out text argument safely ---
    text = ""
    if args:
        text = args[0] or ""
    elif "text" in kwargs:
        text = kwargs.get("text") or ""
    else:
        logger.warning("gemini_summarize called without text; returning empty string")
        return ""

    text = clean_text(str(text))
    if not text:
        return ""

    # Groq not configured -> fallback
    if not _groq_client:
        logger.warning("Groq client not available, using fallback summary")
        return _fallback_short(text)

    try:
        logger.debug("Calling Groq for short Telugu summary")
        completion = _groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            temperature=0.4,
            max_tokens=120,  # 2 చిన్న వాక్యాలకు చాలుతుంది
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
        )

        summary = completion.choices[0].message.content.strip()
        summary = clean_text(summary)

        # Safety: చాలా పెద్దగా వస్తే కూడా కట్ చెయ్యి
        return _fallback_short(summary, max_words=40)
    except Exception as e:
        logger.error("Groq summarize failed: %s", e)
        return _fallback_short(text)
