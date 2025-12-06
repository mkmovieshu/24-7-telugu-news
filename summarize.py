# summarize.py
import os
from groq_client import groq_summarize

def summarize_item(doc):
    # doc may contain 'raw_summary' or 'title' + 'published' etc.
    text = doc.get("raw_summary") or doc.get("title") or ""
    
    # === ఇక్కడ మార్పు చేయబడింది: AI ప్రాంప్ట్‌కి తెలుగు సూచనను జోడించడం ===
    prompt_text = "తెలుగు భాషలో మాత్రమే సారాంశం ఇవ్వండి. మాతృక: " + text
    
    # try AI summarizer if credentials set
    try:
        api_key = os.getenv("GROQ_API_KEY")
        endpoint = os.getenv("GROQ_ENDPOINT")
        if api_key and endpoint:
            # *** ఇప్పుడు prompt_text (తెలుగు సూచనతో) ను వాడుతున్నాం ***
            out = groq_summarize(prompt_text, max_tokens=500) 
            if out:
                return out
    except Exception:
        pass
    # fallback simple trim
    s = text.strip()
    if len(s) <= 400:
        return s
    return s[:400].rsplit(" ",1)[0] + "..."
