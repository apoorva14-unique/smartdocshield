import pytesseract
from PIL import Image
import PyPDF2
import docx
import re
import platform

# -------- AUTO DETECT OS --------
IS_WINDOWS = platform.system() == "Windows"

if IS_WINDOWS:
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# -------- CLEAN TEXT --------
def clean_text(text):
    text = text.upper()

    # Fix OCR mistakes
    text = text.replace("O", "0")
    text = text.replace("I", "1")

    text = re.sub(r'[^A-Z0-9\s:/.\-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -------- EXTRACT TEXT --------
def extract_text(filepath):

    text = ""

    try:
        ext = filepath.lower()

        # -------- IMAGE --------
        if ext.endswith((".jpg", ".png", ".jpeg")):
            if IS_WINDOWS:
                img = Image.open(filepath)
                text = pytesseract.image_to_string(img)
            else:
                print("⚠️ OCR not supported on Render for images")
                return ""

        # -------- PDF --------
        elif ext.endswith(".pdf"):

            # ✅ TEXT-BASED PDF (works on Render)
            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted
            except Exception as e:
                print("PDF TEXT ERROR:", e)

            # ❌ OCR fallback only for Windows
            if not text.strip() and IS_WINDOWS:
                try:
                    from pdf2image import convert_from_path

                    images = convert_from_path(filepath)

                    for img in images:
                        text += pytesseract.image_to_string(img)

                except Exception as e:
                    print("PDF OCR ERROR:", e)

        # -------- DOCX --------
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