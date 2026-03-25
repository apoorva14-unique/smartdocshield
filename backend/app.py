from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from ocr_engine import extract_text
from pii_detector import detect_pii
from masker import mask_pii
from ai_detector import detect_ai_entities

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# 🔐 LOGIN
from auth import auth

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth)

# -------- FOLDERS --------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")

# -------- CREATE PDF --------
def create_pdf(text, path):
    doc = SimpleDocTemplate(path)
    styles = getSampleStyleSheet()

    content = []
    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)

# -------- SERVE FRONTEND --------
@app.route("/")
def serve_frontend():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(FRONTEND_DIR, path)

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

        # PII Detection
        pii = detect_pii(text)

        # Masking
        masked_text = mask_pii(text, pii)

        # AI Detection
        ai = detect_ai_entities(text)

        # Document Type
        doc_type = classify_document(text)

        # Risk Calculation
        score = (
            len(pii["aadhaar"]) * 5 +
            len(pii["pan"]) * 4 +
            len(pii["phone"]) * 3 +
            len(pii["dob"]) * 2
        )

        if score >= 8:
            risk = "HIGH"
        elif score >= 4:
            risk = "MEDIUM"
        else:
            risk = "LOW"

        # Create Output PDF
        output_name = os.path.splitext(filename)[0] + "_masked.pdf"
        output_path = os.path.join(UPLOAD_FOLDER, output_name)

        create_pdf(masked_text, output_path)

        # Dynamic URL (works in deployment)
        base_url = request.host_url

        return jsonify({
            "masked_text": masked_text,
            "pii": pii,
            "ai": ai,
            "risk": risk,
            "file_type": filename.split(".")[-1],
            "doc_type": doc_type,
            "download_url": f"{base_url}download/{output_name}"
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

# -------- RUN --------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)