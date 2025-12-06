# summarize.py - Indentation Fixed + Telugu Prompt
import os
from groq_client import groq_summarize 

def summarize_item(doc):
    text = doc.get("raw_summary") or doc.get("title") or ""
    if not text:
        return ""

    # Groq APIకి పంపే స్పష్టమైన తెలుగు ఆదేశం
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
            # full_prompt ను groq_summarize కు పంపుతుంది
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
        # ✅ ఇక్కడ ఇండెంటేషన్ సరిగా ఉండాలి (def కింది అన్ని లైన్లు 4 స్పేస్‌లతో మొదలవ్వాలి)
        print(f"Error during Groq summarization: {e}. Falling back to simple trim.")
        pass 

    # fallback simple trim (if AI fails or credentials missing)
    s = text.strip()
    
    if len(s) <= 500: 
        return s
    
    return s[:500].rsplit(" ",1)[0] + "..."
    
