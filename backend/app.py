from flask import Flask, request, jsonify, send_file, session
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename

from ocr_engine import extract_text
from pii_detector import detect_pii
from masker import mask_pii
from ai_detector import detect_ai_entities
from cleaner import clean_text
from utils import classify_document, detect_fraud

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

app = Flask(__name__)

app.secret_key = "supersecretkey"

CORS(app, supports_credentials=True, origins=[
    "http://127.0.0.1:5500"
])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False


@app.route("/")
def home():
    return "✅ SmartDocShield Backend Running"


# -------- LOGIN --------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    username = data["username"]
    password = data["password"]

    if username in USERS and USERS[username] == password:
        session["user"] = username
        return jsonify({"status": "success"})

    return jsonify({"status": "fail"})

USERS = {
    "admin": "1234",
    "sweety": "1234"
}

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    USERS[data["username"]] = data["password"]

    return jsonify({"status": "registered"})

# -------- CHECK AUTH --------
@app.route("/check-auth")
def check_auth():
    return jsonify({"loggedIn": "user" in session})


# -------- LOGOUT --------
@app.route("/logout")
def logout():
    session.clear()
    return jsonify({"status": "logout"})


# -------- UPLOAD --------
@app.route("/upload", methods=["POST"])
def upload():

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    file = request.files["file"]

    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    # 🔍 OCR
    text = extract_text(filepath)
    text = clean_text(text)

    # 🧠 AI Detection
    ai_data = detect_ai_entities(text)

    # 🔐 PII Detection
    pii = detect_pii(text)

    # 🛡️ Masking
    masked_text = mask_pii(text, pii)

    # 📂 Document Type
    doc_type = classify_document(text)

    # ⚠️ Risk Calculation
    total_pii = sum(len(v) for v in pii.values())

    if total_pii == 0:
        risk = "LOW"
    elif total_pii < 3:
        risk = "MEDIUM"
    else:
        risk = "HIGH"

    # 🔥 Fraud Detection
    fraud = detect_fraud(pii)

    # 📄 Generate Better PDF
    output_name = filename.split(".")[0] + "_masked.pdf"
    output_path = os.path.join(UPLOAD_FOLDER, output_name)

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(output_path)

    content = []
    content.append(Paragraph("<b>SmartDocShield Protected Document</b>", styles["Title"]))
    content.append(Paragraph("<br/>", styles["Normal"]))
    content.append(Paragraph(f"<b>Risk Level:</b> {risk}", styles["Normal"]))
    content.append(Paragraph("<br/>", styles["Normal"]))
    content.append(Paragraph(masked_text, styles["Normal"]))

    doc.build(content)

    os.remove(filepath)

    return jsonify({
        "masked_text": masked_text,
        "pii": pii,
        "download_url": f"http://127.0.0.1:5000/download/{output_name}",
        "risk": risk,
        "file_type": filename.split(".")[-1],
        "ai": ai_data,
        "fraud": fraud
    })


# -------- DOWNLOAD --------
@app.route("/download/<filename>")
def download(filename):

    if "user" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    path = os.path.join(UPLOAD_FOLDER, filename)
    return send_file(path, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)