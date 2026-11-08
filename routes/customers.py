
from flask import Blueprint, request, jsonify

from services.customer_service import create_customer
from services.auth_decorators import admin_required
from services.customer_service import (
    create_customer,
    get_all_customers
)
from services.auth_decorators import admin_required, login_required
from services.customer_service import (
    create_customer,
    get_all_customers,
    get_customer_by_id
)

from services.customer_service import (
    create_customer,
    get_all_customers,
    get_customer_by_id,
    update_customer
)

from services.customer_service import (
    create_customer,
    get_all_customers,
    get_customer_by_id,
    update_customer,
    set_customer_status
)

customers_bp = Blueprint(
    "customers",
    __name__,
    url_prefix="/api/customers"
)


@customers_bp.route("", methods=["POST"])
@admin_required
def add_customer():

    data = request.get_json(silent=True) or {}

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "success": False,
            "message": "Customer name is required"
        }), 400

    email = data.get("email")
    mobile = data.get("mobile")
    city = data.get("city")

    for field, value in [
        ("email", email),
        ("mobile", mobile),
        ("city", city)
    ]:
        if value is not None and not isinstance(value, str):
            return jsonify({
                "success": False,
                "message": f"{field} must be text"
            }), 400

    try:
        result = create_customer(
            name=name.strip(),
            email=email.strip() if email else None,
            mobile=mobile.strip() if mobile else None,
            city=city.strip() if city else None
        )

        return jsonify(result), 201

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not create customer"
        }), 500




@customers_bp.route("", methods=["GET"])
@login_required
def list_customers():

    try:
        customers = get_all_customers()

        return jsonify({
            "success": True,
            "count": len(customers),
            "customers": [
                {
                    **customer,
                    "created_at": (
                        customer["created_at"].isoformat()
                        if customer["created_at"]
                        else None
                    )
                }
                for customer in customers
            ]
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not retrieve customers"
        }), 500


@customers_bp.route("/<int:customer_id>", methods=["GET"])
@login_required
def customer_details(customer_id):

    try:
        customer = get_customer_by_id(customer_id)

        if not customer:
            return jsonify({
                "success": False,
                "message": "Customer not found"
            }), 404

        customer["created_at"] = (
            customer["created_at"].isoformat()
            if customer["created_at"]
            else None
        )

        return jsonify({
            "success": True,
            "customer": customer
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not retrieve customer"
        }), 500



@customers_bp.route("/<int:customer_id>", methods=["PUT"])
@admin_required
def edit_customer(customer_id):

    data = request.get_json(silent=True) or {}

    name = data.get("name")

    if not isinstance(name, str) or not name.strip():
        return jsonify({
            "success": False,
            "message": "Customer name is required"
        }), 400

    email = data.get("email")
    mobile = data.get("mobile")
    city = data.get("city")

    for field, value in [
        ("email", email),
        ("mobile", mobile),
        ("city", city)
    ]:
        if value is not None and not isinstance(value, str):
            return jsonify({
                "success": False,
                "message": f"{field} must be text"
            }), 400

    try:
        updated = update_customer(
            customer_id,
            name.strip(),
            email.strip() if email else None,
            mobile.strip() if mobile else None,
            city.strip() if city else None
        )

        if not updated:
            return jsonify({
                "success": False,
                "message": "Customer not found"
            }), 404

        return jsonify({
            "success": True,
            "message": "Customer updated successfully"
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not update customer"
        }), 500


@customers_bp.route("/<int:customer_id>/status", methods=["PATCH"])
@admin_required
def change_customer_status(customer_id):
    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["active", "inactive"]:
        return jsonify({
            "success": False,
            "message": "Status must be active or inactive"
        }), 400

    try:
        updated = set_customer_status(customer_id, status)

        if not updated:
            return jsonify({
                "success": False,
                "message": "Customer not found"
            }), 404

        return jsonify({
            "success": True,
            "message": f"Customer {status} successfully"
        }), 200

    except Exception:
        return jsonify({
            "success": False,
            "message": "Could not update customer status"
        }), 500