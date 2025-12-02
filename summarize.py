import logging
import re
from typing import Optional

from config import GROQ_API_KEY

# Try to import Groq SDK, but don't crash if it's missing.
try:
    from groq import Groq  # type: ignore
except ImportError:  # pragma: no cover
    Groq = None  # type: ignore

logger = logging.getLogger("short-news-api")


def clean_text(text: str) -> str:
    """
    Remove HTML tags, extra spaces, and weird whitespace.
    """
    if not text:
        return ""

    # Remove script/style tags completely
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.S | re.I)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S | re.I)

    # Remove remaining HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def needs_ai(text: str) -> bool:
    """
    Decide if this item really needs AI summarization.

    - Very short items: no need
    - Longer / multi-sentence: use AI
    """
    if not text:
        return False

    cleaned = clean_text(text)
    if len(cleaned) < 120:
        return False

    # If there is at least one full-stop or multiple clauses, use AI
    if "." in cleaned or "?" in cleaned or "!" in cleaned or "।" in cleaned:
        return True

    return len(cleaned) > 160


def _get_groq_client() -> Optional["Groq"]:
    """
    Return Groq client if available & key is set, otherwise None.
    """
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured; summarization will be fallback only")
        return None

    if Groq is None:
        logger.warning("groq package not installed; run `pip install groq` and add it to requirements.txt")
        return None

    try:
        return Groq(api_key=GROQ_API_KEY)
    except Exception as e:  # pragma: no cover
        logger.exception("Failed to create Groq client: %s", e)
        return None


def _fallback_summary(text: str, max_chars: int = 400) -> str:
    """
    Simple non-AI fallback: trimmed & cleaned text.
    """
    cleaned = clean_text(text)
    if len(cleaned) <= max_chars:
        return cleaned
    return cleaned[: max_chars].rstrip() + "..."


def gemini_summarize(text: str, category: Optional[str] = None) -> str:
    """
    Kept old name `gemini_summarize` so the rest of the code doesn't break,
    but internally we now use Groq.

    - Input: full news text (optionally category)
    - Output: 1–2 line Telugu summary suitable for short-news app.
    """
    if not text:
        return ""

    client = _get_groq_client()
    if client is None:
        # No Groq / no key => fallback summary
        return _fallback_summary(text)

    cleaned = clean_text(text)

    system_prompt = (
        "You are a news summarization assistant for a Telugu short-news mobile app. "
        "Write very short, clear summaries in colloquial Telugu. "
        "Use 1–2 sentences only, no bullet points, no emojis. "
        "Do not add extra commentary; just the core news."
    )

    user_prompt = (
        "క్రింది వార్తను 1–2 చిన్న వాక్యాల్లో, "
        "ఫోన్ యాప్‌లో కనిపించేలా మాట్లాడే తెలుగు స్టైల్‌లో సారాంశం రాయండి.\n\n"
    )

    if category:
        user_prompt += f"కేటగిరీ: {category}\n\n"

    user_prompt += f"వార్త:\n{cleaned}"

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=256,
        )

        summary = (
            response.choices[0].message.content.strip()
            if response.choices
            else ""
        )

        if not summary:
            return _fallback_summary(text)

        # Extra cleanup: one-line, trimmed
        summary = re.sub(r"\s+", " ", summary).strip()
        return summary

    except Exception as e:  # pragma: no cover
        logger.exception("Groq summarization failed: %s", e)
        return _fallback_summary(text)
