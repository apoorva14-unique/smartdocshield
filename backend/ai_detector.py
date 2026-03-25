import spacy

nlp = spacy.load("en_core_web_sm")

def detect_ai_entities(text):

    doc = nlp(text)

    names = []
    locations = []

    for ent in doc.ents:
        val = ent.text.strip()

        # remove garbage OCR words
        if len(val) < 4 or any(char.isdigit() for char in val):
            continue

        if ent.label_ == "PERSON":
            names.append(val)

        elif ent.label_ in ["GPE", "LOC"]:
            locations.append(val)

    return {
        "names": list(set(names))[:5],
        "locations": list(set(locations))[:5]
    }