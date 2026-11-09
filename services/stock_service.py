
from database.db import get_db_connection


VALID_MOVEMENT_TYPES = (
    "opening",
    "adjustment_in",
    "adjustment_out",
    "order_deduction",
    "order_restoration"
)


def get_stock_movement_history(
    product_id=None,
    movement_type=None,
    limit=100
):
    """
    Retrieve stock movement history.

    Optional filters:
    - product_id
    - movement_type
    - limit
    """

    # Validate product ID
    if product_id is not None:
        if (
            isinstance(product_id, bool)
            or not isinstance(product_id, int)
            or product_id <= 0
        ):
            raise ValueError("Invalid product ID")

    # Validate movement type
    if movement_type is not None:
        if movement_type not in VALID_MOVEMENT_TYPES:
            raise ValueError("Invalid movement type")

    # Validate limit
    if (
        isinstance(limit, bool)
        or not isinstance(limit, int)
        or limit < 1
        or limit > 500
    ):
        raise ValueError("Limit must be between 1 and 500")

    connection = get_db_connection()

    try:
        conditions = []
        parameters = []

        # Filter by product
        if product_id is not None:
            conditions.append("sm.product_id = %s")
            parameters.append(product_id)

        # Filter by movement type
        if movement_type is not None:
            conditions.append("sm.movement_type = %s")
            parameters.append(movement_type)

        # Build SQL query
        query = """
            SELECT
                sm.id AS movement_id,
                sm.product_id,
                p.product_code,
                p.name AS product_name,
                sm.movement_type,
                sm.quantity_change,
                sm.related_order_id,
                so.order_number,
                sm.reason,
                sm.created_by,
                u.name AS created_by_name,
                sm.created_at

            FROM stock_movements sm

            INNER JOIN products p
                ON sm.product_id = p.id

            INNER JOIN users u
                ON sm.created_by = u.id

            LEFT JOIN sales_orders so
                ON sm.related_order_id = so.id
        """

        # Add optional filters
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Newest movements first
        query += """
            ORDER BY sm.created_at DESC, sm.id DESC
            LIMIT %s
        """

        parameters.append(limit)

        with connection.cursor() as cursor:
            cursor.execute(query, tuple(parameters))
            movements = cursor.fetchall()

        # Convert datetime into JSON-friendly strings
        for movement in movements:
            if movement["created_at"]:
                movement["created_at"] = (
                    movement["created_at"].isoformat()
                )

        return movements

    finally:
        connection.close()
