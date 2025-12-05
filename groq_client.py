# groq_client.py
import os
import httpx

GROQ_ENDPOINT = os.getenv("GROQ_ENDPOINT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_summarize(text, max_tokens=300):
    if not GROQ_ENDPOINT or not GROQ_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",  # or your model
            "input": f"Summarize the following news into 300-400 characters in Telugu: {text}",
            "max_tokens": max_tokens
        }
        with httpx.Client(timeout=30) as client:
            r = client.post(GROQ_ENDPOINT, headers=headers, json=payload)
            if r.status_code == 200:
                data = r.json()
                # adapt to your provider's response shape
                return data.get("summary") or data.get("text") or data.get("output", "")
    except Exception as e:
        print("groq error", e)
    return None
