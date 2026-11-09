
import csv
import io
from decimal import Decimal, InvalidOperation

from database.db import get_db_connection


REQUIRED_COLUMNS = [
    "product_code",
    "name",
    "category",
    "price",
    "stock_quantity"
]


def validate_csv_content(file_content):
    """
    Validate every CSV row before inserting anything into the database.
    Returns a list of validated products or raises ValueError.
    """

    try:
        text_content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise ValueError("CSV file must use UTF-8 encoding.")

    reader = csv.DictReader(io.StringIO(text_content))

    if not reader.fieldnames:
        raise ValueError("CSV file is empty.")

    headers = [header.strip() for header in reader.fieldnames]

    if headers != REQUIRED_COLUMNS:
        raise ValueError(
            "Invalid CSV columns. Required columns are: "
            + ", ".join(REQUIRED_COLUMNS)
        )

    products = []
    seen_codes = set()
    errors = []

    for row_number, row in enumerate(reader, start=2):

        # Reject rows with extra columns.
        if None in row:
            errors.append(
                f"Row {row_number}: Extra column values found."
            )
            continue

        # Reject completely blank rows.
        if all(
            value is None or not str(value).strip()
            for value in row.values()
        ):
            errors.append(
                f"Row {row_number}: Empty row."
            )
            continue

        product_code = (row.get("product_code") or "").strip()
        name = (row.get("name") or "").strip()
        category = (row.get("category") or "").strip()
        price_value = (row.get("price") or "").strip()
        stock_value = (row.get("stock_quantity") or "").strip()

        if not product_code:
            errors.append(
                f"Row {row_number}: Product code is required."
            )
            continue

        if not name:
            errors.append(
                f"Row {row_number}: Product name is required."
            )
            continue

        if product_code in seen_codes:
            errors.append(
                f"Row {row_number}: Duplicate product code "
                f"'{product_code}' in CSV."
            )
            continue

        seen_codes.add(product_code)

        # Validate price using Decimal, not float.
        try:
            price = Decimal(price_value)

            if not price.is_finite():
                raise ValueError()

            if price < 0:
                raise ValueError()

            if price.as_tuple().exponent < -2:
                raise ValueError()

        except (InvalidOperation, ValueError):
            errors.append(
                f"Row {row_number}: Price must be a valid "
                "non-negative number with at most 2 decimal places."
            )
            continue

        # Validate stock as a whole non-negative integer.
        try:
            stock_quantity = int(stock_value)

            if stock_quantity < 0:
                raise ValueError()

        except (ValueError, TypeError):
            errors.append(
                f"Row {row_number}: Stock quantity must be "
                "a non-negative whole number."
            )
            continue

        products.append({
            "product_code": product_code,
            "name": name,
            "category": category or None,
            "price": format(price, ".2f"),
            "stock_quantity": stock_quantity
        })

    if errors:
        raise ValueError({
            "message": "CSV validation failed. No products were imported.",
            "errors": errors
        })

    if not products:
        raise ValueError("CSV contains no product records.")

    return products


def import_products_from_csv(file_content, created_by):
    """
    Import all validated products in a single transaction.
    If any database operation fails, the complete import is rolled back.
    """

    products = validate_csv_content(file_content)

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:

            # Check whether any product code already exists.
            product_codes = [
                product["product_code"]
                for product in products
            ]

            placeholders = ", ".join(["%s"] * len(product_codes))

            cursor.execute(
                f"""
                SELECT product_code
                FROM products
                WHERE product_code IN ({placeholders})
                """,
                product_codes
            )

            existing_products = cursor.fetchall()

            if existing_products:
                existing_codes = [
                    product["product_code"]
                    for product in existing_products
                ]

                raise ValueError({
                    "message": (
                        "Some product codes already exist. "
                        "No products were imported."
                    ),
                    "duplicate_product_codes": existing_codes
                })

            imported_products = []

            for product in products:

                cursor.execute(
                    """
                    INSERT INTO products (
                        product_code,
                        name,
                        category,
                        price,
                        stock_quantity,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, 'active')
                    """,
                    (
                        product["product_code"],
                        product["name"],
                        product["category"],
                        product["price"],
                        product["stock_quantity"]
                    )
                )

                product_id = cursor.lastrowid

                # Record opening stock only when quantity is greater than zero.
                if product["stock_quantity"] > 0:

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
                            'opening',
                            %s,
                            NULL,
                            %s,
                            %s
                        )
                        """,
                        (
                            product_id,
                            product["stock_quantity"],
                            "Opening stock from CSV import",
                            created_by
                        )
                    )

                imported_products.append({
                    "product_id": product_id,
                    "product_code": product["product_code"],
                    "name": product["name"],
                    "stock_quantity": product["stock_quantity"]
                })

        connection.commit()

        return {
            "success": True,
            "message": "Products imported successfully.",
            "total_imported": len(imported_products),
            "products": imported_products
        }

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
