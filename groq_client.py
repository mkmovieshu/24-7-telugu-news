import httpx
from config import settings

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


class GroqError(Exception):
    pass


async def async_summarize_text(text: str, language: str = "te") -> str:
    """
    Async summarization using Groq Chat Completions API.
    language = 'te' => Telugu, 'en' => English, etc.
    """
    if not settings.USE_GROQ:
        raise GroqError("Groq summarization disabled via USE_GROQ=false")
    if not settings.GROQ_API_KEY:
        raise GroqError("GROQ_API_KEY is not set")

    system_prompt = (
        "You are a professional news editor. "
        "Summarize the given news article into 2 short bullet points in "
        f"{'Telugu' if language == 'te' else 'English'}. "
        "Keep total under 40 words. No extra commentary."
    )

    payload = {
        "model": settings.GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.3,
        "max_tokens": 160,
    }

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(GROQ_API_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            raise GroqError(
                f"Groq API error {resp.status_code}: {resp.text[:200]}"
            )

        data = resp.json()
        try:
            return (
                data["choices"][0]["message"]["content"]
                .strip()
                .replace("\n\n", "\n")
            )
        except Exception as exc:  # noqa: BLE001
            raise GroqError(f"Invalid Groq response: {data}") from exc
