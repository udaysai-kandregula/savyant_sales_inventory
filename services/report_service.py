from database.db import get_db_connection


def get_customer_sales_summary():
    """
    Return sales totals for every customer.

    Customers without confirmed orders are also included.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    c.id AS customer_id,
                    c.name AS customer_name,
                    c.email,
                    c.mobile,
                    c.city,
                    COUNT(so.id) AS total_orders,
                    COALESCE(SUM(so.grand_total), 0.00) AS total_sales
                FROM customers c
                LEFT JOIN sales_orders so
                    ON so.customer_id = c.id
                    AND so.status = 'confirmed'
                GROUP BY
                    c.id,
                    c.name,
                    c.email,
                    c.mobile,
                    c.city
                ORDER BY total_sales DESC, c.name ASC
            """

            cursor.execute(query)
            return cursor.fetchall()

    finally:
        connection.close()


def get_product_sales_summary():
    """
    Return quantity sold and sales amount for every product.

    Only confirmed orders are included.
    Products with no confirmed sales are also included.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    p.id AS product_id,
                    p.product_code,
                    p.name AS product_name,
                    p.category,
                    p.price AS current_price,
                    p.stock_quantity,
                    COALESCE(
                        SUM(CASE WHEN so.id IS NOT NULL THEN soi.quantity ELSE 0 END),
                        0
                    ) AS quantity_sold,

                    COALESCE(
                        SUM(CASE WHEN so.id IS NOT NULL THEN soi.amount ELSE 0 END),
                        0.00
                    ) AS total_sales
                FROM products p
                LEFT JOIN sales_order_items soi
                    ON soi.product_id = p.id
                LEFT JOIN sales_orders so
                    ON so.id = soi.sales_order_id
                    AND so.status = 'confirmed'
                GROUP BY
                    p.id,
                    p.product_code,
                    p.name,
                    p.category,
                    p.price,
                    p.stock_quantity
                ORDER BY total_sales DESC, p.name ASC
            """

            cursor.execute(query)
            return cursor.fetchall()

    finally:
        connection.close()


def get_low_stock_report(threshold=5):
    """
    Return products whose stock is below the given threshold.
    """

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            query = """
                SELECT
                    id AS product_id,
                    product_code,
                    name AS product_name,
                    category,
                    price,
                    stock_quantity,
                    status
                FROM products
                WHERE stock_quantity < %s
                ORDER BY stock_quantity ASC, name ASC
            """

            cursor.execute(query, (threshold,))
            return cursor.fetchall()

    finally:
        connection.close()

