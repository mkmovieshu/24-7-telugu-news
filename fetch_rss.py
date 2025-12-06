# summarize.py - తుది కోడ్
# fetch_rss.py - ఫీడ్స్ లోడ్ చేయడానికి సరిదిద్దబడిన కోడ్
import os
import feedparser
from datetime import datetime
from urllib.parse import urlparse
from db import news_collection
from summarize import summarize_item
from bson.objectid import ObjectId

# ✅ FIX: ENVIRONMENT VARIABLE నుండి ఫీడ్‌లను లోడ్ చేయండి
RSS_FEEDS_ENV = os.getenv("RSS_FEEDS")

# RSS_FEEDS_ENV లో సెట్ చేస్తే, కామాలతో వేరు చేసిన వాటిని లిస్ట్ గా మారుస్తుంది.
if RSS_FEEDS_ENV:
    FEEDS = [f.strip() for f in RSS_FEEDS_ENV.split(',') if f.strip()]
else:
    # Environment variable సెట్ చేయకపోతే, పాత డిఫాల్ట్ ను వాడుతుంది.
    # ఈ డిఫాల్ట్ ను తొలగించడం ద్వారా, FEEDS ఖాళీగా ఉండదు.
    FEEDS = [
        "https://www.hindustantimes.com/feeds/rss/entertainment/telugu-cinema/rssfeed.xml",
        "https://telugu.oneindia.com/rss/feeds/oneindia-telugu-fb.xml",
        "https://www.teluguone.com/news/tonefeeds/latestnews/latestnews-25.rss"
    ]

# ... మిగిలిన కోడ్ అంతా పాతదే...

import os
from groq_client import groq_summarize 

def summarize_item(doc):
    text = doc.get("raw_summary") or doc.get("title") or ""
    if not text:
        return ""

    # User Prompt: సారాంశం యొక్క లక్ష్యాన్ని సెట్ చేస్తుంది.
    instruction = (
        "Summarize the following text into a short news snippet. "
        "The summary should be concise, be between 300 to 500 characters, "
        "and must be based *only* on the provided text. Do not include any title, greeting, or introductory phrase."
    )
    full_prompt = f"{instruction}\n\nTEXT TO SUMMARIZE:\n{text}"

    # try AI summarizer if credentials set
    try:
        api_key = os.getenv("GROQ_API_KEY")
        endpoint = os.getenv("GROQ_ENDPOINT")
        
        if api_key and endpoint:
            out = groq_summarize(full_prompt, max_tokens=500)
            
            if out:
                s = out.strip()
                # తుది అక్షరాల పరిమితి (500) కోసం తనిఖీ
                if len(s) > 500:
                    return s[:500].rsplit(" ", 1)[0] + "..."
                return s
        else:
            print("Warning: GROQ_API_KEY or GROQ_ENDPOINT not set. Falling back to simple trim.")
            
    except Exception as e:
        print(f"Error during Groq summarization: {e}. Falling back to simple trim.")
        pass 

    # fallback simple trim (if AI fails or credentials missing)
    s = text.strip()
    
    if len(s) <= 500: 
        return s
    
    return s[:500].rsplit(" ",1)[0] + "..."
    
