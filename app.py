from flask import Flask, jsonify
import os
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)

    # Basic application configuration
    load_dotenv()
    app.confing["SECRET_"]  = os.getenv("SECRET_KEY")

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