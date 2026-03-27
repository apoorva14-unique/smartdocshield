import re

def mask_pii(text, pii):

    text = text.replace("O", "0").replace("I", "1")

    # Aadhaar
    text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                  lambda x: "XXXX XXXX " + x.group(0)[-4:], text)

    # PAN
    text = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',
                  lambda x: "XXXXX" + x.group(0)[-5:], text)

    # Card
    text = re.sub(r'\b\d{13,16}\b',
                  lambda x: "XXXX XXXX XXXX " + x.group(0)[-4:], text)

    return text