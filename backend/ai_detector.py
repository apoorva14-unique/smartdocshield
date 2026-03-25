import spacy

try:
    nlp = spacy.load("en_core_web_sm")
except:
    print("⚠️ spaCy model not found, using blank model")
    nlp = spacy.blank("en")


def detect_ai_entities(text):
    doc = nlp(text)

    names = []
    locations = []

    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ in ["GPE", "LOC"]:
            locations.append(ent.text)

    return {
        "names": list(set(names)),
        "locations": list(set(locations))
    }