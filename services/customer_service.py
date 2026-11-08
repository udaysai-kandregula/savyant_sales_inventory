
from database.db import get_db_connection


def create_customer(name, email=None, mobile=None, city=None):
    """Create a new customer in the database."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customers (name, email, mobile, city)
                VALUES (%s, %s, %s, %s)
                """,
                (name, email, mobile, city)
            )

            customer_id = cursor.lastrowid

        connection.commit()

        return {
            "success": True,
            "message": "Customer created successfully",
            "customer_id": customer_id
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()




def get_all_customers():
    """Return all customers from the database."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    mobile,
                    city,
                    status,
                    created_at
                FROM customers
                ORDER BY id DESC
                """
            )

            customers = cursor.fetchall()

        return customers

    finally:
        connection.close()



def get_customer_by_id(customer_id):
    """Get one customer using customer ID."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email,
                    mobile,
                    city,
                    status,
                    created_at
                FROM customers
                WHERE id = %s
                """,
                (customer_id,)
            )

            customer = cursor.fetchone()

        return customer

    finally:
        connection.close()



def update_customer(customer_id, name, email=None, mobile=None, city=None):
    """Update an existing customer's details."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE customers
                SET name = %s,
                    email = %s,
                    mobile = %s,
                    city = %s
                WHERE id = %s
                """,
                (name, email, mobile, city, customer_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM customers WHERE id = %s",
                    (customer_id,)
                )

                if not cursor.fetchone():
                    connection.rollback()
                    return False

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def set_customer_status(customer_id, status):
    """Activate or deactivate a customer."""
    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE customers
                SET status = %s
                WHERE id = %s
                """,
                (status, customer_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM customers WHERE id = %s",
                    (customer_id,)
                )

                if not cursor.fetchone():
                    connection.rollback()
                    return False

        connection.commit()
        return True

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()