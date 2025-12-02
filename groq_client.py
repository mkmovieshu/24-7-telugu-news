from typing import Optional

from groq import Groq

from config import GROQ_API_KEY, GROQ_MODEL, USE_GROQ, logger

_client: Optional[Groq] = None

if USE_GROQ and GROQ_API_KEY:
    logger.info("Initializing Groq client")
    _client = Groq(api_key=GROQ_API_KEY)
else:
    logger.warning(
        "Groq is disabled or GROQ_API_KEY/GOOGLE_API_KEY not set – "
        "summaries will fall back to raw text."
    )


def summarize_text(prompt: str, max_tokens: int = 256) -> str:
    """
    LLM summarize call.
    మనం హ్యూమన్‌కు చూపించేది కాకుండా, summary generate చెయ్యడానికి
    మొత్తం prompt ఇక్కడ పంపుతాం.
    """
    if not _client:
        # LLM లేకపోతే, ఖర్చు తప్పించుకోవడానికి అదే టెక్స్ట్ రిటర్న్ చేస్తాం
        return prompt

    try:
        resp = _client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a concise Telugu news summarizer. "
                        "Always reply in natural Telugu. "
                        "Give a short, clear summary (2–3 lines) suitable "
                        "for a mobile news app."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        logger.exception("Groq summarization failed: %s", e)
        # Error వచ్చినప్పుడు కూడా యాప్ క్రాష్ కాకూడదు
        return prompt
