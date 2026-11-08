
from flask import Blueprint, request, jsonify, session

from services.auth_service import (
    register_user,
    authenticate_user
)

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}

    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not all([name, email, password]):
        return jsonify({
            "success": False,
            "message": "Name, email and password are required"
        }), 400

    if len(password) < 8:
        return jsonify({
            "success": False,
            "message": "Password must contain at least 8 characters"
        }), 400

    try:
        result = register_user(
            name=name,
            email=email,
            password=password,
            role="sales"
        )

        status_code = 201 if result["success"] else 409

        return jsonify(result), status_code

    except Exception:
        return jsonify({
            "success": False,
            "message": "Registration failed"
        }), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    try:
        user = authenticate_user(email, password)

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid email or password"
            }), 401

        session.clear()
        session["user_id"] = user["id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        return jsonify({
            "success": True,
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"]
            }
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Login failed"
        }), 500


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()

    return jsonify({
        "success": True,
        "message": "Logout successful"
    }), 200


@auth_bp.route("/me", methods=["GET"])
def current_user():
    if "user_id" not in session:
        return jsonify({
            "success": False,
            "message": "Please log in first"
        }), 401

    return jsonify({
        "success": True,
        "user": {
            "id": session["user_id"],
            "name": session["name"],
            "role": session["role"]
        }
    }), 200
