import os
import json
import logging
import requests

logger = logging.getLogger("short-news-api")

GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash-lite")


def _trim_summary_chars(text: str, max_chars: int = 320, min_chars: int = 220) -> str:
    """
    Telugu short-news కోసం length కట్టే helper.
    - Target: 250–320 characters
    - Sentence మధ్యలో కట్ కాకుండా చూసుకుంటుంది.
    """
    if not text:
        return ""

    s = text.strip()

    # Already within limit
    if len(s) <= max_chars:
        return s

    truncated = s[:max_chars]

    # Try to cut at last sentence boundary within truncated
    sentence_separators = ["।", "!", "?", ".", "…"]
    for sep in sentence_separators:
        idx = truncated.rfind(sep)
        if idx != -1 and idx >= min_chars // 2:
            return truncated[: idx + 1].strip()

    # Else, cut at last space
    last_space = truncated.rfind(" ")
    if last_space != -1 and last_space >= min_chars // 2:
        return (truncated[:last_space].rstrip() + "…").strip()

    # Worst case: just cut and add ellipsis
    return (truncated.rstrip() + "…").strip()


def summarize_text(
    title: str,
    content: str,
    model: str = None,
    max_output_tokens: int = 120,
) -> str:
    """
    Call Gemini 2.x via REST using generateContent.
    Returns a Telugu short-news summary ~250–320 characters.
    """
    if not GOOGLE_KEY:
        raise RuntimeError("GOOGLE_API_KEY not set in environment")

    model = model or DEFAULT_MODEL

    # Example: models/gemini-2.0-flash-lite:generateContent
    url = f"https://generativelanguage.googleapis.com/v1/{model}:generateContent?key={GOOGLE_KEY}"

    # 🔥 కొత్త killer prompt – exactly ఇందే నీ short-news యాప్ కోసం
    system_prompt = (
        "You are a Telugu news summarizer. "
        "Generate a crisp, factual, complete short-news summary in Telugu.\n\n"
        "RULES:\n"
        "1. Length must be 250–320 characters ONLY.\n"
        "2. Summary must end with a complete sentence. Never cut mid-word.\n"
        "3. Use only the facts given in the text. DO NOT imagine or create missing details.\n"
        "4. Include these elements clearly:\n"
        "   – What happened (main point)\n"
        "   – Where happened (place)\n"
        "   – When (if available)\n"
        "   – A key highlight or consequence.\n"
        "5. Avoid repetition. Avoid generic filler lines.\n"
        "6. Write in clean Telugu newsroom style.\n\n"
        "Your output must contain ONLY the final summary text. No headings, no explanation.\n\n"
    )

    prompt_text = (
        system_prompt
        + f"TITLE: {title}\n\n"
        + "CONTENT:\n"
        + (content or "")
    )

    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.25,
            "maxOutputTokens": max_output_tokens,
        },
    }

    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, headers=headers, json=body, timeout=25)
    logger.info("Gemini status: %s", resp.status_code)
    resp.raise_for_status()

    j = resp.json()

    # Debug: raw response snippet log
    try:
        logger.info("Gemini raw response (trimmed): %s", str(j)[:400])
    except Exception:
        pass

    summary = ""

    # ---- Typical Gemini 2.x structure ----
    try:
        candidates = j.get("candidates") or []
        if candidates:
            first = candidates[0]
            content_obj = first.get("content") or {}
            parts = content_obj.get("parts") or []
            texts = []
            for part in parts:
                if isinstance(part, dict) and "text" in part:
                    texts.append(part["text"])
            summary = " ".join(texts).strip()
    except Exception as e:
        logger.exception("Gemini parse failed: %s", str(e))

    # ---- Fallbacks (విడిచిపెట్టకుండా గ్యారెంటీ కోసం) ----
    if not summary and isinstance(j, dict):
        # Some variants might return 'output_text' or 'output'
        candidate = j.get("candidates") or None
        if candidate and isinstance(candidate, list):
            maybe = candidate[0]
            if isinstance(maybe, dict):
                text_val = maybe.get("output_text") or maybe.get("output")
                if isinstance(text_val, str):
                    summary = text_val.strip()

        if not summary:
            tmp = j.get("output_text") or j.get("output") or ""
            if isinstance(tmp, dict):
                tmp = json.dumps(tmp)
            if isinstance(tmp, str):
                summary = tmp.strip()

    summary = (summary or "").strip()

    # Length control – 250–320 chars target
    before_len = len(summary)
    summary = _trim_summary_chars(summary, max_chars=320, min_chars=220)
    after_len = len(summary)

    logger.info(
        "Gemini summary lengths: raw=%d, trimmed=%d",
        before_len,
        after_len,
    )

    if not summary:
        logger.warning("Gemini returned empty summary after trim for title: %s", title)

    return summary
