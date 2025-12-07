# summarize.py (సరిచేసిన కోడ్)
import os
from groq_client import groq_summarize

def summarize_item(doc):
    # doc may contain 'raw_summary' or 'title' + 'published' etc.
    text = doc.get("raw_summary") or doc.get("title") or ""
    
    # === ✅ తెలుగు స్థిరత్వం కోసం సరిచేసిన ప్రాంప్ట్ ===
    # AI కి తెలుగులో మాత్రమే సారాంశం ఇవ్వమని స్పష్టంగా చెబుతోంది.
    prompt_text = "తెలుగు భాషలో మాత్రమే సారాంశం ఇవ్వండి. మాతృక: " + text
    
    # try AI summarizer if credentials set
    try:
        api_key = os.getenv("GROQ_API_KEY")
        endpoint = os.getenv("GROQ_ENDPOINT")
        if api_key and endpoint:
            # *** ఇక్కడ 'text' కు బదులుగా 'prompt_text' ని వాడాలి ***
            out = groq_summarize(prompt_text, max_tokens=300) 
            if out:
                return out
    except Exception:
        pass
        
    # fallback simple trim
    s = text.strip()
    if len(s) <= 400:
        return s
    return s[:400].rsplit(" ",1)[0] + "..."
    
