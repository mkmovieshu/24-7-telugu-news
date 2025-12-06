# groq_client.py - ఫైనల్ సరిచేసిన కోడ్
import os
import httpx

GROQ_ENDPOINT = os.getenv("GROQ_ENDPOINT")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def groq_summarize(text, max_tokens=500):
    if not GROQ_ENDPOINT or not GROQ_API_KEY:
        return None
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        
        # FIXED: స్టాండర్డ్ Groq/OpenAI Chat Completions ఫార్మాట్‌ను ఉపయోగించండి
        payload = {
            # మీ మోడల్ పేరును ఇక్కడ ఖచ్చితంగా సెట్ చేయండి (ఉదా: llama3-8b-8192, gpt-4o-mini)
            "model": "gpt-4o-mini", 
            
            # CRITICAL FIX: 'input' బదులు 'messages' వాడుతున్నాం. 
            # 'text' argument (summarize.py నుండి వచ్చేది) లోనే తెలుగు ఆదేశం ఉంటుంది.
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ],
            
            # సారాంశం 500 అక్షరాల వరకు రావాలి కాబట్టి, max_tokens ను 500 గా ఉంచుదాం.
            "max_tokens": max_tokens
        }
        
        with httpx.Client(timeout=30) as client:
            r = client.post(GROQ_ENDPOINT, headers=headers, json=payload)
            r.raise_for_status() # API నుండి వచ్చిన 4xx/5xx లోపాలను ఇక్కడ పట్టుకుంటుంది
            
            data = r.json()
            
            # FIXED: స్టాండర్డ్ API రెస్పాన్స్ నుండి 'content' ను పార్స్ చేయండి
            if data.get("choices") and data["choices"][0].get("message"):
                return data["choices"][0]["message"].get("content", "").strip()
            
    except httpx.HTTPStatusError as e:
        print(f"groq HTTP error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        print("groq general error", e)
        
    return None
    
