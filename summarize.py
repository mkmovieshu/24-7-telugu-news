# summarize.py
import os
from groq_client import groq_summarize

def summarize_item(doc):
    # doc may contain 'raw_summary' or 'title' + 'published' etc.
    text = doc.get("raw_summary") or doc.get("title") or ""
    
    # === ✅ అత్యంత సమర్థవంతమైన కొత్త ప్రాంప్ట్ ===
    # ఈ ప్రాంప్ట్ Groq AI కి ఇన్‌పుట్ ఏ భాషలో ఉన్నా, చివరకు తెలుగులో మాత్రమే అవుట్‌పుట్ ఇవ్వాలని ఆదేశిస్తుంది.
    prompt_text = (
        "దయచేసి ఈ క్రింది ఆర్టికల్ నీ మొత్తం చదివి అందరికీ అర్థమయ్యే విధంగా, ఆ న్యూస్ మొత్తాన్ని ఒక 500 అక్షరాలతో తెలుగు షార్ట్ న్యూస్ లాగా మార్చు. "
        "ఇన్‌పుట్ ఇంగ్లీష్‌లో ఉంటే, దానిని తెలుగులోకి మార్చి, 500 అక్షరాల తెలుగు షార్ట్ న్యూస్ గా కన్వర్ట్ చేయాలి. "
        "ఫైనల్ అవుట్‌పుట్ పూర్తిగా తెలుగులో (Telugu) మాత్రమే ఉండాలి."
    ) + text
    
    # try AI summarizer if credentials set
    try:
        api_key = os.getenv("GROQ_API_KEY")
        endpoint = os.getenv("GROQ_ENDPOINT")
        if api_key and endpoint:
            # 'prompt_text' ద్వారా Groq AI ని పిలవడం
            out = groq_summarize(prompt_text, max_tokens=300) 
            if out:
                return out
    except Exception:
        pass
        
    # fallback simple trim (AI విఫలమైతే మాత్రమే)
    s = text.strip()
    if len(s) <= 400:
        return s
    return s[:400].rsplit(" ",1)[0] + "..."
    
