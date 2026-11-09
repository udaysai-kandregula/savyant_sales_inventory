from decimal import Decimal, InvalidOperation

from flask import Blueprint, request, jsonify, session
from pymysql.err import IntegrityError

from services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product
)

from services.auth_decorators import (
    admin_required,
    login_required
)

from services.product_service import (
    create_product,
    get_all_products,
    get_product_by_id,
    update_product,
    set_product_status
)



products_bp = Blueprint(
    "products",
    __name__,
    url_prefix="/api/products"
)


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

    # Validate required text fields
    if not isinstance(product_code, str) or not product_code.strip():
        return jsonify({
            "success": False,
            "message": "Product code is required"
        }), 400

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
            "message": "Price must be a valid non-negative amount with up to 2 decimal places"
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

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not create product"
        }), 500


@products_bp.route("", methods=["GET"])
@login_required
def list_products():
    try:
        products = get_all_products()

        for product in products:
            if product["created_at"]:
                product["created_at"] = (
                    product["created_at"].isoformat()
                )

            product["price"] = str(product["price"])

        return jsonify({
            "success": True,
            "count": len(products),
            "products": products
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not retrieve products"
        }), 500


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

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not retrieve product"
        }), 500


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
            "message": "Price must be a valid non-negative amount with up to 2 decimal places"
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

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not update product"
        }), 500

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

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not update product status"
        }), 500

