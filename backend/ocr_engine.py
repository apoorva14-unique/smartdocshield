import pytesseract
from PIL import Image
import PyPDF2
import docx
import re
from pdf2image import convert_from_path
import platform
import cv2
import numpy as np

# -------- SAFE OCR CONFIG --------
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\Users\Lenovo\Downloads\Release-25.12.0-0 (2)\poppler-25.12.0\Library\bin"
else:
    # ❌ Render / Linux → no tesseract installed
    pytesseract.pytesseract.tesseract_cmd = None
    POPPLER_PATH = None


# -------- PREPROCESS --------
def preprocess_image(path):
    img = cv2.imread(path)

    if img is None:
        return None

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.convertScaleAbs(gray, alpha=2, beta=0)

    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )[1]

    return thresh


# -------- CLEAN --------
def clean_text(text):
    if not text:
        return ""

    text = text.replace("\n", " ")
    text = text.upper()

    text = re.sub(r'[^A-Z0-9:/.\-\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# -------- MAIN OCR --------
def extract_text(filepath):

    text = ""

    try:
        ext = filepath.lower()

        # -------- IMAGE --------
        if ext.endswith((".jpg", ".png", ".jpeg")):

            processed = preprocess_image(filepath)

            if processed is None:
                return ""

            try:
                text = pytesseract.image_to_string(
                    processed, config='--oem 3 --psm 6'
                )
            except:
                print("⚠️ Tesseract not available in deployment")
                return ""

        # -------- PDF --------
        elif ext.endswith(".pdf"):

            try:
                with open(filepath, "rb") as f:
                    reader = PyPDF2.PdfReader(f)

                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text += extracted
            except:
                print("⚠️ PDF read failed")

            # fallback OCR
            if not text.strip():
                try:
                    images = convert_from_path(filepath)

                    for img in images:
                        img_np = np.array(img)
                        gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)

                        text += pytesseract.image_to_string(gray)
                except:
                    print("⚠️ Poppler/Tesseract missing → skipping OCR")
                    return ""

        # -------- DOCX --------
        elif ext.endswith(".docx"):
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"

    except Exception as e:
        print("OCR ERROR:", e)
        return ""

    return clean_text(text)