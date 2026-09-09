import os

from dotenv import load_dotenv
from flask import Flask, jsonify, request
from flask_cors import CORS

from analytics.deep_dive_pages import DeepDivePagesService
from analytics.dashboard_summary import DashboardSummaryService
from data_sources.customer_sites import CustomerSitesSourceError, build_customer_sites_source


load_dotenv()


def create_app():
    app = Flask(__name__)
    customer_sites_source = build_customer_sites_source()
    dashboard_service = DashboardSummaryService(customer_sites_source)
    deep_dive_service = DeepDivePagesService(customer_sites_source)

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    origins = "*" if cors_origins == "*" else [origin.strip() for origin in cors_origins.split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Backend is running"})

    @app.get("/api/dashboard/summary")
    def dashboard_summary():
        if not dashboard_service.is_available():
            return jsonify({"error": "Dashboard data source is not available"}), 503

        try:
            return jsonify(
                dashboard_service.load_summary(
                    scope=request.args.get("scope", "current"),
                    channel=request.args.get("channel", ""),
                    commodity=request.args.get("commodity", ""),
                )
            )
        except CustomerSitesSourceError as error:
            return jsonify({"error": str(error)}), 503

    @app.get("/api/analysis/pages")
    def analysis_pages():
        return jsonify({"pages": deep_dive_service.available_pages()})

    @app.get("/api/analysis/<page_key>")
    def analysis_page(page_key):
        if not deep_dive_service.is_available():
            return jsonify({"error": "Analysis data source is not available"}), 503

        try:
            page_summary = deep_dive_service.get_page_summary(page_key)
        except CustomerSitesSourceError as error:
            return jsonify({"error": str(error)}), 503

        if page_summary is None:
            return jsonify({"error": "Analysis page not found"}), 404

        return jsonify(page_summary)

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
