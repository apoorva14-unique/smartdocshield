import spacy
import re

nlp = spacy.load("en_core_web_sm")

STOPWORDS = ["GOVERNMENT", "INDIA", "UNIQUE", "AUTHORITY"]

def detect_ai_entities(text):

    doc = nlp(text)

    names = []

    for ent in doc.ents:
        val = ent.text.strip()

        if ent.label_ == "PERSON" and len(val) > 3:
            names.append(val)

    # 🔥 BETTER FALLBACK
    if not names:
        possible = re.findall(r'[A-Z]{3,}\s[A-Z]{3,}', text.upper())

        filtered = []
        for n in possible:
            if not any(word in n for word in STOPWORDS):
                filtered.append(n)

        names = filtered[:3]

    return {"names": list(set(names))}