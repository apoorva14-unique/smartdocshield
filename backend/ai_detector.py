import spacy
import re

try:
    nlp = spacy.load("en_core_web_sm")
except:
    nlp = None

STOPWORDS = ["GOVERNMENT", "INDIA", "UNIQUE", "AUTHORITY"]

def detect_ai_entities(text):

    names = []

    if nlp:
        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                names.append(ent.text)

    return {
        "names": list(set(names))[:3]
    }

    # 🔥 BETTER FALLBACK
    if not names:
        possible = re.findall(r'[A-Z]{3,}\s[A-Z]{3,}', text.upper())

        filtered = []
        for n in possible:
            if not any(word in n for word in STOPWORDS):
                filtered.append(n)

        names = filtered[:3]

    return {"names": list(set(names))}