import re

def mask_pii(text, pii):

    # Aadhaar
    text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                  lambda x: "XXXX XXXX " + x.group(0)[-4:], text)

    # Phone
    text = re.sub(r'\b[6-9]\d{9}\b',
                  lambda x: "XXXXXX" + x.group(0)[-4:], text)

    # Email
    text = re.sub(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', "[EMAIL]", text)

    # DOB
    text = re.sub(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', "[DOB]", text)

    # 🔥 PAN masking (safe replace)
    for pan in pii.get("pan", []):
        text = re.sub(pan, "XXXXX" + pan[-5:], text, flags=re.IGNORECASE)

    return text