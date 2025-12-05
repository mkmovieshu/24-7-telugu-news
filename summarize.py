# summarize.py
import os
import logging
from groq_client import groq_summarize

logger = logging.getLogger("short-news-api")

def summarize_item(doc: dict) -> str:
    """న్యూస్ ఐటెమ్‌కు సమ్మరీ జనరేట్ చేయడం"""
    
    # సమ్మరీ కోసం టెక్స్ట్ తీసుకోవడం
    text = doc.get("raw_summary") or doc.get("title") or ""
    
    if not text.strip():
        return "వివరాలు అందుబాటులో లేవు"
    
    # తెలుగు భాషా డిటెక్షన్ (సింపుల్)
    def is_telugu_text(txt):
        telugu_range = range(0x0C00, 0x0C7F)
        telugu_chars = sum(1 for char in txt if ord(char) in telugu_range)
        return telugu_chars > len(txt) * 0.3  # 30% కంటే ఎక్కువ తెలుగు అక్షరాలు
    
    # AI సమ్మరీ ప్రయత్నం
    try:
        api_key = os.getenv("GROQ_API_KEY")
        
        if api_key and len(text.strip()) > 100:
            # GROQ AI సమ్మరీ
            summary = groq_summarize(text, max_tokens=350)
            
            if summary and len(summary) > 50:
                # నాణ్యత తనిఖీ
                if len(summary.split()) >= 15:  # కనీసం 15 పదాలు
                    logger.info(f"AI summary generated: {len(summary)} chars")
                    return summary
        
        # ఫాల్‌బ్యాక్: సింపుల్ ట్రంకేషన్
        cleaned_text = text.strip()
        
        # HTML ట్యాగ్‌లను తొలగించడం
        import re
        cleaned_text = re.sub(r'<[^>]+>', '', cleaned_text)
        
        # అదనపు స్పేస్‌లను తొలగించడం
        cleaned_text = ' '.join(cleaned_text.split())
        
        # ఫలితం తెలుగు లేదా ఇంగ్లీషులో ఉండాలి
        if not is_telugu_text(cleaned_text):
            # ఇంగ్లీష్ టెక్స్ట్‌ని సంగ్రహం చేయడం
            if len(cleaned_text) > 400:
                # వాక్యాల వద్ద కట్ చేయడం
                sentences = cleaned_text.split('. ')
                result = []
                total_length = 0
                
                for sentence in sentences:
                    if total_length + len(sentence) < 350:
                        result.append(sentence)
                        total_length += len(sentence)
                    else:
                        break
                
                summary_text = '. '.join(result)
                if summary_text and not summary_text.endswith('.'):
                    summary_text += '.'
                    
                if len(summary_text) > 50:
                    return summary_text
        
        # చివరి ఫాల్‌బ్యాక్
        if len(cleaned_text) > 400:
            return cleaned_text[:397] + "..."
        else:
            return cleaned_text
            
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        # అత్యవసర ఫాల్‌బ్యాక్
        fallback = text[:300].strip()
        if len(fallback) < len(text):
            return fallback + "..."
        return fallback

def summarize_batch(docs: list) -> list:
    """బల్క్ లో అనేక డాక్యుమెంట్స్‌ను సమ్మరైజ్ చేయడం"""
    results = []
    
    for doc in docs:
        try:
            doc["summary"] = summarize_item(doc)
            results.append(doc)
        except Exception as e:
            logger.error(f"Error summarizing doc: {e}")
            # డిఫాల్ట్ సమ్మరీ
            text = doc.get("raw_summary", "") or doc.get("title", "")
            if len(text) > 400:
                doc["summary"] = text[:397] + "..."
            else:
                doc["summary"] = text
            results.append(doc)
    
    return results
