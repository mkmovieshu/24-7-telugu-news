from gemini_client import gemini_summarize

def summarize_item(doc):
    text = doc.get("raw_summary") or doc.get("title") or ""

    try:
        out = gemini_summarize(text)
        if out:
            return out
    except Exception as e:
        print("Gemini error:", e)

    # fallback
    return text[:400]
