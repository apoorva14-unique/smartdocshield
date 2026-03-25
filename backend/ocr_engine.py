import pytesseract
from PIL import Image
import PyPDF2
import docx
import re
from pdf2image import convert_from_path
import os

# ---------------- ENV DETECTION ----------------
IS_RENDER = os.environ.get("RENDER", False)

# ---------------- TESSERACT CONFIG ----------------
if not IS_RENDER:
    # LOCAL WINDOWS PATH
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------------- TEXT CLEANING ----------------
def clean_text(text):
    text = text.upper()

    # Fix common OCR mistakes
    text = text.replace("O", "0")
    text = text.replace("I", "1")

    text = re.sub(r'[^A-Z0-9\s:/.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()

# ---------------- MAIN OCR FUNCTION ----------------
def extract_text(filepath):

    text = ""

    try:
        ext = filepath.lower()

        # ---------------- IMAGE ----------------
        if ext.endswith((".jpg", ".png", ".jpeg")):
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)

        # ---------------- PDF ----------------
        elif ext.endswith(".pdf"):

            # STEP 1: Try direct text extraction
            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        if page.extract_text():
                            text += page.extract_text()
            except Exception as e:
                print("PDF READ ERROR:", e)

            # STEP 2: If no text → OCR fallback
            if not text.strip():
                try:
                    if IS_RENDER:
                        # 🚀 Render (no poppler path needed)
                        images = convert_from_path(filepath)
                    else:
                        # 💻 Local (with poppler)
                        images = convert_from_path(
                            filepath,
                            poppler_path=r"C:\Users\Lenovo\Downloads\Release-25.12.0-0 (2)\poppler-25.12.0\Library\bin"
                        )

                    for img in images:
                        text += pytesseract.image_to_string(img)

                except Exception as e:
                    print("PDF OCR ERROR:", e)

        # ---------------- DOCX ----------------
        elif ext.endswith(".docx"):
            try:
                doc = docx.Document(filepath)

                for para in doc.paragraphs:
                    text += para.text + "\n"

                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            text += cell.text + " "

            except Exception as e:
                print("DOCX ERROR:", e)

        else:
            return ""

    except Exception as e:
        print("OCR ERROR:", e)

    return clean_text(text)