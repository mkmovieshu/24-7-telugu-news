# groq_client.py
import os
import httpx

GROQ_ENDPOINT = os.getenv("GROQ_ENDPOINT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_summarize(text, max_tokens=500):
    if not GROQ_ENDPOINT or not GROQ_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        payload = {
            "model": "mixtral-8x7b-32768", # తెలుగుకు మెరుగైన మోడల్
            
            "messages": [
                # ✅ System Prompt: తెలుగులో మాత్రమే మరియు 300-500 అక్షరాల పరిమితి
                {
                    "role": "system",
                    "content": "You are a professional Telugu news summarizer. You MUST translate and summarize the text **EXCLUSIVELY in Telugu (తెలుగు)**. Do not output any English words, letters, or numbers (transliterate numbers into Telugu words if needed). If any part cannot be translated, you must still provide the most appropriate Telugu equivalent. Maintain a concise 300-500 character length."
                },
                # User Prompt (summarize.py నుండి వస్తుంది)
                {
                    "role": "user",
                    "content": text
                }
            ],
            
            "max_tokens": max_tokens
        }
        
        with httpx.Client(timeout=30) as client:
            r = client.post(GROQ_ENDPOINT, headers=headers, json=payload)
            r.raise_for_status()
            
            data = r.json()
            
            if data.get("choices") and data["choices"][0].get("message"):
                return data["choices"][0]["message"].get("content", "").strip()
            
    except httpx.HTTPStatusError as e:
        print(f"groq HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print("groq general error", e)
        
    return None
    
