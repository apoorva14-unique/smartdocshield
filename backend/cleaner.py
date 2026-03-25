import re

def clean_text(text):

    # Fix OCR number-letter confusion
    text = text.replace("0", "O")
    text = text.replace("1", "I")

    # Fix common Aadhaar/PAN OCR errors
    text = re.sub(r'AP00RVA', 'APOORVA', text, flags=re.IGNORECASE)

    # Fix broken DOB formats
    text = re.sub(r'(\d{2})(\d{2})/(\d{4})', r'\1/\2/\3', text)

    # Remove junk symbols
    text = re.sub(r'[^A-Za-z0-9:/.\-\s]', ' ', text)

    # Normalize spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()