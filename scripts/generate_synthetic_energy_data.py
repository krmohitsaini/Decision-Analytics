#!/usr/bin/env python3
"""Generate synthetic Alberta energy customer/site contract data."""

from __future__ import annotations

import argparse
import csv
import random
from collections import Counter
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable


AS_OF_DATE = date(2026, 9, 9)
SIGNUP_MIN_DATE = date(2023, 1, 1)
SIGNUP_MAX_DATE = AS_OF_DATE - timedelta(days=90)

COLUMNS = [
    "business_partner_id",
    "Site_id",
    "commodity_type",
    "site_contract_start_date",
    "site_contract_end_date",
    "sign_up_date",
    "zipcode",
    "AMB_status",
    "drop_type",
    "sales_type",
    "evergreen_status",
    "surge_status",
    "channel",
    "digital_status",
    "digital_start_date",
    "dob_status",
    "agent_name",
]

COMMODITIES = ("ELE", "GAS", "BOTH")
CHANNELS = (
    "IBTS",
    "Direct Sale",
    "Digital",
    "Telesales",
    "Broker",
    "Door-to-Door",
    "Retail Kiosk",
    "Field Sales",
    "Referral",
    "Partner",
)

NON_DIGITAL_CHANNELS = tuple(channel for channel in CHANNELS if channel != "Digital")

ALBERTA_FSAS = (
    "T0A",
    "T0B",
    "T0C",
    "T0E",
    "T0G",
    "T0H",
    "T0J",
    "T0K",
    "T0L",
    "T0M",
    "T1A",
    "T1B",
    "T1C",
    "T1H",
    "T1J",
    "T1K",
    "T1L",
    "T1M",
    "T1P",
    "T1R",
    "T1S",
    "T1V",
    "T1W",
    "T1X",
    "T1Y",
    "T2A",
    "T2B",
    "T2C",
    "T2E",
    "T2G",
    "T2H",
    "T2J",
    "T2K",
    "T2L",
    "T2M",
    "T2N",
    "T2P",
    "T2R",
    "T2S",
    "T2T",
    "T2V",
    "T2W",
    "T2X",
    "T2Y",
    "T2Z",
    "T3A",
    "T3B",
    "T3C",
    "T3E",
    "T3G",
    "T3H",
    "T3J",
    "T3K",
    "T3L",
    "T3M",
    "T3N",
    "T3P",
    "T3R",
    "T3S",
    "T4A",
    "T4B",
    "T4C",
    "T4E",
    "T4G",
    "T4H",
    "T4J",
    "T4L",
    "T4N",
    "T4P",
    "T4R",
    "T4S",
    "T4V",
    "T4X",
    "T5A",
    "T5B",
    "T5C",
    "T5E",
    "T5G",
    "T5H",
    "T5J",
    "T5K",
    "T5L",
    "T5M",
    "T5N",
    "T5P",
    "T5R",
    "T5S",
    "T5T",
    "T5V",
    "T5W",
    "T5X",
    "T5Y",
    "T5Z",
    "T6A",
    "T6B",
    "T6C",
    "T6E",
    "T6G",
    "T6H",
    "T6J",
    "T6K",
    "T6L",
    "T6M",
    "T6N",
    "T6P",
    "T6R",
    "T6S",
    "T6T",
    "T6V",
    "T6W",
    "T6X",
    "T7A",
    "T7E",
    "T7N",
    "T7P",
    "T7S",
    "T7V",
    "T7X",
    "T7Y",
    "T7Z",
    "T8A",
    "T8B",
    "T8C",
    "T8E",
    "T8H",
    "T8L",
    "T8N",
    "T8R",
    "T8S",
    "T8V",
    "T8W",
    "T8X",
    "T9A",
    "T9C",
    "T9E",
    "T9G",
    "T9H",
    "T9J",
    "T9K",
    "T9M",
    "T9N",
    "T9S",
    "T9V",
    "T9W",
    "T9X",
)

POSTAL_LETTERS = "ABCEGHJKLMNPRSTVWXYZ"
LEAKAGE_PROBABILITY = 0.031


@dataclass(frozen=True)
class PartnerProfile:
    business_partner_id: str
    sign_up_date: date
    zipcode: str
    digital_status: bool
    digital_start_date: date | None
    dob_status: bool


def weighted_choice(rng: random.Random, choices: Iterable[tuple[str, float]]) -> str:
    labels, weights = zip(*choices)
    return rng.choices(labels, weights=weights, k=1)[0]


def random_date(rng: random.Random, start: date, end: date) -> date:
    if end <= start:
        return start
    return start + timedelta(days=rng.randint(0, (end - start).days))


def random_alberta_postal_code(rng: random.Random) -> str:
    fsa = rng.choice(ALBERTA_FSAS)
    local_delivery_unit = (
        f"{rng.randint(0, 9)}"
        f"{rng.choice(POSTAL_LETTERS)}"
        f"{rng.randint(0, 9)}"
    )
    return f"{fsa} {local_delivery_unit}"


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def format_date(value: date | None) -> str:
    return value.isoformat() if value else ""


def make_partner_profile(rng: random.Random, index: int) -> PartnerProfile:
    sign_up_date = random_date(rng, SIGNUP_MIN_DATE, SIGNUP_MAX_DATE)
    digital_status = rng.random() < 0.30

    if digital_status:
        digital_delay = rng.choice(
            [
                rng.randint(1, 14),
                rng.randint(15, 90),
                rng.randint(91, 365),
                rng.randint(366, max(366, (AS_OF_DATE - sign_up_date).days)),
            ]
        )
        digital_start_date = min(sign_up_date + timedelta(days=digital_delay), AS_OF_DATE)
    else:
        digital_start_date = None

    return PartnerProfile(
        business_partner_id=f"BP{index:09d}",
        sign_up_date=sign_up_date,
        zipcode=random_alberta_postal_code(rng),
        digital_status=digital_status,
        digital_start_date=digital_start_date,
        dob_status=rng.random() < 0.72,
    )


def site_count_for_partner(rng: random.Random) -> int:
    return rng.choices(
        population=range(1, 11),
        weights=(5, 6, 7, 8, 10, 12, 14, 15, 13, 10),
        k=1,
    )[0]


def episode_count_for_site(rng: random.Random) -> int:
    return rng.choices(
        population=(1, 2, 3, 4, 5),
        weights=(38, 34, 18, 7, 3),
        k=1,
    )[0]


def choose_channel(rng: random.Random, digital_status: bool) -> str:
    if digital_status:
        return weighted_choice(
            rng,
            (
                ("Digital", 42),
                ("Telesales", 16),
                ("Direct Sale", 12),
                ("IBTS", 9),
                ("Referral", 8),
                ("Broker", 5),
                ("Partner", 4),
                ("Field Sales", 2),
                ("Retail Kiosk", 1),
                ("Door-to-Door", 1),
            ),
        )

    return weighted_choice(
        rng,
        (
            ("Telesales", 24),
            ("Direct Sale", 18),
            ("IBTS", 16),
            ("Broker", 11),
            ("Field Sales", 9),
            ("Partner", 8),
            ("Referral", 7),
            ("Retail Kiosk", 4),
            ("Door-to-Door", 3),
        ),
    )


def agent_for_channel(rng: random.Random, channel: str, agents: list[str]) -> str:
    if channel == "Digital":
        return ""
    return rng.choice(agents)


def first_start_date(rng: random.Random, sign_up_date: date) -> date:
    latest_start = max(sign_up_date + timedelta(days=1), AS_OF_DATE - timedelta(days=15))
    return random_date(rng, sign_up_date + timedelta(days=1), latest_start)


def next_sales_type(previous_drop_type: str | None) -> str:
    if previous_drop_type in {"Auto Renewal", "Positive Renewal", "TOS"}:
        return previous_drop_type
    return "Organic"


def non_active_drop_type(rng: random.Random) -> str:
    return weighted_choice(
        rng,
        (
            ("Churn", 44),
            ("Auto Renewal", 25),
            ("Positive Renewal", 21),
            ("TOS", 10),
        ),
    )


def rows_for_site(
    rng: random.Random,
    partner: PartnerProfile,
    site_id: str,
    agents: list[str],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    commodity = weighted_choice(rng, (("ELE", 42), ("GAS", 35), ("BOTH", 23)))
    planned_episodes = episode_count_for_site(rng)
    start_date = first_start_date(rng, partner.sign_up_date)
    previous_drop: str | None = None

    for episode_number in range(planned_episodes):
        remaining_days = (AS_OF_DATE - start_date).days
        if remaining_days < 0:
            break

        is_last_planned = episode_number == planned_episodes - 1
        forced_last = remaining_days <= 35
        sales_type = next_sales_type(previous_drop)

        if is_last_planned or forced_last:
            active = rng.random() < 0.66
            if active:
                drop_type = "Active"
                min_remaining_duration = max(1, remaining_days + rng.randint(30, 365))
                contract_end = start_date + timedelta(days=min_remaining_duration)
            else:
                drop_type = (
                    "Leakage"
                    if rng.random() < LEAKAGE_PROBABILITY
                    else non_active_drop_type(rng)
                )
                max_duration = max(0, remaining_days)
                if drop_type == "Leakage":
                    duration = rng.randint(0, min(5, max_duration))
                else:
                    duration = rng.randint(0, max_duration)
                contract_end = start_date + timedelta(days=duration)
        else:
            max_duration = max(0, remaining_days - 20 * (planned_episodes - episode_number - 1))
            drop_type = (
                "Leakage"
                if rng.random() < LEAKAGE_PROBABILITY
                else non_active_drop_type(rng)
            )
            if drop_type == "Leakage":
                duration = rng.randint(0, min(5, max_duration))
            else:
                min_duration = 30 if max_duration >= 30 else 0
                duration = rng.randint(min_duration, max_duration)
            contract_end = start_date + timedelta(days=duration)

        channel = choose_channel(rng, partner.digital_status)
        row = {
            "business_partner_id": partner.business_partner_id,
            "Site_id": site_id,
            "commodity_type": commodity,
            "site_contract_start_date": format_date(start_date),
            "site_contract_end_date": format_date(contract_end),
            "sign_up_date": format_date(partner.sign_up_date),
            "zipcode": partner.zipcode,
            "AMB_status": bool_text(rng.random() < 0.34),
            "drop_type": drop_type,
            "sales_type": sales_type,
            "evergreen_status": bool_text(rng.random() < 0.20),
            "surge_status": bool_text(rng.random() < 0.13),
            "channel": channel,
            "digital_status": bool_text(partner.digital_status),
            "digital_start_date": format_date(partner.digital_start_date),
            "dob_status": bool_text(partner.dob_status),
            "agent_name": agent_for_channel(rng, channel, agents),
        }
        rows.append(row)

        if drop_type == "Active":
            break

        previous_drop = drop_type
        gap_days = rng.randint(1, 120)
        start_date = contract_end + timedelta(days=gap_days)

    return rows


def generate_csv(output_path: Path, partner_count: int, seed: int) -> Counter:
    rng = random.Random(seed)
    agents = [f"Agent {index:03d}" for index in range(1, 101)]
    stats: Counter = Counter()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)
        writer.writeheader()

        for partner_index in range(1, partner_count + 1):
            partner = make_partner_profile(rng, partner_index)
            stats["business_partners"] += 1
            stats[f"digital_status={bool_text(partner.digital_status)}"] += 1

            for site_sequence in range(1, site_count_for_partner(rng) + 1):
                site_id = f"SITE{partner_index:09d}-{site_sequence:02d}"
                site_rows = rows_for_site(rng, partner, site_id, agents)
                if not site_rows:
                    continue

                stats["sites"] += 1
                for row in site_rows:
                    writer.writerow(row)
                    stats["rows"] += 1
                    stats[f"drop_type={row['drop_type']}"] += 1
                    stats[f"sales_type={row['sales_type']}"] += 1
                    stats[f"channel={row['channel']}"] += 1
                    stats[f"commodity_type={row['commodity_type']}"] += 1

    return stats


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate synthetic Alberta energy customer/site contract CSV data."
    )
    parser.add_argument(
        "--business-partners",
        type=int,
        default=100_000,
        help="Number of unique business_partner_id values to create.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("Dataset/synthetic_energy_customer_sites.csv"),
        help="CSV output path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20260909,
        help="Random seed for reproducible output.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    stats = generate_csv(args.output, args.business_partners, args.seed)

    print(f"CSV written: {args.output}")
    print(f"Business partners: {stats['business_partners']:,}")
    print(f"Sites: {stats['sites']:,}")
    print(f"Rows: {stats['rows']:,}")
    print(
        "Digital business partners: "
        f"{stats['digital_status=true']:,} "
        f"({stats['digital_status=true'] / stats['business_partners']:.1%})"
    )
    print(
        "Leakage rows: "
        f"{stats['drop_type=Leakage']:,} "
        f"({stats['drop_type=Leakage'] / stats['rows']:.1%})"
    )


if __name__ == "__main__":
    main()
