from flask import Flask, jsonify
import os
from dotenv import load_dotenv


from routes.auth import auth_bp
from routes.customers import customers_bp

from services.auth_decorators import (
    login_required,
    admin_required,
    sales_required
)

from routes.products import products_bp
from routes.orders import orders_bp
from routes.stock_movements import stock_movements_bp


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"


    # Register authentication APIs
    app.register_blueprint(auth_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(orders_bp)
    app.register_blueprint(stock_movements_bp)


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
    
    # login routing 
    @app.route("/api/test/login")
    @login_required
    def test_login_access():
        return jsonify({
            "success": True,
            "message": "Login access granted"
        })

    #admin routing
    @app.route("/api/test/admin")
    @admin_required
    def test_admin_access():
        return jsonify({
            "success": True,
            "message": "Admin access granted"
        })

    #sales routing
    @app.route("/api/test/sales")
    @sales_required
    def test_sales_access():
        return jsonify({
            "success": True,
            "message": "Sales access granted"
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)