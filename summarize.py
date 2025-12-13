# summarize.py
import os
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is missing")

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

def summarize_news(title: str, content: str, max_chars: int = 500):
    """
    Returns (summary_text, ai_used: bool)
    """

    # చిన్న న్యూస్ అయితే AI వద్దు
    if content and len(content) <= max_chars:
        return content.strip(), False

    prompt = f"""
క్రింది వార్తను తెలుగులో {max_chars} అక్షరాల లోపల స్పష్టంగా సమరీ చెయ్యి.
అవసరం లేని ఉపోద్ఘాతం వద్దు.

శీర్షిక:
{title}

వార్త:
{content}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text[:max_chars], True

    except Exception as e:
        # AI fail అయితే fallback
        fallback = content[:max_chars] if content else title
        return fallback, False
