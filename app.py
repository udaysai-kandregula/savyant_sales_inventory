from flask import Flask, jsonify


def create_app():
    app = Flask(__name__)

    # Basic application configuration
    app.config["SECRET_KEY"] = "development-secret"

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