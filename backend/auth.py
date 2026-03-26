from flask import Blueprint, request, jsonify

auth = Blueprint("auth", __name__)

USER = {
    "username": "admin",
    "password": "1234"
}

@auth.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    print("LOGIN:", data)

    if data.get("username") == USER["username"] and data.get("password") == USER["password"]:
        return jsonify({"status": "success"})
    else:
        return jsonify({
            "status": "fail",
            "message": "Invalid username or password"
        })