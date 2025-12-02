import re

from config import logger
from gemini_client import summarize_text


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    # HTML tags, extra spaces తీసేయడం
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def needs_ai(text: str, max_chars: int = 280) -> bool:
    """
    text చిన్నదైతే LLM call skip చేసి టోకెన్లు సేవ్ చేసుకుంటాం.
    """
    if not text:
        return False
    return len(text) > max_chars


def gemini_summarize(text: str, title: str = "") -> str:
    """
    బయట కోడ్‌లో ఉన్న function పేరు మార్చకుండా ఉంచాం (gemini_summarize),
    కానీ లోపల Groq ను వాడుతున్నాం.
    """
    text = clean_text(text)

    if not text:
        return ""

    # Prompt in Telugu – news app కి తగ్గట్టు చిన్న summary
    prompt = (
        "కింద ఇచ్చిన వార్తని 2–3 లైన్లలో, సింపుల్ తెలుగు లో "
        "చిన్న షార్ట్ న్యూస్‌లా సమ్మరీ చెయ్యి. "
        "అవసరమైన పాయింట్లు మాత్రమే ఉంచు, క్లిక్‌బైట్ మాటలు వాడకు.\n\n"
    )
    if title:
        prompt += f"శీర్షిక: {title}\n"
    prompt += f"వివరాలు:\n{text}"

    summary = summarize_text(prompt, max_tokens=200)
    summary = clean_text(summary)

    if not summary:
        # LLM ఏదైనా గందరగోళం చేస్తే, అసలు టెక్స్ట్ నుంచి truncate
        logger.warning("Empty summary from LLM, falling back to original text")
        return text[:250]

    return summary
