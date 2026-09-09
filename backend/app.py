import os
from collections import Counter
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS


load_dotenv()


DATASET_PATH = Path(__file__).resolve().parent.parent / "Dataset" / "synthetic_energy_customer_sites.csv"


def _percentage(numerator, denominator):
    if not denominator:
        return 0

    return round((numerator / denominator) * 100, 1)


def _top_items(counter, limit=6):
    total = sum(counter.values())

    return [
        {
            "label": label,
            "count": count,
            "percentage": _percentage(count, total),
        }
        for label, count in counter.most_common(limit)
    ]


@lru_cache(maxsize=1)
def load_dashboard_summary():
    import csv

    business_partners = set()
    digital_business_partners = set()
    dob_business_partners = set()
    site_ids = set()
    active_business_partners = set()
    latest_site_rows = {}
    channel_counts = Counter()
    outcome_counts = Counter()
    commodity_counts = Counter()
    monthly_starts = Counter()
    total_episodes = 0
    closed_episodes = 0
    churn_episodes = 0
    renewal_episodes = 0
    leakage_episodes = 0

    with DATASET_PATH.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        for row in reader:
            total_episodes += 1

            business_partner_id = row["business_partner_id"]
            site_id = row["Site_id"]
            drop_type = row["drop_type"]
            start_date = row["site_contract_start_date"]

            business_partners.add(business_partner_id)
            site_ids.add(site_id)
            channel_counts[row["channel"]] += 1
            outcome_counts[drop_type] += 1
            commodity_counts[row["commodity_type"]] += 1
            monthly_starts[start_date[:7]] += 1

            if row["digital_status"] == "true":
                digital_business_partners.add(business_partner_id)

            if row["dob_status"] == "true":
                dob_business_partners.add(business_partner_id)

            if drop_type == "Active":
                active_business_partners.add(business_partner_id)
            else:
                closed_episodes += 1

            if drop_type == "Churn":
                churn_episodes += 1

            if drop_type in {"Auto Renewal", "Positive Renewal"}:
                renewal_episodes += 1

            if drop_type == "Leakage":
                leakage_episodes += 1

            previous_site_row = latest_site_rows.get(site_id)
            if previous_site_row is None or start_date > previous_site_row["site_contract_start_date"]:
                latest_site_rows[site_id] = row

    total_business_partners = len(business_partners)
    total_sites = len(site_ids)
    active_sites = sum(1 for row in latest_site_rows.values() if row["drop_type"] == "Active")
    last_12_months = sorted(monthly_starts)[-12:]

    return {
        "asOfDate": "2026-09-09",
        "dataset": {
            "name": DATASET_PATH.name,
            "grain": "One site-level contract episode per row",
            "businessPartners": total_business_partners,
            "sites": total_sites,
            "episodes": total_episodes,
        },
        "kpis": {
            "totalBusinessPartners": total_business_partners,
            "totalSites": total_sites,
            "totalContractEpisodes": total_episodes,
            "activeSites": active_sites,
            "activeBusinessPartners": len(active_business_partners),
            "activeSiteRate": _percentage(active_sites, total_sites),
            "churnRate": _percentage(churn_episodes, closed_episodes),
            "renewalRate": _percentage(renewal_episodes, closed_episodes),
            "leakageRate": _percentage(leakage_episodes, total_episodes),
            "digitalAdoptionRate": _percentage(len(digital_business_partners), total_business_partners),
            "averageSitesPerBusinessPartner": round(total_sites / total_business_partners, 2),
            "dobCaptureRate": _percentage(len(dob_business_partners), total_business_partners),
        },
        "mixes": {
            "channels": _top_items(channel_counts),
            "outcomes": _top_items(outcome_counts),
            "commodities": _top_items(commodity_counts),
        },
        "trends": {
            "monthlyStarts": [
                {"month": month, "episodes": monthly_starts[month]} for month in last_12_months
            ],
        },
    }


def create_app():
    app = Flask(__name__)

    cors_origins = os.getenv("CORS_ORIGINS", "*")
    origins = "*" if cors_origins == "*" else [origin.strip() for origin in cors_origins.split(",")]
    CORS(app, resources={r"/api/*": {"origins": origins}})

    @app.get("/api/health")
    def health():
        return jsonify({"status": "ok", "message": "Backend is running"})

    @app.get("/api/dashboard/summary")
    def dashboard_summary():
        if not DATASET_PATH.exists():
            return jsonify({"error": "Dashboard dataset not found"}), 404

        return jsonify(load_dashboard_summary())

    return app


app = create_app()


if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "5000"))
    debug = os.getenv("FLASK_DEBUG", "true").lower() == "true"

    app.run(host=host, port=port, debug=debug)
