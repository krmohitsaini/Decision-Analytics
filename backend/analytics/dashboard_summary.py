from collections import Counter
from functools import lru_cache


DEFAULT_SCOPE = "current"
VALID_SCOPES = {"current", "all"}


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


def _sort_options(counter):
    return [
        {"label": label, "count": counter[label]}
        for label in sorted(counter)
    ]


def _normalize_scope(scope):
    normalized_scope = (scope or DEFAULT_SCOPE).strip().lower()

    if normalized_scope not in VALID_SCOPES:
        return DEFAULT_SCOPE

    return normalized_scope


def _normalize_value(value):
    return (value or "").strip()


def _row_matches_filters(row, channel, commodity):
    if channel and row["channel"] != channel:
        return False

    if commodity and row["commodity_type"] != commodity:
        return False

    return True


class DashboardSummaryService:
    def __init__(self, customer_sites_source):
        self.customer_sites_source = customer_sites_source

    def is_available(self):
        return self.customer_sites_source.is_available()

    @lru_cache(maxsize=64)
    def load_summary(self, scope=DEFAULT_SCOPE, channel="", commodity=""):
        scope = _normalize_scope(scope)
        channel = _normalize_value(channel)
        commodity = _normalize_value(commodity)
        latest_site_rows = {}
        selected_rows = []
        available_channels = Counter()
        available_commodities = Counter()

        for row in self.customer_sites_source.iter_contract_episodes():
            available_channels[row["channel"]] += 1
            available_commodities[row["commodity_type"]] += 1

            site_id = row["Site_id"]
            start_date = row["site_contract_start_date"]
            previous_site_row = latest_site_rows.get(site_id)
            if previous_site_row is None or start_date > previous_site_row["site_contract_start_date"]:
                latest_site_rows[site_id] = row

            if scope == "all" and _row_matches_filters(row, channel, commodity):
                selected_rows.append(row)

        if scope == "current":
            selected_rows = [
                row
                for row in latest_site_rows.values()
                if _row_matches_filters(row, channel, commodity)
            ]

        return self._build_summary(
            selected_rows=selected_rows,
            latest_site_rows=latest_site_rows,
            available_channels=available_channels,
            available_commodities=available_commodities,
            scope=scope,
            channel=channel,
            commodity=commodity,
        )

    def _build_summary(
        self,
        selected_rows,
        latest_site_rows,
        available_channels,
        available_commodities,
        scope,
        channel,
        commodity,
    ):
        business_partners = set()
        digital_business_partners = set()
        dob_business_partners = set()
        site_ids = set()
        active_business_partners = set()
        channel_counts = Counter()
        outcome_counts = Counter()
        commodity_counts = Counter()
        monthly_starts = Counter()
        total_episodes = 0
        closed_episodes = 0
        churn_episodes = 0
        renewal_episodes = 0
        leakage_episodes = 0

        for row in selected_rows:
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

        total_business_partners = len(business_partners)
        total_sites = len(site_ids)
        active_sites = sum(
            1
            for row in latest_site_rows.values()
            if row["drop_type"] == "Active" and _row_matches_filters(row, channel, commodity)
        )
        last_12_months = sorted(monthly_starts)[-12:]

        return {
            "asOfDate": "2026-09-09",
            "dataset": {
                "name": self.customer_sites_source.name,
                "sourceType": self.customer_sites_source.source_type,
                "grain": self.customer_sites_source.grain,
                "businessPartners": total_business_partners,
                "sites": total_sites,
                "episodes": total_episodes,
            },
            "filters": {
                "scope": scope,
                "channel": channel,
                "commodity": commodity,
                "availableScopes": [
                    {"label": "Current portfolio", "value": "current"},
                    {"label": "All contract episodes", "value": "all"},
                ],
                "channels": _sort_options(available_channels),
                "commodities": _sort_options(available_commodities),
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
                "averageSitesPerBusinessPartner": (
                    round(total_sites / total_business_partners, 2)
                    if total_business_partners
                    else 0
                ),
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
