# summarize.py
# Simple bridge: delegates summarization to gemini_client (REST)
from gemini_client import summarize_text

def generate_summary(title, content, model=None, max_output_tokens=120):
    """
    wrapper used by other modules — returns string (may be empty on failure)
    """
    try:
        return summarize_text(title=title or "", content=content or "", model=model, max_output_tokens=max_output_tokens)
    except Exception as e:
        # Avoid raising — log will show in Render logs
        print("generate_summary failed:", str(e))
        return ""
