# gemini_client.py
import os
import requests
import json

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")

def summarize_text(title: str, content: str, model: str = None, max_output_tokens: int = 120) -> str:
    model = model or DEFAULT_MODEL
    if not GOOGLE_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set in environment")

    url = f"https://generativelanguage.googleapis.com/v1/{model}:generate?key={GOOGLE_KEY}"

    prompt_text = (
        f"Summarize the following Telugu article in 250-300 Telugu characters, neutral tone, no clickbait.\n\n"
        f"TITLE: {title}\n\nCONTENT:\n{content}"
    )

    payload = {
      "prompt": {"text": prompt_text},
      "temperature": 0.2,
      "maxOutputTokens": max_output_tokens
    }

    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    resp.raise_for_status()
    j = resp.json()

    # robust extraction for different shapes
    summary = ""
    candidates = j.get("candidates") or j.get("outputs") or []
    if candidates and isinstance(candidates, list):
        first = candidates[0]
        if isinstance(first, dict):
            summary = first.get("output") or first.get("content") or first.get("text") or ""
            if not summary:
                for v in first.values():
                    if isinstance(v, str) and v.strip():
                        summary = v
                        break

    if not summary:
        summary = j.get("output_text") or j.get("output") or ""
        if isinstance(summary, dict):
            summary = json.dumps(summary)

    return (summary or "").strip()
