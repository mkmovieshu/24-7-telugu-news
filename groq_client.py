# groq_client.py

import logging
from typing import Optional

from config import GROQ_API_KEY, GROQ_MODEL, USE_GROQ

logger = logging.getLogger("short-news-api")

try:
    from groq import Groq  # type: ignore
except ImportError:
    Groq = None  # type: ignore


def _make_client() -> Optional["Groq"]:
    """
    Create Groq client only if:
    - USE_GROQ is True
    - GROQ_API_KEY is set
    - groq library is installed
    """
    if not USE_GROQ:
        logger.info("USE_GROQ is False → using trimmed text summaries.")
        return None

    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not set → using trimmed text summaries.")
        return None

    if Groq is None:
        logger.warning("groq library not installed → using trimmed text summaries.")
        return None

    return Groq(api_key=GROQ_API_KEY)


_client = _make_client()


def summarize_text(text: str, max_tokens: int = 512) -> str:
    """
    If Groq client is available, call the API and return summary.
    Else just return trimmed original text (fallback).
    """
    # Fallback – no client / no key / no lib
    if not _client:
        return text[:max_tokens]

    try:
        resp = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "తెలుగులో చాలా చిన్న, క్లియర్ short news summary ఇవ్వు. "
                        "Clickbait లేకుండా, single paragraph లో."
                    ),
                },
                {"role": "user", "content": text},
            ],
            max_tokens=max_tokens,
            temperature=0.3,
        )
        summary = resp.choices[0].message.content.strip()
        return summary or text[:max_tokens]
    except Exception as e:
        logger.error("Groq summarize failed: %s", e)
        return text[:max_tokens]
