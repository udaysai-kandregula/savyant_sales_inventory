
from flask import Blueprint, request, jsonify

from services.stock_service import (
    get_stock_movement_history,
    VALID_MOVEMENT_TYPES
)

from services.auth_decorators import login_required


stock_movements_bp = Blueprint(
    "stock_movements",
    __name__,
    url_prefix="/api/stock-movements"
)


@stock_movements_bp.route("", methods=["GET"])
@login_required
def list_stock_movements():

    # Read query parameters
    product_id_value = request.args.get("product_id")
    movement_type = request.args.get("movement_type")
    limit_value = request.args.get("limit", "100")

    # Validate product ID
    product_id = None

    if product_id_value is not None:
        try:
            product_id = int(product_id_value)

            if product_id <= 0:
                raise ValueError

        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "message": "Product ID must be a positive integer"
            }), 400

    # Validate movement type
    if movement_type is not None:
        if movement_type not in VALID_MOVEMENT_TYPES:
            return jsonify({
                "success": False,
                "message": "Invalid movement type"
            }), 400

    # Validate limit
    try:
        limit = int(limit_value)

        if limit < 1 or limit > 500:
            raise ValueError

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Limit must be between 1 and 500"
        }), 400

    try:

        movements = get_stock_movement_history(
            product_id=product_id,
            movement_type=movement_type,
            limit=limit
        )

        return jsonify({
            "success": True,
            "count": len(movements),
            "movements": movements
        }), 200

    except ValueError as error:

        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:

        print(
            "STOCK MOVEMENT HISTORY ERROR:",
            repr(error)
        )

        return jsonify({
            "success": False,
            "message": "Unable to retrieve stock movement history"
        }), 500
