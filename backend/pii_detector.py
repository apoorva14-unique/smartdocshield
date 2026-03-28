import re

def normalize_text(text):
    text = text.upper()
    text = text.replace("O", "0")
    text = text.replace("I", "1")
    return text

def detect_pii(text):

    clean = normalize_text(text)

    pii = {}

    # ---------------- AADHAAR (STRONG FIX) ----------------
    # ---------------- AADHAAR (IMPROVED) ----------------
    aadhaar_matches = []

# 12 digit continuous
    aadhaar_matches += re.findall(r'\b\d{12}\b', clean)

# spaced format
    aadhaar_matches += re.findall(r'\b\d{4}\s\d{4}\s\d{4}\b', clean)

    aadhaar_formatted = []
    for a in aadhaar_matches:
        a = re.sub(r'\s', '', a)
        if len(a) == 12:
            aadhaar_formatted.append(a[:4]+" "+a[4:8]+" "+a[8:])

# 🔥 SMART VALIDATION
    if aadhaar_formatted:
        pii["aadhaar"] = list(set(aadhaar_formatted))
    else:
        pii["aadhaar"] = []

    # If Aadhaar found → ignore PAN false positives
    if pii["aadhaar"]:
        pii["pan"] = []

    # ---------------- PAN ----------------
    pii["pan"] = list(set(re.findall(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', clean)))

    # ---------------- PHONE ----------------
    pii["phone"] = list(set(re.findall(r'\b[6-9]\d{9}\b', clean)))

    # ---------------- EMAIL ----------------
    pii["email"] = list(set(re.findall(
        r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}', text)))

    # ---------------- DOB ----------------
    pii["dob"] = list(set(re.findall(r'\b\d{2}/\d{2}/\d{4}\b', clean)))

    # ---------------- CARD ----------------
    card_matches = re.findall(r'\b(?:\d{4}\s?){4}\b', clean)
    cards = [re.sub(r'\s', '', c) for c in card_matches]

    # ❗ Remove Aadhaar from card
    cards = [
        c for c in cards
        if c not in [a.replace(" ", "") for a in pii["aadhaar"]]
    ]

    # ❗ Remove DOB-like numbers (e.g., 15081988)
    cards = [c for c in cards if not re.match(r'^\d{8}$', c)]

    pii["card"] = list(set(cards))

    # ---------------- PARTIAL CARD (FALLBACK) ----------------
    partial_cards = re.findall(r'\b\d{4}\b', clean)

    if not pii["card"] and partial_cards:
        pii["card"] = ["**** **** **** " + partial_cards[-1]]

    # ---------------- BANK ----------------
    pii["bank"] = list(set(re.findall(r'\b\d{10,18}\b', clean)))

    # ❗ Remove Aadhaar & card from bank
    pii["bank"] = [
        x for x in pii["bank"]
        if x not in [a.replace(" ", "") for a in pii["aadhaar"]]
        and x not in pii["card"]
    ]

    # ---------------- IFSC ----------------
    pii["ifsc"] = list(set(re.findall(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', clean)))

    return pii