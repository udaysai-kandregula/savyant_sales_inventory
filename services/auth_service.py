from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection


def hash_password(password):
    """Convert a plain password into a secure hash."""

    if not isinstance(password, str):
        raise ValueError("Password must be text")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")

    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Check whether a password matches its stored hash."""

    if not isinstance(password, str):
        return False

    if not isinstance(password_hash, str):
        return False

    try:
        return check_password_hash(password_hash, password)
    except (ValueError, TypeError):
        return False


def register_user(name, email, password, role="sales"):
    """Register a new user in the database."""

    # Validate input types
    if not isinstance(name, str):
        return {"success": False, "message": "Name must be text"}

    if not isinstance(email, str):
        return {"success": False, "message": "Email must be text"}

    if not isinstance(password, str):
        return {"success": False, "message": "Password must be text"}

    if not isinstance(role, str):
        return {"success": False, "message": "Invalid user role"}

    # Normalize inputs
    name = name.strip()
    email = email.strip().lower()

    # Validate required fields
    if not name or not email or not password:
        return {"success": False, "message": "All fields are required"}

    # Validate database column limits
    if len(name) > 100:
        return {"success": False, "message": "Name cannot exceed 100 characters"}

    if len(email) > 150:
        return {"success": False, "message": "Email cannot exceed 150 characters"}

    # Validate password
    if len(password) < 8:
        return {
            "success": False,
            "message": "Password must contain at least 8 characters"
        }

    # Validate role
    if role not in ("admin", "sales"):
        return {"success": False, "message": "Invalid user role"}

    password_hash = hash_password(password)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (name, email, password_hash, role)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, password_hash, role)
            )

        connection.commit()

        return {
            "success": True,
            "message": "User registered successfully"
        }

    except Exception as error:
        connection.rollback()

        if getattr(error, "args", [None])[0] == 1062:
            return {
                "success": False,
                "message": "Email already exists"
            }

        raise

    finally:
        connection.close()


def authenticate_user(email, password):
    """Find a user and verify their password."""

    # Validate input types
    if not isinstance(email, str) or not isinstance(password, str):
        return None

    email = email.strip().lower()

    if not email or not password or len(email) > 150:
        return None

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, name, email, password_hash, role
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            user = cursor.fetchone()

        if user and verify_password(password, user["password_hash"]):
            return user

        return None

    finally:
        connection.close()
