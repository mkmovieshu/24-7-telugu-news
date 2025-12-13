import os
import logging
from google import genai
from google.genai.errors import APIError 
# config.py నుండి GOOGLE_API_KEY (ఇదే Gemini కీ) ని ఇంపోర్ట్ చేసుకోవచ్చు,
# కానీ సులభం కోసం ఇక్కడ os.getenv ఉపయోగిద్దాం.

logger = logging.getLogger('summarize')
logger.setLevel(logging.INFO)

# ==============================================================================
# 1. Gemini API సెటప్
# ==============================================================================

# config.py లో GOOGLE_API_KEY గా సెట్ చేసినప్పటికీ, 
# ఎన్విరాన్‌మెంట్ వేరియబుల్‌గా 'GEMINI_API_KEY' లేదా 'GOOGLE_API_KEY' లో ఒకదాన్ని ఉపయోగించండి.
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") 

gemini_client = None
MODEL_NAME = "gemini-2.5-flash"

if not GEMINI_API_KEY:
    logger.warning("GOOGLE_API_KEY (Gemini) అందుబాటులో లేదు. AI సారాంశం పనిచేయదు.")
else:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel(MODEL_NAME)
        logger.info(f"Gemini క్లయింట్ సెటప్ చేయబడింది. మోడల్: {MODEL_NAME}")
    except Exception as e:
        logger.error(f"Gemini క్లయింట్ ప్రారంభించడంలో లోపం: {e}")


# ==============================================================================
# 2. సారాంశం ఫంక్షన్
# ==============================================================================

def summarize_news(title: str, content: str, max_chars: int = 500):
    """
    వార్తను తెలుగులో సారాంశం చేసి తిరిగి పంపుతుంది. 
    Returns (summary_text, ai_used: bool)
    """
    
    if not gemini_client:
        fallback = content.strip()[:max_chars] if content else title
        return fallback, False

    # ⚠️ చాలా చిన్న వార్త అయితే AI కాల్ వద్దు
    full_text = f"{title}\n{content}"
    if len(full_text) < 150:
        return content.strip(), False
        
    prompt = f"""
    ఈ క్రింది వార్తను పూర్తిగా చదివి, అందరికీ అర్థమయ్యేలా, 
    {max_chars} అక్షరాలలోపు తెలుగు షార్ట్ న్యూస్ గా మార్చు. 
    ఫైనల్ అవుట్‌పుట్ పూర్తిగా తెలుగులో మాత్రమే ఉండాలి.
    
    వార్త కంటెంట్:
    ---
    శీర్షిక: {title}
    వివరణ: {content}
    ---
    """

    try:
        response = gemini_client.generate_content(prompt)
        text = response.text.strip()
        return text[:max_chars], True

    except (APIError, Exception) as e:
        logger.error(f"Gemini API కాల్ లోపం: {e}")
        fallback = content.strip()[:max_chars] if content else title
        return fallback, False
