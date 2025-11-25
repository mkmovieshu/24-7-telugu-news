import re
from config import GOOGLE_API_KEY, FREE_MODE
import logging
try:
    import google.generativeai as genai
    genai.configure(api_key=GOOGLE_API_KEY)
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    logging.warning("Gemini SDK not available: %s", e)

# Helpers
def clean_text(html_or_text):
    text = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html_or_text)).strip()
    return text

# Decide if we should call AI (hybrid policy)
def needs_ai(full_text):
    # cheap rules: if very short, or looks like bullet list -> no AI
    if not full_text:
        return False
    tlen = len(full_text)
    # if under 220 chars -> do cheap truncation (no AI)
    if tlen < 220:
        return False
    # otherwise use AI for higher quality
    return True

# Prompt template (Telugu, strict length)
PROMPT = """
మీ పని: క్రింద ఇచ్చిన వార్తని 250–300 తెలుగు అక్షరాలలో స్పష్టంగా, న్యూట్రల్ టోన్‌లో, క్లియర్ పాయింట్లుగా రాయండి. టెక్స్ట్ clickbait లాంటిది కాకూడదు. వార్త శీర్షిక మరియు మూలో తర్వాత ఒక వాక్యం లో "Source:" లింక్ చూపించవద్దు — లింక్ API ఎలిమెంటుగా వేరుగా ఉండాలి.
Title: {title}

Content:
{content}

నీ సమాధానం కేవలం summary మాత్రమె — 250 నుంచి 300 అక్షరాలు మాత్రమే.
"""

def gemini_summarize(title, content, model="gemini-1.5-flash"):
    if FREE_MODE:
        # debug fallback: cheap truncate
        txt = (title + " " + (content or ""))[:300]
        return txt
    if not GEMINI_AVAILABLE:
        # graceful fallback
        txt = (title + " " + (content or ""))[:300]
        return txt

    cleaned = clean_text(content or "")
    prompt = PROMPT.format(title=title, content=cleaned[:3000])  # limit input
    try:
        # Use generate_text; docs show generate endpoints — this is conservative example
        resp = genai.generate_text(model=model, input=prompt, max_output_tokens=200)
        out = resp.text if hasattr(resp, "text") else str(resp)
        out = out.strip()
        # ensure size
        if len(out) > 330:
            out = out[:330].rsplit(" ",1)[0] + "…"
        return out
    except Exception as e:
        logging.exception("Gemini call failed: %s", e)
        # fallback truncate
        txt = (title + " " + cleaned)[:300]
        return txt
