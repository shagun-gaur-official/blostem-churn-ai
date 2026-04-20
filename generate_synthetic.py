"""
Blostem ChurnSense AI — Synthetic Data Generator
Generates realistic Fixed Deposit customer data for model training.
"""

import random
import json
import csv
from datetime import datetime, timedelta
import argparse
import math
import os

random.seed(42)

PLATFORMS = ["upstox", "jupiter", "mobikwik", "zerodha", "niyo", "freo", "fi_money", "smallcase"]
BANKS = ["suryoday_sfb", "utkarsh_sfb", "jana_sfb", "equitas_sfb", "shivalik_sfb", "esaf_sfb"]
STATES = ["UP", "MH", "DL", "KA", "TN", "WB", "GJ", "RJ", "MP", "HR"]

def noise(base, pct=0.15):
    return base * (1 + random.uniform(-pct, pct))

def generate_customer(customer_id: int, churn_bias: float = None) -> dict:
    """Generate a single FD customer record with realistic behavioral signals."""

    # Segment assignment (drives correlated features)
    segment_roll = random.random()
    if segment_roll < 0.18:
        segment = "champion"
    elif segment_roll < 0.42:
        segment = "engaged"
    elif segment_roll < 0.73:
        segment = "passive"
    elif segment_roll < 0.92:
        segment = "at_risk"
    else:
        segment = "churner"

    # Segment-driven base features
    base = {
        "champion":  {"renewal_count": (4, 8),  "login_gap": (1, 10),  "fd_amount": (200000, 1000000), "tenure": (18, 36)},
        "engaged":   {"renewal_count": (2, 5),  "login_gap": (3, 18),  "fd_amount": (75000, 300000),  "tenure": (12, 24)},
        "passive":   {"renewal_count": (1, 3),  "login_gap": (15, 35), "fd_amount": (25000, 100000),  "tenure": (6, 18)},
        "at_risk":   {"renewal_count": (0, 2),  "login_gap": (21, 50), "fd_amount": (10000, 75000),   "tenure": (3, 12)},
        "churner":   {"renewal_count": (0, 1),  "login_gap": (30, 90), "fd_amount": (10000, 50000),   "tenure": (3, 9)},
    }[segment]

    tenure_months = random.randint(*base["tenure"])
    fd_amount = round(noise(random.randint(*base["fd_amount"]), 0.2) / 1000) * 1000
    renewal_count = random.randint(*base["renewal_count"])
    days_since_login = random.randint(*base["login_gap"])

    # Interest rate sensitivity: churners are more sensitive
    interest_rate = round(random.uniform(7.0, 9.5), 2)
    rate_sensitivity = {"champion": 0.1, "engaged": 0.3, "passive": 0.5, "at_risk": 0.7, "churner": 0.9}[segment]
    rate_sensitivity = min(1.0, noise(rate_sensitivity, 0.2))

    # Support tickets: at-risk and churners raise more issues
    support_tickets = {
        "champion": random.randint(0, 1), "engaged": random.randint(0, 2),
        "passive": random.randint(0, 2), "at_risk": random.randint(1, 4), "churner": random.randint(2, 6)
    }[segment]

    # App engagement score (0–100)
    engagement_base = {"champion": 80, "engaged": 65, "passive": 40, "at_risk": 25, "churner": 15}[segment]
    app_engagement_score = int(max(0, min(100, noise(engagement_base, 0.25))))

    # KYC completeness
    kyc_complete = random.random() > (0.05 if segment in ["champion", "engaged"] else 0.2)

    # Days to FD maturity
    days_to_maturity = random.randint(-5, 45)  # negative = already matured

    # Platform
    platform = random.choice(PLATFORMS)
    bank = random.choice(BANKS)
    state = random.choice(STATES)

    # Did customer open competing FD elsewhere?
    checked_competitor = segment in ["at_risk", "churner"] and random.random() > 0.5

    # Nominee added? (loyalty signal)
    nominee_added = segment in ["champion", "engaged"] and random.random() > 0.3

    # Churn label: deterministic from segment + noise
    churn_prob_map = {"champion": 0.05, "engaged": 0.15, "passive": 0.35, "at_risk": 0.70, "churner": 0.92}
    base_churn_prob = churn_prob_map[segment]
    # Modulate by login gap and days_to_maturity
    if days_since_login > 30 and days_to_maturity < 20:
        base_churn_prob = min(1.0, base_churn_prob * 1.3)
    if support_tickets >= 3:
        base_churn_prob = min(1.0, base_churn_prob * 1.2)
    if renewal_count >= 3:
        base_churn_prob = max(0.02, base_churn_prob * 0.7)

    churned = int(random.random() < base_churn_prob)

    return {
        "customer_id": f"cust_{customer_id:06d}",
        "platform_id": platform,
        "bank_id": bank,
        "state": state,
        "fd_amount": fd_amount,
        "tenure_months": tenure_months,
        "interest_rate": interest_rate,
        "renewal_count": renewal_count,
        "days_since_login": days_since_login,
        "app_engagement_score": app_engagement_score,
        "rate_sensitivity": round(rate_sensitivity, 3),
        "support_tickets_last_90d": support_tickets,
        "kyc_complete": int(kyc_complete),
        "days_to_maturity": days_to_maturity,
        "checked_competitor_fd": int(checked_competitor),
        "nominee_added": int(nominee_added),
        "true_segment": segment,
        "churned": churned,  # label
    }


def generate_dataset(n_customers: int = 10000) -> list:
    print(f"Generating {n_customers:,} synthetic FD customer records...")
    customers = [generate_customer(i) for i in range(1, n_customers + 1)]

    churn_count = sum(c["churned"] for c in customers)
    print(f"  Churn rate: {churn_count/n_customers*100:.1f}% ({churn_count:,} churned)")

    segment_dist = {}
    for c in customers:
        seg = c["true_segment"]
        segment_dist[seg] = segment_dist.get(seg, 0) + 1
    print("  Segment distribution:")
    for seg, count in sorted(segment_dist.items()):
        print(f"    {seg:12s}: {count:5d} ({count/n_customers*100:.1f}%)")

    return customers


def save_csv(customers: list, path: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=customers[0].keys())
        writer.writeheader()
        writer.writerows(customers)
    print(f"  Saved CSV → {path}")


def save_json_sample(customers: list, path: str, n: int = 20):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(customers[:n], f, indent=2)
    print(f"  Saved JSON sample ({n} records) → {path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate synthetic FD customer data")
    parser.add_argument("--customers", type=int, default=10000, help="Number of customer records")
    parser.add_argument("--out", type=str, default="data/fd_customers.csv")
    args = parser.parse_args()

    customers = generate_dataset(args.customers)
    save_csv(customers, args.out)
    save_json_sample(customers, args.out.replace(".csv", "_sample.json"))
    print("\nDone. Run `python src/models/churn_model.py --train` next.")
