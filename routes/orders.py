
from flask import Blueprint, request, jsonify, session

from services.order_service import (
    create_draft_order,
    get_order_by_id,
    confirm_order,
    cancel_order
)

from services.auth_decorators import login_required

orders_bp = Blueprint("orders", __name__, url_prefix="/api/orders")


# Create a draft order
@orders_bp.route("", methods=["POST"])
@login_required
def create_order():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Invalid JSON request"
        }), 400

    try:
        result = create_draft_order(
            customer_id=data.get("customer_id"),
            items=data.get("items"),
            discount_percentage=data.get("discount_percentage", 0),
            created_by=session["user_id"]
        )

        return jsonify(result), 201

    except ValueError as error:
        return jsonify({
            "success": False,
            "message": str(error)
        }), 400

    except Exception as error:
        print("CREATE ORDER ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to create order"
        }), 500


# Get order details
@orders_bp.route("/<int:order_id>", methods=["GET"])
@login_required
def get_order(order_id):

    order = get_order_by_id(order_id)

    if not order:
        return jsonify({
            "success": False,
            "message": "Order not found"
        }), 404

    return jsonify({
        "success": True,
        "order": order
    }), 200


# Confirm a draft order
@orders_bp.route("/<int:order_id>/confirm", methods=["POST"])
@login_required
def confirm_sales_order(order_id):

    try:
        result = confirm_order(
            order_id=order_id,
            confirmed_by=session["user_id"]
        )

        return jsonify(result), 200

    except ValueError as error:
        message = str(error)
        status_code = 404 if message == "Order not found" else 400

        return jsonify({
            "success": False,
            "message": message
        }), status_code

    except Exception as error:
        print("CONFIRM ORDER ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to confirm order"
        }), 500


# Cancel an order
@orders_bp.route("/<int:order_id>/cancel", methods=["POST"])
@login_required
def cancel_sales_order(order_id):

    try:
        result = cancel_order(
            order_id=order_id,
            cancelled_by=session["user_id"]
        )

        return jsonify(result), 200

    except ValueError as error:
        message = str(error)
        status_code = 404 if message == "Order not found" else 400

        return jsonify({
            "success": False,
            "message": message
        }), status_code

    except Exception as error:
        print("CANCEL ORDER ERROR:", repr(error))
        return jsonify({
            "success": False,
            "message": "Unable to cancel order"
        }), 500
