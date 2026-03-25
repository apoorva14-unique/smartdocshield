import re

def normalize_text(text):
    text = text.upper()
    text = text.replace("0", "O").replace("1", "I")
    return text

def detect_pii(text):

    pii = {}
    text_upper = normalize_text(text)

    # Aadhaar
    pii["aadhaar"] = list(set(re.findall(r'\b\d{4}\s?\d{4}\s?\d{4}\b', text)))

    # Phone
    pii["phone"] = list(set(re.findall(r'\b[6-9]\d{9}\b', text)))

    # Email
    pii["email"] = list(set(re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)))

    # DOB
    pii["dob"] = list(set(re.findall(r'\b\d{2}[/-]\d{2}[/-]\d{4}\b', text)))

    # 🔥 STRONG PAN DETECTION (OCR tolerant)
    possible_words = re.findall(r'\b[A-Z0-9]{8,12}\b', text_upper)

    pan_list = []

    for word in possible_words:
        if len(word) == 10:
            letters = sum(c.isalpha() for c in word)
            digits = sum(c.isdigit() for c in word)

            if letters >= 5 and digits >= 3:
                pan_list.append(word)

    pii["pan"] = list(set(pan_list))

    return pii