
from database.db import get_db_connection
# from database.db import get_db_connection


def create_product(
    product_code,
    name,
    category,
    price,
    stock_quantity,
    created_by
):
    """Create a product and record its opening stock."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Insert product
            cursor.execute(
                """
                INSERT INTO products (
                    product_code,
                    name,
                    category,
                    price,
                    stock_quantity
                )
                VALUES (%s, %s, %s, %s, %s)
                """,
                (
                    product_code,
                    name,
                    category,
                    price,
                    stock_quantity
                )
            )

            product_id = cursor.lastrowid

            # Record opening stock when initial stock is greater than zero
            if stock_quantity > 0:
                cursor.execute(
                    """
                    INSERT INTO stock_movements (
                        product_id,
                        movement_type,
                        quantity_change,
                        reason,
                        created_by
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        product_id,
                        "opening",
                        stock_quantity,
                        "Initial product stock",
                        created_by
                    )
                )

        connection.commit()

        return {
            "success": True,
            "message": "Product created successfully",
            "product_id": product_id
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_all_products():
    """Retrieve all products from the database."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    product_code,
                    name,
                    category,
                    price,
                    stock_quantity,
                    status,
                    created_at
                FROM products
                ORDER BY id DESC
                """
            )

            products = cursor.fetchall()

        return products

    finally:
        connection.close()


def get_product_by_id(product_id):
    """Retrieve a single product using its ID."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    product_code,
                    name,
                    category,
                    price,
                    stock_quantity,
                    status,
                    created_at
                FROM products
                WHERE id = %s
                """,
                (product_id,)
            )

            product = cursor.fetchone()

        return product

    finally:
        connection.close()


def update_product(product_id, name, category, price):
    """Update product details without changing stock quantity."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET name = %s,
                    category = %s,
                    price = %s
                WHERE id = %s
                """,
                (name, category, price, product_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM products WHERE id = %s",
                    (product_id,)
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


def set_product_status(product_id, status):
    """Activate or deactivate a product."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE products
                SET status = %s
                WHERE id = %s
                """,
                (status, product_id)
            )

            if cursor.rowcount == 0:
                cursor.execute(
                    "SELECT id FROM products WHERE id = %s",
                    (product_id,)
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
