from flask import Blueprint, request, jsonify

auth = Blueprint("auth", __name__)

# Dummy user (you can upgrade later to DB)
USER = {
    "username": "admin",
    "password": "1234"
}

@auth.route("/login", methods=["POST"])
def login():
    data = request.json

    if data["username"] == USER["username"] and data["password"] == USER["password"]:
        return jsonify({"status": "success", "message": "Login successful"})
    
    return jsonify({"status": "fail", "message": "Invalid credentials"})