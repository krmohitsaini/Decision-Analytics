import os

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS


load_dotenv()


def create_app():
    app = Flask(__name__)

    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173")
    CORS(app, resources={r"/api/*": {"origins": [origin.strip() for origin in cors_origins.split(",")]}})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Backend is running"})

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
