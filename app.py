
from flask import Flask, jsonify
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_wtf.csrf import CSRFError
from extensions import limiter
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")



# Import API blueprints
from routes.auth import auth_bp
from routes.customers import customers_bp
from routes.products import products_bp
from routes.orders import orders_bp
from routes.stock_movements import stock_movements_bp
from routes.reports import reports_bp
from routes.product_import import product_import_bp

# Import authorization decorators
from services.auth_decorators import (
    login_required,
    admin_required,
    sales_required
)


def create_app():

    # Create Flask application
    app = Flask(__name__)

    # Validate secret key
    secret_key = os.getenv("SECRET_KEY")

    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY is missing from environment configuration"
        )

    # Flask configuration
    app.config.update(
        SECRET_KEY=secret_key,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv(
            "SESSION_COOKIE_SECURE", "False"
        ).lower() == "true"
    )

    # Enable CSRF protection
    csrf = CSRFProtect(app)

    # Initialize rate limiter
    limiter.init_app(app)

    # Register API blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(stock_movements_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(product_import_bp)

    # Home route
    @app.route("/")
    def home():
        return "Savyant Sales and Inventory Management System"

    # Health check route
    @app.route("/health")
    def health():
        return jsonify({
            "status": "success",
            "message": "Application is running"
        })

    # Generate CSRF token
    @app.route("/api/csrf-token", methods=["GET"])
    def get_csrf_token():
        return jsonify({
            "success": True,
            "csrf_token": generate_csrf()
        })

    # Login-required test route
    @app.route("/api/test/login")
    @login_required
    def test_login_access():
        return jsonify({
            "success": True,
            "message": "Login access granted"
        })

    # Admin-only test route
    @app.route("/api/test/admin")
    @admin_required
    def test_admin_access():
        return jsonify({
            "success": True,
            "message": "Admin access granted"
        })

    # Sales-only test route
    @app.route("/api/test/sales")
    @sales_required
    def test_sales_access():
        return jsonify({
            "success": True,
            "message": "Sales access granted"
        })

        # Handle CSRF errors with JSON response

    # @app.errorhandler(CSRFError)
    # def handle_csrf_error(error):
    #     return jsonify({
    #         "success": False,
    #         "message": "CSRF token is missing or invalid"
    #     }), 400
    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        # print("CSRF HANDLER CALLED:", type(error), str(error))

        return jsonify({
            "success": False,
            "message": "CSRF token is missing or invalid"
        }), 400

    # Handle rate-limit errors with JSON response
    @app.errorhandler(429)
    def handle_rate_limit_error(error):
        return jsonify({
            "success": False,
            "message": "Too many login attempts. Please try again later."
        }), 429

    return app


if __name__ == "__main__":

    app = create_app()

    debug_mode = os.getenv(
        "FLASK_DEBUG", "False"
    ).lower() == "true"

    app.run(debug=debug_mode)
