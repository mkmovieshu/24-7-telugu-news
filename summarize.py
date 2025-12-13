# summarize.py
import os
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)

def summarize_news(title: str, content: str, max_chars: int = 500):
    """
    Returns (summary_text, ai_used: bool)
    """

    # 🔒 AI వాడకుండా నేరుగా content చిన్నదైతే
    if content and len(content) <= max_chars:
        return content.strip(), False

    prompt = f"""
క్రింది న్యూస్‌ని తెలుగులో {max_chars} అక్షరాల లోపల స్పష్టంగా, వార్తలా సమరీ చెయ్యి.
అవసరం లేని ఉపోద్ఘాతం వద్దు.

Title:
{title}

Content:
{content}
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )

        text = response.text.strip()

        # hard safety cut
        return text[:max_chars], True

    except Exception as e:
        # 🔥 AI fail అయితే RSS content fallback
        fallback = content[:max_chars] if content else title
        return fallback, False
