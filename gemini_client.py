import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

def gemini_summarize(text):
    prompt = (
        "ఈ క్రింది న్యూస్ ని పూర్తిగా చదివి, "
        "అందరికీ అర్థమయ్యేలా, 500 అక్షరాలలోపు "
        "తెలుగు షార్ట్ న్యూస్ గా మార్చు. "
        "ఫైనల్ అవుట్‌పుట్ పూర్తిగా తెలుగులో మాత్రమే ఉండాలి.\n\n"
        + text
    )

    response = model.generate_content(prompt)
    return response.text.strip()
