import os
import logging
from google import genai
from google.genai.errors import APIError 

# లాగింగ్ సెటప్
logger = logging.getLogger('summarize')
logger.setLevel(logging.INFO)

# ==============================================================================
# 1. Gemini API సెటప్
# ==============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
gemini_client = None

if not GEMINI_API_KEY:
    logger.warning("GEMINI_API_KEY లేదు. AI సారాంశం పనిచేయదు.")
else:
    try:
        # ✅ API కీతో క్లయింట్‌ను కాన్ఫిగర్ చేయండి
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_client = genai.GenerativeModel("gemini-2.5-flash") # మోడల్ నేరుగా
        logger.info("Gemini క్లయింట్ సెటప్ చేయబడింది.")
    except Exception as e:
        logger.error(f"Gemini క్లయింట్ ప్రారంభించడంలో లోపం: {e}")


# ==============================================================================
# 2. సారాంశం ఫంక్షన్ (fetch_rss.py ఉపయోగించే విధంగా)
# ==============================================================================

def summarize_news(title: str, content: str, max_chars: int = 500):
    """
    వార్తను తెలుగులో సారాంశం చేసి తిరిగి పంపుతుంది. 
    Returns (summary_text, ai_used: bool)
    """
    
    # ❌ API క్లయింట్ సెట్ చేయబడకపోతే, ఫాల్‌బ్యాక్
    if not gemini_client:
        # కంటెంట్ మొదటి భాగాన్ని ఫాల్‌బ్యాక్‌గా ఇస్తుంది
        fallback = content.strip()[:max_chars] if content else title
        return fallback, False

    # ⚠️ చాలా చిన్న వార్త అయితే AI కాల్ వద్దు
    full_text = f"{title}\n{content}"
    if len(full_text) < 150:
        return content.strip(), False
        
    prompt = f"""
    ఈ క్రింది న్యూస్ ని పూర్తిగా చదివి, అందరికీ అర్థమయ్యేలా, 
    {max_chars} అక్షరాలలోపు తెలుగు షార్ట్ న్యూస్ గా మార్చు. 
    ఫైనల్ అవుట్‌పుట్ పూర్తిగా తెలుగులో మాత్రమే ఉండాలి.
    
    వార్త కంటెంట్:
    ---
    శీర్షిక: {title}
    వివరణ: {content}
    ---
    """

    try:
        # ✅ API కాల్‌లో try/except
        response = gemini_client.generate_content(prompt)
        
        text = response.text.strip()
        return text[:max_chars], True

    except (APIError, Exception) as e:
        logger.error(f"Gemini API కాల్ లోపం: {e}")
        # లోపం వస్తే, కంటెంట్ మొదటి భాగాన్ని ఫాల్‌బ్యాక్‌గా ఇవ్వండి
        fallback = content.strip()[:max_chars] if content else title
        return fallback, False
