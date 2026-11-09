
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify, session
from pymysql.err import IntegrityError

from services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    set_product_status,
    adjust_stock
)


from services.auth_decorators import (
    admin_required,
    login_required
)


products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


# --------------------------------------------------
# CREATE PRODUCT
# POST /api/products
# Admin only
# --------------------------------------------------

@products_bp.route("", methods=["POST"])
@admin_required
def add_product():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Valid JSON data is required"
        }), 400

    product_code = data.get("product_code")
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    stock_quantity = data.get("stock_quantity", 0)

    # Validate product code
    if not isinstance(product_code, str) or not product_code.strip():
        return jsonify({
            "success": False,
            "message": "Product code is required"
        }), 400

    # Validate product name
    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "success": False,
            "message": "Product name is required"
        }), 400

    # Validate category
    if category is not None and not isinstance(category, str):
        return jsonify({
            "success": False,
            "message": "Category must be text"
        }), 400

    # Validate price
    try:
        if isinstance(price, bool) or price is None:
            raise InvalidOperation

        price = Decimal(str(price))

        if not price.is_finite() or price < 0:
            raise InvalidOperation

        if price.as_tuple().exponent < -2:
            raise InvalidOperation

    except (InvalidOperation, ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": (
                "Price must be a valid non-negative amount "
                "with up to 2 decimal places"
            )
        }), 400

    # Validate stock quantity
    if (
        isinstance(stock_quantity, bool)
        or not isinstance(stock_quantity, int)
        or stock_quantity < 0
    ):
        return jsonify({
            "success": False,
            "message": "Stock quantity must be a non-negative whole number"
        }), 400

    try:
        result = create_product(
            product_code.strip(),
            name.strip(),
            category.strip() if category and category.strip() else None,
            price,
            stock_quantity,
            session["user_id"]
        )

        return jsonify(result), 201

    except IntegrityError:
        return jsonify({
            "success": False,
            "message": "Product code already exists or database constraint failed"
        }), 409

    except Exception as error:
        print("CREATE PRODUCT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Could not create product"
        }), 500


# --------------------------------------------------
# GET ALL PRODUCTS
# GET /api/products
# Login required
# --------------------------------------------------

@products_bp.route("", methods=["GET"])
@login_required
def list_products():

    try:
        products = get_all_products()

        for product in products:

            if product["created_at"]:
                product["created_at"] = product["created_at"].isoformat()

            product["price"] = str(product["price"])

        return jsonify({
            "success": True,
            "count": len(products),
            "products": products
        }), 200

    except Exception as error:
        print("GET PRODUCTS ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Could not retrieve products"
        }), 500


# --------------------------------------------------
# GET PRODUCT BY ID
# GET /api/products/<product_id>
# Login required
# --------------------------------------------------

@products_bp.route("/<int:product_id>", methods=["GET"])
@login_required
def get_product(product_id):

    try:
        product = get_product_by_id(product_id)

        if not product:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        if product["created_at"]:
            product["created_at"] = product["created_at"].isoformat()

        product["price"] = str(product["price"])

        return jsonify({
            "success": True,
            "product": product
        }), 200

    except Exception as error:
        print("GET PRODUCT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Could not retrieve product"
        }), 500


# --------------------------------------------------
# UPDATE PRODUCT
# PUT /api/products/<product_id>
# Admin only
# --------------------------------------------------

@products_bp.route("/<int:product_id>", methods=["PUT"])
@admin_required
def edit_product(product_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Valid JSON data is required"
        }), 400

    name = data.get("name")
    category = data.get("category")
    price = data.get("price")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "success": False,
            "message": "Product name is required"
        }), 400

    if category is not None and not isinstance(category, str):
        return jsonify({
            "success": False,
            "message": "Category must be text"
        }), 400

    try:
        if isinstance(price, bool) or price is None:
            raise InvalidOperation

        price = Decimal(str(price))

        if not price.is_finite() or price < 0:
            raise InvalidOperation

        if price.as_tuple().exponent < -2:
            raise InvalidOperation

    except (InvalidOperation, ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": (
                "Price must be a valid non-negative amount "
                "with up to 2 decimal places"
            )
        }), 400

    try:
        updated = update_product(
            product_id,
            name.strip(),
            category.strip() if category and category.strip() else None,
            price
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Product updated successfully"
        }), 200

    except Exception as error:
        print("UPDATE PRODUCT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Could not update product"
        }), 500


# --------------------------------------------------
# CHANGE PRODUCT STATUS
# PATCH /api/products/<product_id>/status
# Admin only
# --------------------------------------------------

@products_bp.route("/<int:product_id>/status", methods=["PATCH"])
@admin_required
def change_product_status(product_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Valid JSON data is required"
        }), 400

    status = data.get("status")

    if status not in ("active", "inactive"):
        return jsonify({
            "success": False,
            "message": "Status must be active or inactive"
        }), 400

    try:
        updated = set_product_status(product_id, status)

        if not updated:
            return jsonify({
                "success": False,
                "message": "Product not found"
            }), 404

        return jsonify({
            "success": True,
            "message": f"Product {status} successfully"
        }), 200

    except Exception as error:
        print("CHANGE PRODUCT STATUS ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Could not update product status"
        }), 500

@products_bp.route(
    "/<int:product_id>/stock-adjustment",
    methods=["POST"]
)
@admin_required
def stock_adjustment(product_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Request body must contain valid JSON"
        }), 400

    adjustment_type = data.get("adjustment_type")
    quantity = data.get("quantity")
    reason = data.get("reason")

    if adjustment_type not in ("increase", "decrease"):
        return jsonify({
            "success": False,
            "message": "Adjustment type must be increase or decrease"
        }), 400

    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
        return jsonify({
            "success": False,
            "message": "Quantity must be a positive whole number"
        }), 400

    if not isinstance(reason, str) or not reason.strip():
        return jsonify({
            "success": False,
            "message": "Adjustment reason is required"
        }), 400

    try:
        result = adjust_stock(
            product_id=product_id,
            adjustment_type=adjustment_type,
            quantity=quantity,
            reason=reason,
            created_by=session.get("user_id")
        )

        return jsonify(result), 200

    except ValueError as error:
        message = str(error)
        status_code = 404 if message == "Product not found" else 400

        return jsonify({
            "success": False,
            "message": message
        }), status_code

    except Exception as error:
        print("ADJUST STOCK ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Failed to adjust stock"
        }), 500

