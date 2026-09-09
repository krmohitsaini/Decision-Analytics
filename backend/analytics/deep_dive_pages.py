from collections import Counter, defaultdict
from functools import lru_cache
from statistics import median


PAGE_TITLES = {
    "retention": {
        "title": "Retention Deep Dive",
        "subtitle": "Contract outcomes, churn patterns, leakage, and site restart behavior.",
    },
    "commercial": {
        "title": "Commercial Performance",
        "subtitle": "Sales mix, renewal performance, channels, and contract start momentum.",
    },
    "portfolio": {
        "title": "Customer & Site Portfolio",
        "subtitle": "Customer footprint, site concentration, commodity mix, and Alberta FSA coverage.",
    },
    "products": {
        "title": "Product and Plan Adoption",
        "subtitle": "AMB, evergreen, and surge adoption with churn comparisons by plan flag.",
    },
    "digital": {
        "title": "Digital Engagement",
        "subtitle": "Portal adoption, activation timing, digital-channel penetration, and churn differences.",
    },
    "agents": {
        "title": "Agent and Channel Deep Dive",
        "subtitle": "Agent productivity and channel-specific churn, renewal, leakage, and active rates.",
    },
    "quality": {
        "title": "Data Quality",
        "subtitle": "Pipeline checks for dates, digital fields, agent assignment, and customer consistency.",
    },
}


def _date_ordinal(value):
    if not value or len(value) < 10:
        return None

    try:
        year = int(value[:4])
        month = int(value[5:7])
        day = int(value[8:10])
    except ValueError:
        return None

    if month < 1 or month > 12 or day < 1 or day > 31:
        return None

    if month <= 2:
        year -= 1
        month += 12

    return (
        365 * year
        + year // 4
        - year // 100
        + year // 400
        + (153 * (month - 3) + 2) // 5
        + day
    )


def _percentage(numerator, denominator):
    if not denominator:
        return 0

    return round((numerator / denominator) * 100, 1)


def _average(values):
    if not values:
        return 0

    return round(sum(values) / len(values), 1)


def _median(values):
    if not values:
        return 0

    return round(median(values), 1)


def _compact_int(value):
    return int(value or 0)


def _kpi(label, value, format_type="number", helper="", tone="blue"):
    return {
        "label": label,
        "value": value,
        "format": format_type,
        "helper": helper,
        "tone": tone,
    }


def _section(section_type, title, kicker, items=None, rows=None, columns=None, metric=None):
    return {
        "type": section_type,
        "title": title,
        "kicker": kicker,
        "metric": metric or "",
        "items": items or [],
        "rows": rows or [],
        "columns": columns or [],
    }


def _bar_items(counter, denominator=None, limit=8):
    total = denominator if denominator is not None else sum(counter.values())

    return [
        {
            "label": label,
            "value": count,
            "percentage": _percentage(count, total),
        }
        for label, count in counter.most_common(limit)
    ]


def _rate_rows(labels, totals, numerators, numerator_label, limit=None):
    rows = []

    for label in labels:
        total = totals[label]
        numerator = numerators[label]
        rows.append(
            {
                "label": label,
                "volume": total,
                numerator_label: numerator,
                "rate": _percentage(numerator, total),
            }
        )

    rows.sort(key=lambda row: (row["rate"], row["volume"]), reverse=True)

    return rows[:limit] if limit else rows


def _top_rate(counter_total, counter_numerator):
    rows = _rate_rows(counter_total.keys(), counter_total, counter_numerator, "count")
    return rows[0] if rows else {"label": "N/A", "rate": 0}


class DeepDivePagesService:
    def __init__(self, customer_sites_source):
        self.customer_sites_source = customer_sites_source

    def is_available(self):
        return self.customer_sites_source.is_available()

    def available_pages(self):
        return [
            {"key": key, **value}
            for key, value in PAGE_TITLES.items()
        ]

    @lru_cache(maxsize=1)
    def _build_context(self):
        total_rows = 0
        closed_rows = 0
        active_rows = 0
        churn_rows = 0
        renewal_rows = 0
        same_day_drops = 0
        leakage_within_five_days = 0
        tagged_leakage_rows = 0
        invalid_contract_dates = 0
        signup_after_start_rows = 0
        missing_digital_start_for_digital = 0
        digital_start_for_non_digital = 0
        digital_channel_rows_with_agent = 0
        non_digital_rows_missing_agent = 0
        non_alberta_rows = 0
        duration_days = []
        closed_duration_days = []
        digital_activation_lags = []
        business_partners = set()
        digital_customers = set()
        non_digital_customers = set()
        active_business_partners = set()
        active_digital_business_partners = set()
        digital_customers_with_digital_channel = set()
        customer_sites = defaultdict(set)
        customer_signup_dates = defaultdict(set)
        customer_digital_statuses = defaultdict(set)
        customer_postal_codes = defaultdict(set)
        customer_level_seen = set()
        signup_cohort_customers = defaultdict(set)
        signup_cohort_digital_customers = defaultdict(set)

        site_episode_counts = Counter()
        latest_site_rows = {}
        sales_type_counts = Counter()
        channel_counts = Counter()
        channel_closed = Counter()
        channel_churn = Counter()
        channel_renewal = Counter()
        channel_leakage = Counter()
        channel_active = Counter()
        commodity_counts = Counter()
        commodity_closed = Counter()
        commodity_churn = Counter()
        active_commodity_sites = defaultdict(set)
        drop_type_counts = Counter()
        closed_drop_type_counts = Counter()
        monthly_starts = Counter()
        monthly_closed = Counter()
        monthly_churn = Counter()
        monthly_renewal = Counter()
        duration_buckets = Counter()
        fsa_customers = defaultdict(set)
        active_fsa_sites = defaultdict(set)
        agent_sales = Counter()
        agent_closed = Counter()
        agent_churn = Counter()
        agent_renewal = Counter()
        agent_active_sites = defaultdict(set)

        amb_true = 0
        evergreen_true = 0
        surge_true = 0
        active_amb_true = 0
        active_evergreen_true = 0
        active_surge_true = 0
        plan_totals = {
            "AMB": Counter(),
            "Evergreen": Counter(),
            "Surge": Counter(),
        }
        plan_churn = {
            "AMB": Counter(),
            "Evergreen": Counter(),
            "Surge": Counter(),
        }
        digital_status_closed = Counter()
        digital_status_churn = Counter()

        for row in self.customer_sites_source.iter_contract_episodes():
            total_rows += 1

            business_partner_id = row["business_partner_id"]
            site_id = row["Site_id"]
            drop_type = row["drop_type"]
            channel = row["channel"]
            commodity = row["commodity_type"]
            sales_type = row["sales_type"]
            agent_name = row["agent_name"].strip()
            digital_status = row["digital_status"]
            zipcode = row["zipcode"]
            fsa = zipcode[:3]
            start_value = row["site_contract_start_date"]
            end_value = row["site_contract_end_date"]
            signup_value = row["sign_up_date"]
            digital_start_value = row["digital_start_date"]
            start_ordinal = _date_ordinal(start_value)
            end_ordinal = _date_ordinal(end_value)
            signup_ordinal = _date_ordinal(signup_value)

            business_partners.add(business_partner_id)
            customer_sites[business_partner_id].add(site_id)
            customer_signup_dates[business_partner_id].add(row["sign_up_date"])
            customer_digital_statuses[business_partner_id].add(digital_status)
            customer_postal_codes[business_partner_id].add(zipcode)
            fsa_customers[fsa].add(business_partner_id)
            site_episode_counts[site_id] += 1
            sales_type_counts[sales_type] += 1
            channel_counts[channel] += 1
            commodity_counts[commodity] += 1
            drop_type_counts[drop_type] += 1

            if start_value:
                monthly_starts[start_value[:7]] += 1

            if business_partner_id not in customer_level_seen:
                customer_level_seen.add(business_partner_id)
                signup_month = signup_value[:7]
                signup_cohort_customers[signup_month].add(business_partner_id)

                if digital_status == "true":
                    digital_customers.add(business_partner_id)
                    signup_cohort_digital_customers[signup_month].add(business_partner_id)

                    digital_start_ordinal = _date_ordinal(digital_start_value)
                    if signup_ordinal and digital_start_ordinal:
                        lag = digital_start_ordinal - signup_ordinal
                        if lag >= 0:
                            digital_activation_lags.append(lag)
                else:
                    non_digital_customers.add(business_partner_id)

            if digital_status == "true" and channel == "Digital":
                digital_customers_with_digital_channel.add(business_partner_id)

            if start_ordinal and end_ordinal:
                duration = end_ordinal - start_ordinal

                if duration < 0:
                    invalid_contract_dates += 1
                else:
                    duration_days.append(duration)

                    if duration == 0:
                        same_day_drops += 1

                    if 0 <= duration <= 5:
                        leakage_within_five_days += 1

                    if duration == 0:
                        duration_buckets["0 days"] += 1
                    elif duration <= 5:
                        duration_buckets["1-5 days"] += 1
                    elif duration <= 30:
                        duration_buckets["6-30 days"] += 1
                    elif duration <= 180:
                        duration_buckets["31-180 days"] += 1
                    elif duration <= 365:
                        duration_buckets["181-365 days"] += 1
                    else:
                        duration_buckets["366+ days"] += 1

            if signup_ordinal and start_ordinal:
                if signup_ordinal >= start_ordinal:
                    signup_after_start_rows += 1

            if digital_status == "true" and not row["digital_start_date"]:
                missing_digital_start_for_digital += 1

            if digital_status == "false" and row["digital_start_date"]:
                digital_start_for_non_digital += 1

            if channel == "Digital" and agent_name:
                digital_channel_rows_with_agent += 1

            if channel != "Digital" and not agent_name:
                non_digital_rows_missing_agent += 1

            if not zipcode.startswith("T"):
                non_alberta_rows += 1

            if row["AMB_status"] == "true":
                amb_true += 1

            if row["evergreen_status"] == "true":
                evergreen_true += 1

            if row["surge_status"] == "true":
                surge_true += 1

            if drop_type == "Active":
                active_rows += 1
                active_business_partners.add(business_partner_id)
                active_commodity_sites[commodity].add(site_id)
                active_fsa_sites[fsa].add(site_id)
                channel_active[channel] += 1

                if digital_status == "true":
                    active_digital_business_partners.add(business_partner_id)

                if row["AMB_status"] == "true":
                    active_amb_true += 1

                if row["evergreen_status"] == "true":
                    active_evergreen_true += 1

                if row["surge_status"] == "true":
                    active_surge_true += 1
            else:
                closed_rows += 1
                channel_closed[channel] += 1
                commodity_closed[commodity] += 1
                closed_drop_type_counts[drop_type] += 1
                digital_status_closed[digital_status] += 1

                if end_value:
                    monthly_closed[end_value[:7]] += 1

                if start_ordinal and end_ordinal and end_ordinal >= start_ordinal:
                    closed_duration_days.append(end_ordinal - start_ordinal)

                if agent_name:
                    agent_closed[agent_name] += 1

                for plan_name, column in (
                    ("AMB", "AMB_status"),
                    ("Evergreen", "evergreen_status"),
                    ("Surge", "surge_status"),
                ):
                    plan_totals[plan_name][row[column]] += 1

            if drop_type == "Churn":
                churn_rows += 1
                channel_churn[channel] += 1
                commodity_churn[commodity] += 1
                digital_status_churn[digital_status] += 1

                if end_value:
                    monthly_churn[end_value[:7]] += 1

                if agent_name:
                    agent_churn[agent_name] += 1

                for plan_name, column in (
                    ("AMB", "AMB_status"),
                    ("Evergreen", "evergreen_status"),
                    ("Surge", "surge_status"),
                ):
                    plan_churn[plan_name][row[column]] += 1

            if drop_type in {"Auto Renewal", "Positive Renewal"}:
                renewal_rows += 1
                channel_renewal[channel] += 1

                if end_value:
                    monthly_renewal[end_value[:7]] += 1

                if agent_name:
                    agent_renewal[agent_name] += 1

            if drop_type == "Leakage":
                tagged_leakage_rows += 1
                channel_leakage[channel] += 1

            if agent_name:
                agent_sales[agent_name] += 1

                if drop_type == "Active":
                    agent_active_sites[agent_name].add(site_id)

            previous_site_row = latest_site_rows.get(site_id)
            if (
                previous_site_row is None
                or row["site_contract_start_date"] > previous_site_row["site_contract_start_date"]
            ):
                latest_site_rows[site_id] = row

        total_business_partners = len(business_partners)
        total_sites = len(site_episode_counts)
        restarted_sites = sum(1 for count in site_episode_counts.values() if count > 1)
        multi_site_customers = sum(1 for sites in customer_sites.values() if len(sites) > 1)
        single_site_customers = sum(1 for sites in customer_sites.values() if len(sites) == 1)
        active_sites = sum(1 for row in latest_site_rows.values() if row["drop_type"] == "Active")
        active_business_partner_count = len(active_business_partners)

        context = {
            "total_rows": total_rows,
            "closed_rows": closed_rows,
            "active_rows": active_rows,
            "churn_rows": churn_rows,
            "renewal_rows": renewal_rows,
            "same_day_drops": same_day_drops,
            "leakage_within_five_days": leakage_within_five_days,
            "tagged_leakage_rows": tagged_leakage_rows,
            "invalid_contract_dates": invalid_contract_dates,
            "signup_after_start_rows": signup_after_start_rows,
            "missing_digital_start_for_digital": missing_digital_start_for_digital,
            "digital_start_for_non_digital": digital_start_for_non_digital,
            "digital_channel_rows_with_agent": digital_channel_rows_with_agent,
            "non_digital_rows_missing_agent": non_digital_rows_missing_agent,
            "non_alberta_rows": non_alberta_rows,
            "duration_days": duration_days,
            "closed_duration_days": closed_duration_days,
            "digital_activation_lags": digital_activation_lags,
            "total_business_partners": total_business_partners,
            "total_sites": total_sites,
            "active_sites": active_sites,
            "active_business_partner_count": active_business_partner_count,
            "digital_customers": len(digital_customers),
            "non_digital_customers": len(non_digital_customers),
            "active_digital_business_partners": len(active_digital_business_partners),
            "digital_customers_with_digital_channel": len(digital_customers_with_digital_channel),
            "single_site_customers": single_site_customers,
            "multi_site_customers": multi_site_customers,
            "restarted_sites": restarted_sites,
            "customer_site_count_distribution": Counter(len(sites) for sites in customer_sites.values()),
            "inconsistent_signup_customers": sum(
                1 for values in customer_signup_dates.values() if len(values) > 1
            ),
            "inconsistent_digital_status_customers": sum(
                1 for values in customer_digital_statuses.values() if len(values) > 1
            ),
            "inconsistent_postal_code_customers": sum(
                1 for values in customer_postal_codes.values() if len(values) > 1
            ),
            "sales_type_counts": sales_type_counts,
            "channel_counts": channel_counts,
            "channel_closed": channel_closed,
            "channel_churn": channel_churn,
            "channel_renewal": channel_renewal,
            "channel_leakage": channel_leakage,
            "channel_active": channel_active,
            "commodity_counts": commodity_counts,
            "commodity_closed": commodity_closed,
            "commodity_churn": commodity_churn,
            "active_commodity_counts": Counter(
                {label: len(sites) for label, sites in active_commodity_sites.items()}
            ),
            "drop_type_counts": drop_type_counts,
            "closed_drop_type_counts": closed_drop_type_counts,
            "monthly_starts": monthly_starts,
            "monthly_closed": monthly_closed,
            "monthly_churn": monthly_churn,
            "monthly_renewal": monthly_renewal,
            "duration_buckets": duration_buckets,
            "fsa_customer_counts": Counter({label: len(customers) for label, customers in fsa_customers.items()}),
            "active_fsa_site_counts": Counter({label: len(sites) for label, sites in active_fsa_sites.items()}),
            "agent_sales": agent_sales,
            "agent_closed": agent_closed,
            "agent_churn": agent_churn,
            "agent_renewal": agent_renewal,
            "agent_active_site_counts": Counter(
                {label: len(sites) for label, sites in agent_active_sites.items()}
            ),
            "amb_true": amb_true,
            "evergreen_true": evergreen_true,
            "surge_true": surge_true,
            "active_amb_true": active_amb_true,
            "active_evergreen_true": active_evergreen_true,
            "active_surge_true": active_surge_true,
            "plan_totals": plan_totals,
            "plan_churn": plan_churn,
            "digital_status_closed": digital_status_closed,
            "digital_status_churn": digital_status_churn,
            "signup_cohort_customers": Counter(
                {label: len(customers) for label, customers in signup_cohort_customers.items()}
            ),
            "signup_cohort_digital_customers": Counter(
                {label: len(customers) for label, customers in signup_cohort_digital_customers.items()}
            ),
        }

        return context

    def get_page_summary(self, page_key):
        page_key = page_key.strip().lower()

        if page_key not in PAGE_TITLES:
            return None

        context = self._build_context()

        builders = {
            "retention": self._retention_page,
            "commercial": self._commercial_page,
            "portfolio": self._portfolio_page,
            "products": self._products_page,
            "digital": self._digital_page,
            "agents": self._agents_page,
            "quality": self._quality_page,
        }

        return {
            "pageKey": page_key,
            **PAGE_TITLES[page_key],
            **builders[page_key](context),
        }

    def _retention_page(self, c):
        churn_by_channel_rows = _rate_rows(
            c["channel_closed"].keys(),
            c["channel_closed"],
            c["channel_churn"],
            "churned",
            limit=8,
        )
        churn_by_commodity_rows = _rate_rows(
            c["commodity_closed"].keys(),
            c["commodity_closed"],
            c["commodity_churn"],
            "churned",
        )

        return {
            "kpis": [
                _kpi("Closed episodes", c["closed_rows"], "number", "Non-active contract outcomes"),
                _kpi("Churn rate", _percentage(c["churn_rows"], c["closed_rows"]), "percent", "Share of closed episodes", "red"),
                _kpi("Same-day drop rate", _percentage(c["same_day_drops"], c["total_rows"]), "percent", "Start date equals end date", "amber"),
                _kpi("Leakage within 5 days", _percentage(c["leakage_within_five_days"], c["total_rows"]), "percent", "Date-derived early loss", "violet"),
                _kpi("Avg closed duration", _average(c["closed_duration_days"]), "days", "Closed episodes only", "green"),
                _kpi("Site restart rate", _percentage(c["restarted_sites"], c["total_sites"]), "percent", "Sites with more than one episode", "teal"),
            ],
            "sections": [
                _section("bars", "Closed Outcome Mix", "Outcomes", _bar_items(c["closed_drop_type_counts"], c["closed_rows"])),
                _section("table", "Churn by Channel", "Channel risk", rows=churn_by_channel_rows, columns=[
                    {"key": "label", "label": "Channel"},
                    {"key": "volume", "label": "Closed"},
                    {"key": "churned", "label": "Churned"},
                    {"key": "rate", "label": "Churn Rate", "format": "percent"},
                ]),
                _section("table", "Churn by Commodity", "Commodity risk", rows=churn_by_commodity_rows, columns=[
                    {"key": "label", "label": "Commodity"},
                    {"key": "volume", "label": "Closed"},
                    {"key": "churned", "label": "Churned"},
                    {"key": "rate", "label": "Churn Rate", "format": "percent"},
                ]),
                _section("bars", "Duration Buckets", "Contract duration", _bar_items(c["duration_buckets"], c["total_rows"])),
            ],
        }

    def _commercial_page(self, c):
        renewal_outcomes = Counter({
            label: c["closed_drop_type_counts"][label]
            for label in ("Auto Renewal", "Positive Renewal", "TOS", "Churn", "Leakage")
        })
        monthly_rows = []

        for month in sorted(c["monthly_closed"])[-12:]:
            monthly_rows.append(
                {
                    "label": month,
                    "volume": c["monthly_closed"][month],
                    "renewed": c["monthly_renewal"][month],
                    "rate": _percentage(c["monthly_renewal"][month], c["monthly_closed"][month]),
                }
            )

        return {
            "kpis": [
                _kpi("Organic sales", c["sales_type_counts"]["Organic"], "number", "Contract episodes tagged Organic"),
                _kpi("Organic share", _percentage(c["sales_type_counts"]["Organic"], c["total_rows"]), "percent", "Share of all episodes", "green"),
                _kpi("Auto renewal sales", c["sales_type_counts"]["Auto Renewal"], "number", "Sales type Auto Renewal", "blue"),
                _kpi("Positive renewal sales", c["sales_type_counts"]["Positive Renewal"], "number", "Sales type Positive Renewal", "teal"),
                _kpi("TOS sales", c["sales_type_counts"]["TOS"], "number", "Sales type TOS", "amber"),
                _kpi("Digital channel share", _percentage(c["channel_counts"]["Digital"], c["total_rows"]), "percent", "Sales through Digital channel", "violet"),
            ],
            "sections": [
                _section("bars", "Sales Mix by Type", "Sales", _bar_items(c["sales_type_counts"], c["total_rows"])),
                _section("bars", "Channel Sales Volume", "Channels", _bar_items(c["channel_counts"], c["total_rows"], limit=10)),
                _section("bars", "Renewal Outcome Mix", "Closed outcomes", _bar_items(renewal_outcomes, c["closed_rows"])),
                _section("table", "Monthly Renewal Rate", "Last 12 closed months", rows=monthly_rows, columns=[
                    {"key": "label", "label": "Month"},
                    {"key": "volume", "label": "Closed"},
                    {"key": "renewed", "label": "Renewed"},
                    {"key": "rate", "label": "Renewal Rate", "format": "percent"},
                ]),
            ],
        }

    def _portfolio_page(self, c):
        site_count_items = [
            {
                "label": f"{label} site" if label == 1 else f"{label} sites",
                "value": count,
                "percentage": _percentage(count, c["total_business_partners"]),
            }
            for label, count in sorted(c["customer_site_count_distribution"].items())[:10]
        ]

        return {
            "kpis": [
                _kpi("Single-site customers", c["single_site_customers"], "number", "Exactly one distinct site"),
                _kpi("Multi-site customers", c["multi_site_customers"], "number", "More than one distinct site", "green"),
                _kpi("Multi-site rate", _percentage(c["multi_site_customers"], c["total_business_partners"]), "percent", "Share of business partners", "teal"),
                _kpi(
                    "Active sites per active BP",
                    round(c["active_sites"] / c["active_business_partner_count"], 2)
                    if c["active_business_partner_count"]
                    else 0,
                    "decimal",
                    "Current active footprint",
                    "blue",
                ),
                _kpi("Restarted sites", c["restarted_sites"], "number", "Sites with repeat episodes", "amber"),
                _kpi("Avg episodes per site", round(c["total_rows"] / c["total_sites"], 2), "decimal", "Episode history depth", "violet"),
            ],
            "sections": [
                _section("bars", "Customers by Site Count", "Customer footprint", site_count_items),
                _section("bars", "Commodity Mix", "All episodes", _bar_items(c["commodity_counts"], c["total_rows"])),
                _section("bars", "Active Commodity Mix", "Active sites", _bar_items(c["active_commodity_counts"], c["active_sites"])),
                _section("bars", "Top Alberta FSAs", "Customers by postal FSA", _bar_items(c["fsa_customer_counts"], c["total_business_partners"], limit=8)),
            ],
        }

    def _products_page(self, c):
        plan_rows = []

        for plan_name in ("AMB", "Evergreen", "Surge"):
            for status in ("true", "false"):
                total = c["plan_totals"][plan_name][status]
                plan_rows.append(
                    {
                        "label": f"{plan_name}: {status}",
                        "volume": total,
                        "churned": c["plan_churn"][plan_name][status],
                        "rate": _percentage(c["plan_churn"][plan_name][status], total),
                    }
                )

        plan_rows.sort(key=lambda row: row["label"])

        return {
            "kpis": [
                _kpi("AMB enrollment", _percentage(c["amb_true"], c["total_rows"]), "percent", "All contract episodes"),
                _kpi("Active AMB", _percentage(c["active_amb_true"], c["active_rows"]), "percent", "Active rows only", "green"),
                _kpi("Evergreen adoption", _percentage(c["evergreen_true"], c["total_rows"]), "percent", "All contract episodes", "teal"),
                _kpi("Active evergreen", _percentage(c["active_evergreen_true"], c["active_rows"]), "percent", "Active rows only", "blue"),
                _kpi("Surge adoption", _percentage(c["surge_true"], c["total_rows"]), "percent", "All contract episodes", "amber"),
                _kpi("Active surge", _percentage(c["active_surge_true"], c["active_rows"]), "percent", "Active rows only", "violet"),
            ],
            "sections": [
                _section("table", "Churn by Plan Status", "Product retention", rows=plan_rows, columns=[
                    {"key": "label", "label": "Plan Status"},
                    {"key": "volume", "label": "Closed"},
                    {"key": "churned", "label": "Churned"},
                    {"key": "rate", "label": "Churn Rate", "format": "percent"},
                ]),
                _section("bars", "Product Adoption", "All episodes", Counter({
                    "AMB": c["amb_true"],
                    "Evergreen": c["evergreen_true"],
                    "Surge": c["surge_true"],
                }) and _bar_items(Counter({
                    "AMB": c["amb_true"],
                    "Evergreen": c["evergreen_true"],
                    "Surge": c["surge_true"],
                }), c["total_rows"])),
            ],
        }

    def _digital_page(self, c):
        cohort_rows = []

        for month in sorted(c["signup_cohort_customers"])[-12:]:
            total = c["signup_cohort_customers"][month]
            digital = c["signup_cohort_digital_customers"][month]
            cohort_rows.append(
                {
                    "label": month,
                    "volume": total,
                    "digital": digital,
                    "rate": _percentage(digital, total),
                }
            )

        churn_rows = _rate_rows(
            ("true", "false"),
            c["digital_status_closed"],
            c["digital_status_churn"],
            "churned",
        )

        return {
            "kpis": [
                _kpi("Digital customers", c["digital_customers"], "number", "Distinct business partners"),
                _kpi("Non-digital customers", c["non_digital_customers"], "number", "Portal opportunity pool", "amber"),
                _kpi("Digital adoption", _percentage(c["digital_customers"], c["total_business_partners"]), "percent", "Customer-level rate", "green"),
                _kpi("Avg activation lag", _average(c["digital_activation_lags"]), "days", "Signup to portal start", "blue"),
                _kpi("Median activation lag", _median(c["digital_activation_lags"]), "days", "Signup to portal start", "teal"),
                _kpi("Digital channel penetration", _percentage(c["digital_customers_with_digital_channel"], c["digital_customers"]), "percent", "Digital customers buying digitally", "violet"),
            ],
            "sections": [
                _section("table", "Digital Adoption by Signup Cohort", "Latest 12 signup months", rows=cohort_rows, columns=[
                    {"key": "label", "label": "Signup Month"},
                    {"key": "volume", "label": "Customers"},
                    {"key": "digital", "label": "Digital"},
                    {"key": "rate", "label": "Adoption Rate", "format": "percent"},
                ]),
                _section("table", "Churn by Digital Status", "Closed episodes", rows=churn_rows, columns=[
                    {"key": "label", "label": "Digital Status"},
                    {"key": "volume", "label": "Closed"},
                    {"key": "churned", "label": "Churned"},
                    {"key": "rate", "label": "Churn Rate", "format": "percent"},
                ]),
                _section("bars", "Digital Customer Split", "Business partners", _bar_items(Counter({
                    "Digital": c["digital_customers"],
                    "Non-digital": c["non_digital_customers"],
                }), c["total_business_partners"])),
            ],
        }

    def _agents_page(self, c):
        agent_performance = []

        for agent_name in c["agent_sales"]:
            closed = c["agent_closed"][agent_name]
            agent_performance.append(
                {
                    "label": agent_name,
                    "volume": c["agent_sales"][agent_name],
                    "activeSites": c["agent_active_site_counts"][agent_name],
                    "churnRate": _percentage(c["agent_churn"][agent_name], closed),
                    "renewalRate": _percentage(c["agent_renewal"][agent_name], closed),
                }
            )

        agent_performance.sort(key=lambda row: row["volume"], reverse=True)
        channel_performance = []

        for channel in c["channel_counts"]:
            total = c["channel_counts"][channel]
            closed = c["channel_closed"][channel]
            channel_performance.append(
                {
                    "label": channel,
                    "volume": total,
                    "churnRate": _percentage(c["channel_churn"][channel], closed),
                    "renewalRate": _percentage(c["channel_renewal"][channel], closed),
                    "leakageRate": _percentage(c["channel_leakage"][channel], total),
                    "activeRate": _percentage(c["channel_active"][channel], total),
                }
            )

        channel_performance.sort(key=lambda row: row["volume"], reverse=True)
        highest_churn_channel = _top_rate(c["channel_closed"], c["channel_churn"])

        return {
            "kpis": [
                _kpi("Agent-handled episodes", sum(c["agent_sales"].values()), "number", "Excludes blank digital agents"),
                _kpi("Active agents", len(c["agent_sales"]), "number", "Agents with assigned rows", "green"),
                _kpi("Top agent volume", c["agent_sales"].most_common(1)[0][1], "number", c["agent_sales"].most_common(1)[0][0], "blue"),
                _kpi("Highest channel churn", highest_churn_channel["rate"], "percent", highest_churn_channel["label"], "red"),
                _kpi("Digital channel share", _percentage(c["channel_counts"]["Digital"], c["total_rows"]), "percent", "Rows without agent assignment", "violet"),
                _kpi("Channel count", len(c["channel_counts"]), "number", "Sales channels represented", "teal"),
            ],
            "sections": [
                _section("bars", "Agent Sales Volume", "Top agents", _bar_items(c["agent_sales"], sum(c["agent_sales"].values()), limit=8)),
                _section("table", "Agent Performance", "Top 10 by volume", rows=agent_performance[:10], columns=[
                    {"key": "label", "label": "Agent"},
                    {"key": "volume", "label": "Episodes"},
                    {"key": "activeSites", "label": "Active Sites"},
                    {"key": "churnRate", "label": "Churn", "format": "percent"},
                    {"key": "renewalRate", "label": "Renewal", "format": "percent"},
                ]),
                _section("table", "Channel Performance", "All channels", rows=channel_performance, columns=[
                    {"key": "label", "label": "Channel"},
                    {"key": "volume", "label": "Episodes"},
                    {"key": "activeRate", "label": "Active", "format": "percent"},
                    {"key": "churnRate", "label": "Churn", "format": "percent"},
                    {"key": "renewalRate", "label": "Renewal", "format": "percent"},
                    {"key": "leakageRate", "label": "Leakage", "format": "percent"},
                ]),
            ],
        }

    def _quality_page(self, c):
        quality_items = Counter({
            "Missing digital start for digital customers": c["missing_digital_start_for_digital"],
            "Digital start present for non-digital customers": c["digital_start_for_non_digital"],
            "Invalid contract date rows": c["invalid_contract_dates"],
            "Signup after contract start rows": c["signup_after_start_rows"],
            "Digital channel rows with agent": c["digital_channel_rows_with_agent"],
            "Non-digital rows missing agent": c["non_digital_rows_missing_agent"],
            "Non-Alberta postal code rows": c["non_alberta_rows"],
        })
        consistency_rows = [
            {"label": "Signup date", "volume": c["inconsistent_signup_customers"]},
            {"label": "Digital status", "volume": c["inconsistent_digital_status_customers"]},
            {"label": "Postal code", "volume": c["inconsistent_postal_code_customers"]},
        ]
        total_issues = sum(quality_items.values()) + sum(row["volume"] for row in consistency_rows)

        return {
            "kpis": [
                _kpi("Total issue flags", total_issues, "number", "Rows and customer-level consistency checks", "amber"),
                _kpi("Invalid contract dates", c["invalid_contract_dates"], "number", "Start date after end date", "red"),
                _kpi("Signup timing issues", c["signup_after_start_rows"], "number", "Signup not before contract start", "violet"),
                _kpi("Digital field issues", c["missing_digital_start_for_digital"] + c["digital_start_for_non_digital"], "number", "Digital status/date mismatches", "blue"),
                _kpi("Agent assignment issues", c["digital_channel_rows_with_agent"] + c["non_digital_rows_missing_agent"], "number", "Channel-agent rule checks", "teal"),
                _kpi("Non-Alberta rows", c["non_alberta_rows"], "number", "Postal code outside T prefix", "green"),
            ],
            "sections": [
                _section("bars", "Row-Level Quality Checks", "Issue flags", _bar_items(quality_items, c["total_rows"])),
                _section("table", "Customer-Level Consistency", "Distinct business partners", rows=consistency_rows, columns=[
                    {"key": "label", "label": "Field"},
                    {"key": "volume", "label": "Inconsistent Customers"},
                ]),
            ],
        }
