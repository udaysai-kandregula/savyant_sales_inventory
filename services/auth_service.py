
from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection


def hash_password(password):
    """Convert a plain password into a secure hash."""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Check whether a password matches its stored hash."""
    return check_password_hash(password_hash, password)


def register_user(name, email, password, role="sales"):
    """Register a new user in the database."""

    if not name or not email or not password:
        return {"success": False, "message": "All fields are required"}

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
                (name, email.strip().lower(), password_hash, role)
            )

        connection.commit()

        return {
            "success": True,
            "message": "User registered successfully"
        }

    except Exception as error:
        connection.rollback()

        if getattr(error, "args", [None])[0] == 1062:
            return {"success": False, "message": "Email already exists"}

        raise

    finally:
        connection.close()
