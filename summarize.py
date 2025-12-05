# summarize.py
import os
from groq_client import groq_summarize

def summarize_item(doc):
    # doc may contain 'raw_summary' or 'title' + 'published' etc.
    text = doc.get("raw_summary") or doc.get("title") or ""
    # try AI summarizer if credentials set
    try:
        api_key = os.getenv("GROQ_API_KEY")
        endpoint = os.getenv("GROQ_ENDPOINT")
        if api_key and endpoint:
            out = groq_summarize(text, max_tokens=300)
            if out:
                return out
    except Exception:
        pass
    # fallback simple trim
    s = text.strip()
    if len(s) <= 400:
        return s
    return s[:400].rsplit(" ",1)[0] + "..."
