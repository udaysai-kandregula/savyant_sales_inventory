
from functools import wraps
from flask import session, jsonify


def login_required(view_function):
    """Allow access only to logged-in users."""

    @wraps(view_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return jsonify({
                "success": False,
                "message": "Please log in first"
            }), 401

        return view_function(*args, **kwargs)

    return wrapper


def admin_required(view_function):
    """Allow access only to administrators."""

    @wraps(view_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return jsonify({
                "success": False,
                "message": "Please log in first"
            }), 401

        if session.get("role") != "admin":
            return jsonify({
                "success": False,
                "message": "Admin access required"
            }), 403

        return view_function(*args, **kwargs)

    return wrapper


def sales_required(view_function):
    """Allow access only to sales users."""

    @wraps(view_function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return jsonify({
                "success": False,
                "message": "Please log in first"
            }), 401

        if session.get("role") != "sales":
            return jsonify({
                "success": False,
                "message": "Sales access required"
            }), 403

        return view_function(*args, **kwargs)

    return wrapper
