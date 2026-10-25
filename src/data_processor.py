import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "transaction_id",
    "account_id",
    "timestamp",
    "amount",
    "merchant_category",
    "transaction_type",
    "location",
]


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean transaction records."""
    missing = set(REQUIRED_COLUMNS) - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    cleaned = df[REQUIRED_COLUMNS].copy()

    cleaned["transaction_id"] = cleaned["transaction_id"].astype("string").str.strip()
    cleaned["account_id"] = cleaned["account_id"].astype("string").str.strip()

    cleaned["timestamp"] = pd.to_datetime(
        cleaned["timestamp"], errors="coerce", utc=True
    )
    cleaned["amount"] = pd.to_numeric(cleaned["amount"], errors="coerce")

    cleaned = cleaned.dropna(
        subset=["transaction_id", "account_id", "timestamp", "amount"]
    )

    cleaned = cleaned[
        cleaned["transaction_id"].ne("")
        & cleaned["account_id"].ne("")
        & np.isfinite(cleaned["amount"])
        & cleaned["amount"].ge(0)
    ].copy()

    # Keep the first occurrence of each transaction ID.
    cleaned = cleaned.drop_duplicates(subset=["transaction_id"], keep="first")

    return cleaned.sort_values(
        ["account_id", "timestamp", "transaction_id"]
    ).reset_index(drop=True)
