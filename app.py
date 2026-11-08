from flask import Flask, jsonify
import os
from dotenv import load_dotenv
from routes.auth import auth_bp



def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Register authentication APIs
    app.register_blueprint(auth_bp)

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

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)