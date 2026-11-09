
from database.db import get_db_connection



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


def adjust_stock(product_id, adjustment_type, quantity, reason, created_by):
    """Increase or decrease product stock and record the movement."""

    # Validate product ID
    if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
        raise ValueError("Invalid product ID")

    # Validate user ID
    if isinstance(created_by, bool) or not isinstance(created_by, int) or created_by <= 0:
        raise ValueError("Invalid user ID")

    # Validate adjustment type
    if adjustment_type not in ("increase", "decrease"):
        raise ValueError("Adjustment type must be increase or decrease")

    # Validate quantity
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        raise ValueError("Quantity must be a positive whole number")

    # Validate reason
    if not isinstance(reason, str) or not reason.strip():
        raise ValueError("Adjustment reason is required")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Lock the product row
            cursor.execute(
                """
                SELECT id, stock_quantity
                FROM products
                WHERE id = %s
                FOR UPDATE
                """,
                (product_id,)
            )

            product = cursor.fetchone()

            if not product:
                raise ValueError("Product not found")

            current_stock = product["stock_quantity"]

            # 2. Calculate new stock
            if adjustment_type == "increase":
                new_stock = current_stock + quantity
                movement_type = "adjustment_in"
                quantity_change = quantity

            else:
                if quantity > current_stock:
                    raise ValueError(
                        f"Insufficient stock. Available stock: {current_stock}"
                    )

                new_stock = current_stock - quantity
                movement_type = "adjustment_out"
                quantity_change = -quantity

            # 3. Update product stock
            cursor.execute(
                """
                UPDATE products
                SET stock_quantity = %s
                WHERE id = %s
                """,
                (new_stock, product_id)
            )

            # 4. Record stock movement
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
                    movement_type,
                    quantity_change,
                    reason.strip(),
                    created_by
                )
            )

        # 5. Commit both changes together
        connection.commit()

        return {
            "success": True,
            "message": "Stock adjusted successfully",
            "product_id": product_id,
            "previous_stock": current_stock,
            "adjustment_type": adjustment_type,
            "quantity_changed": quantity_change,
            "current_stock": new_stock
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()

