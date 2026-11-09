from flask import Blueprint, jsonify, request
from decimal import Decimal
from datetime import date, datetime

from services.report_service import (
    get_customer_sales_summary,
    get_product_sales_summary,
    get_low_stock_report
)

from services.auth_decorators import login_required


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/api/reports"
)


def serialize_report_data(rows):
    """
    Convert Decimal and datetime values into JSON-compatible values.
    """

    serialized_rows = []

    for row in rows:
        serialized_row = {}

        for key, value in row.items():

            if isinstance(value, Decimal):
                serialized_row[key] = str(value)

            elif isinstance(value, (datetime, date)):
                serialized_row[key] = value.isoformat()

            else:
                serialized_row[key] = value

        serialized_rows.append(serialized_row)

    return serialized_rows


@reports_bp.route("/customer-sales", methods=["GET"])
@login_required
def customer_sales_report():

    try:
        rows = get_customer_sales_summary()

        return jsonify({
            "success": True,
            "count": len(rows),
            "report": serialize_report_data(rows)
        }), 200

    except Exception as error:
        print("CUSTOMER SALES REPORT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Unable to generate customer sales report"
        }), 500


@reports_bp.route("/product-sales", methods=["GET"])
@login_required
def product_sales_report():

    try:
        rows = get_product_sales_summary()

        return jsonify({
            "success": True,
            "count": len(rows),
            "report": serialize_report_data(rows)
        }), 200

    except Exception as error:
        print("PRODUCT SALES REPORT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Unable to generate product sales report"
        }), 500


@reports_bp.route("/low-stock", methods=["GET"])
@login_required
def low_stock_report():

    threshold_value = request.args.get("threshold", "5")

    try:
        threshold = int(threshold_value)

        if threshold < 0:
            return jsonify({
                "success": False,
                "message": "Threshold cannot be negative"
            }), 400

    except (ValueError, TypeError):
        return jsonify({
            "success": False,
            "message": "Threshold must be a valid non-negative integer"
        }), 400

    try:
        rows = get_low_stock_report(threshold)

        return jsonify({
            "success": True,
            "threshold": threshold,
            "count": len(rows),
            "report": serialize_report_data(rows)
        }), 200

    except Exception as error:
        print("LOW STOCK REPORT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "Unable to generate low stock report"
        }), 500
