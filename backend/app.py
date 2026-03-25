from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from ocr_engine import extract_text
from pii_detector import detect_pii
from masker import mask_pii
from ai_detector import detect_ai_entities

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# 🔐 LOGIN IMPORT
from auth import auth

app = Flask(__name__)
CORS(app)

# 🔐 REGISTER LOGIN ROUTES
app.register_blueprint(auth)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -------- CREATE PDF --------
def create_pdf(text, path):
    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)


# -------- HOME --------
@app.route("/")
def home():
    return "✅ SmartDocShield Backend Running"


# -------- DOCUMENT TYPE --------
def classify_document(text):
    t = text.lower()

    if "aadhaar" in t or "uidai" in t:
        return "Aadhaar Card"
    elif "income tax" in t or "permanent account number" in t:
        return "PAN Card"
    else:
        return "General Document"


# -------- UPLOAD --------
@app.route("/upload", methods=["POST"])
def upload_file():
    try:
        file = request.files["file"]

        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # OCR
        text = extract_text(filepath)

        if not text.strip():
            return jsonify({"error": "OCR failed"})

        # PII
        pii = detect_pii(text)

        # MASK
        masked_text = mask_pii(text, pii)

        # AI
        ai = detect_ai_entities(text)

        # DOCUMENT TYPE
        doc_type = classify_document(text)

        # RISK
        score = (
            len(pii["aadhaar"]) * 5 +
            len(pii["pan"]) * 4 +
            len(pii["phone"]) * 3 +
            len(pii["dob"]) * 2
        )

        risk = "LOW"
        if score >= 8:
            risk = "HIGH"
        elif score >= 4:
            risk = "MEDIUM"

        # OUTPUT FILE
        output_name = os.path.splitext(filename)[0] + "_masked.pdf"
        output_path = os.path.join(UPLOAD_FOLDER, output_name)

        create_pdf(masked_text, output_path)

        return jsonify({
            "masked_text": masked_text,
            "pii": pii,
            "ai": ai,
            "risk": risk,
            "file_type": filename.split(".")[-1],
            "doc_type": doc_type,
            "download_url": f"http://127.0.0.1:5000/download/{output_name}"
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# -------- DOWNLOAD --------
@app.route("/download/<filename>")
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)

    if not os.path.exists(path):
        return jsonify({"error": "File not found!"})

    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)