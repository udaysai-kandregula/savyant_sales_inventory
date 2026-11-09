
from flask import Blueprint, request, jsonify, session

from services.auth_decorators import admin_required
from services.csv_import_service import import_products_from_csv


product_import_bp = Blueprint(
    "product_import",
    __name__,
    url_prefix="/api/products"
)


@product_import_bp.route("/import", methods=["POST"])
@admin_required
def import_products():

    if "file" not in request.files:
        return jsonify({
            "success": False,
            "message": "Please upload a CSV file using the 'file' field."
        }), 400

    uploaded_file = request.files["file"]

    if not uploaded_file.filename:
        return jsonify({
            "success": False,
            "message": "No file selected."
        }), 400

    if not uploaded_file.filename.lower().endswith(".csv"):
        return jsonify({
            "success": False,
            "message": "Only CSV files are allowed."
        }), 400

    try:
        file_content = uploaded_file.read()

        if not file_content:
            return jsonify({
                "success": False,
                "message": "Uploaded CSV file is empty."
            }), 400

        result = import_products_from_csv(
            file_content=file_content,
            created_by=session["user_id"]
        )

        return jsonify(result), 201

    except ValueError as error:

        details = error.args[0] if error.args else str(error)

        if isinstance(details, dict):
            return jsonify({
                "success": False,
                **details
            }), 400

        return jsonify({
            "success": False,
            "message": str(details)
        }), 400

    except Exception as error:

        print("CSV IMPORT ERROR:", repr(error))

        return jsonify({
            "success": False,
            "message": "CSV import failed. No products were imported."
        }), 500
