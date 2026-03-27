import pytesseract
from PIL import Image
import PyPDF2
import docx
import re
from pdf2image import convert_from_path
import platform
import cv2
import numpy as np

# AUTO CONFIG
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    POPPLER_PATH = r"C:\Users\Lenovo\Downloads\Release-25.12.0-0 (2)\poppler-25.12.0\Library\bin"
else:
    POPPLER_PATH = None


# 🔥 PREPROCESS IMAGE (STRONG)
def preprocess_image(path):
    img = cv2.imread(path)

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Improve contrast
    gray = cv2.convertScaleAbs(gray, alpha=2, beta=0)

    # Blur
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold
    thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    return thresh


# CLEAN TEXT
def clean_text(text):
    text = text.replace("\n", " ")

    text = text.replace("O", "0")
    text = text.replace("I", "1")
    text = text.replace("l", "1")

    text = text.upper()

    text = re.sub(r'[^A-Z0-9:/.\-\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


# MAIN OCR
def extract_text(filepath):

    text = ""

    try:
        ext = filepath.lower()

        # IMAGE
        if ext.endswith((".jpg", ".png", ".jpeg")):
            processed = preprocess_image(filepath)

            config = '--oem 3 --psm 6'   # 🔥 removed whitelist

            text = pytesseract.image_to_string(processed, config=config)

        # PDF
        elif ext.endswith(".pdf"):

            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted

            if not text.strip():

                if POPPLER_PATH:
                    images = convert_from_path(filepath, poppler_path=POPPLER_PATH)
                else:
                    images = convert_from_path(filepath)

                for img in images:
                    img_np = np.array(img)

                    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

                    text += pytesseract.image_to_string(thresh, config='--psm 6')

        # DOCX
        elif ext.endswith(".docx"):
            doc = docx.Document(filepath)
            for para in doc.paragraphs:
                text += para.text + "\n"

    except Exception as e:
        print("OCR ERROR:", e)

    return clean_text(text)