import os
from google.generativeai import GenerativeModel
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL_NAME = "models/gemini-2.5-flash"

def summarize_news(title: str, content: str):
    # ❌ RULE 1: Very short title → NO AI
    if len(title) < 40 or not content:
        return content[:500], False

    prompt = f"""
క్రింది న్యూస్‌ని తెలుగు లో
అత్యవసర సమాచారం మాత్రమే ఉంచి
గరిష్టంగా 5 వాక్యాలు
500 అక్షరాలు దాటకుండా
నిష్పక్షపాతంగా రాయండి.

న్యూస్:
{content}
"""

    try:
        model = GenerativeModel(MODEL_NAME)
        result = model.generate_content(prompt)
        text = result.text.strip()

        # 🔪 HARD CUT (NO TRUST ON AI)
        return text[:500], True

    except Exception as e:
        # ❗ AI fail అయినా site పడకూడదు
        return content[:500], False
