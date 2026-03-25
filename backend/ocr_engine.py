import pytesseract
from PIL import Image
import PyPDF2
import docx
import re
from pdf2image import convert_from_path
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

POPPLER_PATH = r"C:\Users\Lenovo\Downloads\Release-25.12.0-0 (2)\poppler-25.12.0\Library\bin"


def clean_text(text):
    text = text.upper()

    # fix common OCR mistakes
    text = text.replace("O", "0")
    text = text.replace("I", "1")

    text = re.sub(r'[^A-Z0-9\s:/.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def extract_text(filepath):

    text = ""

    try:
        ext = filepath.lower()

        # IMAGE
        if ext.endswith((".jpg", ".png", ".jpeg")):
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)

        # PDF
        elif ext.endswith(".pdf"):

            # Try direct extraction
            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        if page.extract_text():
                            text += page.extract_text()
            except:
                pass

            # 🔥 If empty → OCR
            if not text.strip():
                images = convert_from_path(filepath, poppler_path=POPPLER_PATH)

                for img in images:
                    text += pytesseract.image_to_string(img)

        # DOCX
        elif ext.endswith(".docx"):
            doc = docx.Document(filepath)

            for para in doc.paragraphs:
                text += para.text + "\n"

            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        text += cell.text + " "

        else:
            return ""

    except Exception as e:
        print("OCR ERROR:", e)

    return clean_text(text)