def classify_document(text):
    t = text.upper()

    if "AADHAAR" in t:
        return "Aadhaar Card"
    elif "INCOME TAX" in t or "PERMANENT ACCOUNT NUMBER" in t:
        return "PAN Card"
    else:
        return "Unknown Document"


def ocr_quality_score(text):
    words = text.split()
    if len(words) == 0:
        return 0

    valid = sum(1 for w in words if w.isalpha())
    return int((valid / len(words)) * 100)