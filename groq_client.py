# groq_client.py
import os
import httpx
import logging
from typing import Optional

logger = logging.getLogger("short-news-api")

GROQ_ENDPOINT = os.getenv("GROQ_ENDPOINT", "https://api.groq.com/openai/v1/chat/completions")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_summarize(text: str, max_tokens: int = 350) -> Optional[str]:
    """GROQ AI ద్వారా తెలుగులో సమ్మరీ జనరేట్ చేయడం"""
    
    if not GROQ_API_KEY:
        logger.warning("GROQ_API_KEY not configured")
        return None
    
    if not text or len(text.strip()) < 20:
        logger.warning("Text too short for summarization")
        return text[:300] if text else ""
    
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # తెలుగులో సమ్మరీ కోసం ప్రామ్ప్ట్
        prompt = f"""కింది వార్తను 300-400 అక్షరాలలో తెలుగులో సంగ్రహంగా రాయండి:
        
        {text[:2000]}
        
        సూచనలు:
        1. ముఖ్యమైన వివరాలు మాత్రమే చేర్చండి
        2. సరళమైన తెలుగు భాషలో రాయండి
        3. వాస్తవాలపై దృష్టి పెట్టండి
        4. అభిప్రాయాలు చేర్చకండి"""
        
        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "మీరు తెలుగు వార్తా సంగ్రహకారుడు. వార్తలను సంగ్రహంగా, స్పష్టంగా తెలుగులో రాయండి."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
            "top_p": 0.9
        }
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(GROQ_ENDPOINT, headers=headers, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                summary = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                
                if summary and len(summary) > 50:
                    logger.info(f"Generated summary: {len(summary)} characters")
                    return summary
                else:
                    logger.warning("Empty or very short summary received")
                    return text[:350]
            else:
                logger.error(f"GROQ API error: {response.status_code} - {response.text[:200]}")
                return text[:350]
                
    except httpx.TimeoutException:
        logger.error("GROQ API timeout")
        return text[:350]
    except Exception as e:
        logger.error(f"GROQ summarization error: {e}")
        return text[:350]

def batch_summarize(news_items: list) -> list:
    """బల్క్ లో సమ్మరీస్ జనరేట్ చేయడం"""
    if not GROQ_API_KEY:
        return news_items
    
    summarized_items = []
    
    for item in news_items:
        try:
            text_to_summarize = item.get("raw_summary") or item.get("title", "")
            
            if text_to_summarize:
                summary = groq_summarize(text_to_summarize)
                if summary and summary != text_to_summarize[:350]:
                    item["summary"] = summary
                else:
                    # ఫాల్‌బ్యాక్ సింపుల్ సమ్మరీ
                    text = text_to_summarize
                    if len(text) > 400:
                        item["summary"] = text[:397] + "..."
                    else:
                        item["summary"] = text
            else:
                item["summary"] = item.get("title", "")
                
        except Exception as e:
            logger.error(f"Error summarizing item {item.get('title', 'unknown')}: {e}")
            # ఫాల్‌బ్యాక్
            text = item.get("raw_summary", "") or item.get("title", "")
            if len(text) > 400:
                item["summary"] = text[:397] + "..."
            else:
                item["summary"] = text
        
        summarized_items.append(item)
    
    return summarized_items
