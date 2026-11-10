
from functools import wraps

from flask import session, jsonify

from database.db import get_db_connection


def get_current_user_role(user_id):
    """Get the user's latest role directly from the database."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT role
                FROM users
                WHERE id = %s
                """,
                (user_id,)
            )

            user = cursor.fetchone()

            if not user:
                return None

            return user["role"]

    finally:
        connection.close()


def authorization_required(allowed_roles=None):
    """Verify login and current database role."""

    def decorator(view_function):

        @wraps(view_function)
        def wrapper(*args, **kwargs):

            # 1. Check whether the user is logged in
            user_id = session.get("user_id")

            if user_id is None:
                return jsonify({
                    "success": False,
                    "message": "Please log in first"
                }), 401

            # 2. Verify the current role from MySQL
            try:
                current_role = get_current_user_role(user_id)

            except Exception:
                return jsonify({
                    "success": False,
                    "message": "Unable to verify user permissions. Please try again."
                }), 503

            # 3. Check whether the user still exists
            if current_role is None:
                session.clear()

                return jsonify({
                    "success": False,
                    "message": "User account not found. Please log in again."
                }), 401

            # 4. Refresh the role stored in the session
            session["role"] = current_role

            # 5. Check allowed roles
            if allowed_roles and current_role not in allowed_roles:
                return jsonify({
                    "success": False,
                    "message": "You do not have permission to access this resource"
                }), 403

            return view_function(*args, **kwargs)

        return wrapper

    return decorator


def login_required(view_function):
    """Allow access only to existing logged-in users."""

    return authorization_required()(view_function)


def admin_required(view_function):
    """Allow access only to administrators."""

    return authorization_required(["admin"])(view_function)


def sales_required(view_function):
    """Allow access only to sales users."""

    return authorization_required(["sales"])(view_function)
