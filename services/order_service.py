from database.db import get_db_connection

from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime
from uuid import uuid4

from database.db import get_db_connection



MONEY_PLACES = Decimal("0.01")


def money(value):
    """Round money values to two decimal places."""
    return Decimal(str(value)).quantize(
        MONEY_PLACES,
        rounding=ROUND_HALF_UP
    )


def create_draft_order(customer_id, items, discount_percentage, created_by):
    """Create a draft order without deducting product stock."""

    # 1. Validate customer and user IDs
    if isinstance(customer_id, bool) or not isinstance(customer_id, int) or customer_id <= 0:
        raise ValueError("Invalid customer ID")

    if isinstance(created_by, bool) or not isinstance(created_by, int) or created_by <= 0:
        raise ValueError("Invalid user ID")

    # 2. Validate items
    if not isinstance(items, list) or not items:
        raise ValueError("At least one order item is required")

    validated_items = []
    used_product_ids = set()

    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Each order item must be an object")

        product_id = item.get("product_id")
        quantity = item.get("quantity")

        if isinstance(product_id, bool) or not isinstance(product_id, int) or product_id <= 0:
            raise ValueError("Invalid product ID")

        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive whole number")

        if product_id in used_product_ids:
            raise ValueError("Duplicate products are not allowed in one order")

        used_product_ids.add(product_id)

        validated_items.append({
            "product_id": product_id,
            "quantity": quantity
        })

    # 3. Validate discount
    try:
        discount_percentage = Decimal(str(discount_percentage))
    except (InvalidOperation, TypeError, ValueError):
        raise ValueError("Invalid discount percentage")

    if not discount_percentage.is_finite() or not 0 <= discount_percentage <= 20:
        raise ValueError("Discount must be between 0 and 20 percent")

    discount_percentage = discount_percentage.quantize(MONEY_PLACES)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 4. Check customer
            cursor.execute(
                "SELECT id, status FROM customers WHERE id = %s",
                (customer_id,)
            )
            customer = cursor.fetchone()

            if not customer:
                raise ValueError("Customer not found")

            if customer["status"] != "active":
                raise ValueError("Cannot create an order for an inactive customer")

            # 5. Generate order number
            order_number = (
                f"SO-{datetime.now():%Y%m%d}-"
                f"{uuid4().hex[:8].upper()}"
            )

            # 6. Insert draft order
            cursor.execute(
                """
                INSERT INTO sales_orders (
                    order_number,
                    customer_id,
                    status,
                    discount_percentage,
                    subtotal,
                    discount_amount,
                    grand_total,
                    created_by
                )
                VALUES (%s, %s, 'draft', %s, 0.00, 0.00, 0.00, %s)
                """,
                (
                    order_number,
                    customer_id,
                    discount_percentage,
                    created_by
                )
            )

            order_id = cursor.lastrowid
            subtotal = Decimal("0.00")

            # 7. Insert order items
            for item in validated_items:

                cursor.execute(
                    """
                    SELECT id, price, status
                    FROM products
                    WHERE id = %s
                    """,
                    (item["product_id"],)
                )

                product = cursor.fetchone()

                if not product:
                    raise ValueError(
                        f"Product {item['product_id']} not found"
                    )

                if product["status"] != "active":
                    raise ValueError(
                        f"Product {item['product_id']} is inactive"
                    )

                rate = money(product["price"])
                quantity = item["quantity"]
                amount = money(rate * quantity)

                cursor.execute(
                    """
                    INSERT INTO sales_order_items (
                        sales_order_id,
                        product_id,
                        quantity,
                        rate,
                        amount
                    )
                    VALUES (%s, %s, %s, %s, %s)
                    """,
                    (
                        order_id,
                        item["product_id"],
                        quantity,
                        rate,
                        amount
                    )
                )

                subtotal += amount

            # 8. Calculate totals
            subtotal = money(subtotal)

            discount_amount = money(
                subtotal * discount_percentage / Decimal("100")
            )

            grand_total = money(subtotal - discount_amount)

            # 9. Update order totals
            cursor.execute(
                """
                UPDATE sales_orders
                SET subtotal = %s,
                    discount_amount = %s,
                    grand_total = %s
                WHERE id = %s
                """,
                (
                    subtotal,
                    discount_amount,
                    grand_total,
                    order_id
                )
            )

        # 10. Commit the complete order
        connection.commit()

        return {
            "success": True,
            "message": "Draft order created successfully",
            "order_id": order_id,
            "order_number": order_number,
            "status": "draft",
            "subtotal": str(subtotal),
            "discount_percentage": str(discount_percentage),
            "discount_amount": str(discount_amount),
            "grand_total": str(grand_total)
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def get_order_by_id(order_id):
    """Retrieve an order with customer and product details."""

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Retrieve order and customer details
            cursor.execute(
                """
                SELECT
                    so.id,
                    so.order_number,
                    so.customer_id,
                    c.name AS customer_name,
                    c.email AS customer_email,
                    c.mobile AS customer_mobile,
                    so.order_date,
                    so.status,
                    so.discount_percentage,
                    so.subtotal,
                    so.discount_amount,
                    so.grand_total,
                    so.created_by,
                    so.created_at
                FROM sales_orders so
                JOIN customers c ON so.customer_id = c.id
                WHERE so.id = %s
                """,
                (order_id,)
            )

            order = cursor.fetchone()

            if not order:
                return None

            # 2. Retrieve all products in this order
            cursor.execute(
                """
                SELECT
                    soi.id,
                    soi.product_id,
                    p.product_code,
                    p.name AS product_name,
                    soi.quantity,
                    soi.rate,
                    soi.amount
                FROM sales_order_items soi
                JOIN products p ON soi.product_id = p.id
                WHERE soi.sales_order_id = %s
                ORDER BY soi.id
                """,
                (order_id,)
            )

            items = cursor.fetchall()

        # 3. Convert database values into JSON-friendly values
        for field in (
            "discount_percentage",
            "subtotal",
            "discount_amount",
            "grand_total"
        ):
            order[field] = str(order[field])

        for field in ("order_date", "created_at"):
            if order[field]:
                order[field] = order[field].isoformat()

        for item in items:
            item["rate"] = str(item["rate"])
            item["amount"] = str(item["amount"])

        order["items"] = items

        return order

    finally:
        connection.close()


def confirm_order(order_id, confirmed_by):
    """Confirm a draft order and deduct stock atomically."""

    if isinstance(order_id, bool) or not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("Invalid order ID")

    if isinstance(confirmed_by, bool) or not isinstance(confirmed_by, int) or confirmed_by <= 0:
        raise ValueError("Invalid user ID")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Lock the order
            cursor.execute(
                """
                SELECT id, status
                FROM sales_orders
                WHERE id = %s
                FOR UPDATE
                """,
                (order_id,)
            )

            order = cursor.fetchone()

            if not order:
                raise ValueError("Order not found")

            if order["status"] != "draft":
                raise ValueError(
                    f"Only draft orders can be confirmed. Current status: {order['status']}"
                )

            # 2. Get order items
            cursor.execute(
                """
                SELECT product_id, quantity
                FROM sales_order_items
                WHERE sales_order_id = %s
                ORDER BY product_id
                """,
                (order_id,)
            )

            items = cursor.fetchall()

            if not items:
                raise ValueError("Order has no items")

            # 3. Lock products in a consistent order
            for item in items:

                cursor.execute(
                    """
                    SELECT id, name, stock_quantity
                    FROM products
                    WHERE id = %s
                    FOR UPDATE
                    """,
                    (item["product_id"],)
                )

                product = cursor.fetchone()

                if not product:
                    raise ValueError(
                        f"Product {item['product_id']} not found"
                    )

                if product["stock_quantity"] < item["quantity"]:
                    raise ValueError(
                        f"Insufficient stock for {product['name']}. "
                        f"Available: {product['stock_quantity']}, "
                        f"Required: {item['quantity']}"
                    )

            # 4. Deduct stock and record movements
            for item in items:

                cursor.execute(
                    """
                    UPDATE products
                    SET stock_quantity = stock_quantity - %s
                    WHERE id = %s
                      AND stock_quantity >= %s
                    """,
                    (
                        item["quantity"],
                        item["product_id"],
                        item["quantity"]
                    )
                )

                if cursor.rowcount != 1:
                    raise ValueError(
                        f"Stock deduction failed for product {item['product_id']}"
                    )

                cursor.execute(
                    """
                    INSERT INTO stock_movements (
                        product_id,
                        movement_type,
                        quantity_change,
                        related_order_id,
                        reason,
                        created_by
                    )
                    VALUES (%s, 'order_deduction', %s, %s, %s, %s)
                    """,
                    (
                        item["product_id"],
                        -item["quantity"],
                        order_id,
                        f"Stock deducted for order {order_id}",
                        confirmed_by
                    )
                )

            # 5. Update order status
            cursor.execute(
                """
                UPDATE sales_orders
                SET status = 'confirmed'
                WHERE id = %s
                """,
                (order_id,)
            )

        # 6. Commit all changes together
        connection.commit()

        return {
            "success": True,
            "message": "Order confirmed successfully",
            "order_id": order_id,
            "status": "confirmed"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def cancel_order(order_id, cancelled_by):
    """Cancel an order and restore stock if it was confirmed."""

    if isinstance(order_id, bool) or not isinstance(order_id, int) or order_id <= 0:
        raise ValueError("Invalid order ID")

    if isinstance(cancelled_by, bool) or not isinstance(cancelled_by, int) or cancelled_by <= 0:
        raise ValueError("Invalid user ID")

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # 1. Lock the order
            cursor.execute(
                """
                SELECT id, status
                FROM sales_orders
                WHERE id = %s
                FOR UPDATE
                """,
                (order_id,)
            )

            order = cursor.fetchone()

            if not order:
                raise ValueError("Order not found")

            if order["status"] == "cancelled":
                raise ValueError("Order is already cancelled")

            # 2. Restore stock only for confirmed orders
            if order["status"] == "confirmed":

                cursor.execute(
                    """
                    SELECT product_id, quantity
                    FROM sales_order_items
                    WHERE sales_order_id = %s
                    ORDER BY product_id
                    """,
                    (order_id,)
                )

                items = cursor.fetchall()

                for item in items:

                    cursor.execute(
                        """
                        SELECT id
                        FROM products
                        WHERE id = %s
                        FOR UPDATE
                        """,
                        (item["product_id"],)
                    )

                    product = cursor.fetchone()

                    if not product:
                        raise ValueError(
                            f"Product {item['product_id']} not found"
                        )

                    cursor.execute(
                        """
                        UPDATE products
                        SET stock_quantity = stock_quantity + %s
                        WHERE id = %s
                        """,
                        (item["quantity"], item["product_id"])
                    )

                    cursor.execute(
                        """
                        INSERT INTO stock_movements (
                            product_id,
                            movement_type,
                            quantity_change,
                            related_order_id,
                            reason,
                            created_by
                        )
                        VALUES (
                            %s,
                            'order_restoration',
                            %s,
                            %s,
                            %s,
                            %s
                        )
                        """,
                        (
                            item["product_id"],
                            item["quantity"],
                            order_id,
                            f"Stock restored for cancelled order {order_id}",
                            cancelled_by
                        )
                    )

            # 3. Update order status
            cursor.execute(
                """
                UPDATE sales_orders
                SET status = 'cancelled'
                WHERE id = %s
                """,
                (order_id,)
            )

        connection.commit()

        return {
            "success": True,
            "message": "Order cancelled successfully",
            "order_id": order_id,
            "status": "cancelled"
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
