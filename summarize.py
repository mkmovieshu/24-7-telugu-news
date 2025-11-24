from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def summarize_text(title, content):
    prompt = f"""
    క్రింద ఇచ్చిన వార్తను 250–300 తెలుగు అక్షరాలలో సూపర్ క్లియర్‌గా, పాయింట్‌కు వచ్చేలా 
    షార్ట్ న్యూస్‌గా రాయండి. Clickbait వద్దు. రాజకీయ బయ్యాస్ లేకూడదు.
    
    శీర్షిక: {title}

    కంటెంట్:
    {content}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=120
        )
        return response.choices[0].message["content"].strip()

    except Exception:
        # fallback to GPT-4o
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=130
        )
        return response.choices[0].message["content"].strip()
