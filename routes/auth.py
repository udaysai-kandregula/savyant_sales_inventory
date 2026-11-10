from flask import Blueprint, request, jsonify, session
from extensions import limiter
from services.auth_service import (
    register_user,
    authenticate_user
)
from services.auth_decorators import login_required

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be a JSON object"
        }), 400

    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Validate input types
    if not isinstance(name, str):
        return jsonify({
            "success": False,
            "message": "Name must be text"
        }), 400

    if not isinstance(email, str):
        return jsonify({
            "success": False,
            "message": "Email must be text"
        }), 400

    if not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Password must be text"
        }), 400

    name = name.strip()
    email = email.strip().lower()

    # Validate required fields
    if not name or not email or not password:
        return jsonify({
            "success": False,
            "message": "Name, email and password are required"
        }), 400

    if len(name) > 100:
        return jsonify({
            "success": False,
            "message": "Name cannot exceed 100 characters"
        }), 400

    if len(email) > 150:
        return jsonify({
            "success": False,
            "message": "Email cannot exceed 150 characters"
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
@limiter.limit("5 per minute")
def login():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must be a JSON object"
        }), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "Email and password must be text"
        }), 400

    email = email.strip().lower()

    if not email or not password:
        return jsonify({
            "success": False,
            "message": "Email and password are required"
        }), 400

    if len(email) > 150:
        return jsonify({
            "success": False,
            "message": "Invalid email or password"
        }), 401

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
@login_required
def current_user():

    if not all(key in session for key in ("user_id", "name", "role")):
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
