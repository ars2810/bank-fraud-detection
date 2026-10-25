from pathlib import Path

import numpy as np
import pandas as pd


def generate_transactions() -> pd.DataFrame:
    """Generate reproducible, fictional banking transactions."""
    rng = np.random.default_rng(42)

    start_time = pd.Timestamp("2026-01-01 08:00:00")

    categories = [
        "Grocery",
        "Shopping",
        "Fuel",
        "Dining",
        "Travel",
        "Utilities",
    ]

    transaction_types = ["Debit", "Online", "Transfer", "ATM"]

    rows = []

    # Generate 100 ordinary sample transactions.
    for i in range(1, 101):
        rows.append(
            {
                "transaction_id": f"TXN{i:04d}",
                "account_id": f"ACC{rng.integers(1001, 1021)}",
                "timestamp": (
                    start_time + pd.Timedelta(minutes=int(rng.integers(0, 20160)))
                ),
                "amount": round(float(rng.uniform(10, 2500)), 2),
                "merchant_category": str(rng.choice(categories)),
                "transaction_type": str(rng.choice(transaction_types)),
                "location": str(rng.choice(["Delhi", "Mumbai", "Bengaluru", "Pune"])),
            }
        )

    # Scenario 1: An unusually large transaction.
    rows.append(
        {
            "transaction_id": "TXN0101",
            "account_id": "ACC9001",
            "timestamp": start_time + pd.Timedelta(days=1),
            "amount": 8500.00,
            "merchant_category": "Shopping",
            "transaction_type": "Online",
            "location": "Mumbai",
        }
    )

    # Scenario 2: Three transactions from one account within 10 minutes.
    for i, minute, amount in [
        (102, 0, 180.00),
        (103, 3, 195.00),
        (104, 6, 205.00),
    ]:
        rows.append(
            {
                "transaction_id": f"TXN{i:04d}",
                "account_id": "ACC9002",
                "timestamp": start_time + pd.Timedelta(days=2, minutes=minute),
                "amount": amount,
                "merchant_category": "Shopping",
                "transaction_type": "Online",
                "location": "Delhi",
            }
        )

    # Scenario 3: Five transactions within a 30-minute period.
    for i, minute in enumerate([0, 5, 10, 15, 20], start=105):
        rows.append(
            {
                "transaction_id": f"TXN{i:04d}",
                "account_id": "ACC9003",
                "timestamp": start_time + pd.Timedelta(days=3, minutes=minute),
                "amount": 75.00 + minute,
                "merchant_category": "Dining",
                "transaction_type": "Debit",
                "location": "Pune",
            }
        )

    df = pd.DataFrame(rows)

    return df.sort_values("timestamp").reset_index(drop=True)


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[1]
    output_path = project_root / "data" / "synthetic_transactions.csv"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    transactions = generate_transactions()
    transactions.to_csv(output_path, index=False)

    print(f"Generated {len(transactions)} transactions.")
    print(f"Saved to: {output_path}")
