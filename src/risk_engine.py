
from collections import deque

import numpy as np
import pandas as pd

from src.data_processor import clean_transactions


# Rule configuration
AMOUNT_THRESHOLD = 5000.00

SHORT_WINDOW_MINUTES = 10
SHORT_WINDOW_COUNT = 3

FREQUENCY_WINDOW_MINUTES = 30
FREQUENCY_WINDOW_COUNT = 5

ACCOUNT_HISTORY_MIN_TRANSACTIONS = 5
ACCOUNT_SPIKE_MULTIPLIER = 3
ACCOUNT_SPIKE_MIN_AMOUNT = 1000.00

AMOUNT_POINTS = 40
REPEATED_POINTS = 35
FREQUENCY_POINTS = 25
ACCOUNT_SPIKE_POINTS = 20

FLAG_THRESHOLD = 30


def detect_suspicious_transactions(
    transactions: pd.DataFrame,
) -> pd.DataFrame:

    df = clean_transactions(transactions)

    df["risk_score"] = 0
    df["risk_reasons"] = ""

    large_amount = df["amount"] > AMOUNT_THRESHOLD

    df.loc[large_amount, "risk_score"] += AMOUNT_POINTS

    for _, group in df.groupby("account_id", sort=False):
        group = group.sort_values("timestamp")

        short_window = deque()
        frequency_window = deque()
        amount_history = []

        for idx, row in group.iterrows():
            current_time = row["timestamp"]
            amount = float(row["amount"])

            # Remove transactions outside the time windows.
            while (
                short_window
                and current_time - short_window[0]
                > pd.Timedelta(minutes=SHORT_WINDOW_MINUTES)
            ):
                short_window.popleft()

            while (
                frequency_window
                and current_time - frequency_window[0]
                > pd.Timedelta(minutes=FREQUENCY_WINDOW_MINUTES)
            ):
                frequency_window.popleft()

            reasons = []

            if large_amount.loc[idx]:
                reasons.append("Unusually large amount")

            # Compare against previous transactions for this account.
            # Do not use the current transaction in its own baseline.
            if len(amount_history) >= ACCOUNT_HISTORY_MIN_TRANSACTIONS:
                typical_amount = float(np.median(amount_history))

                if (
                    amount > ACCOUNT_SPIKE_MIN_AMOUNT
                    and amount > typical_amount * ACCOUNT_SPIKE_MULTIPLIER
                ):
                    df.loc[idx, "risk_score"] += ACCOUNT_SPIKE_POINTS
                    reasons.append(
                        "Unusually high compared with account history"
                    )

            # Check transaction frequency.
            short_window.append(current_time)
            frequency_window.append(current_time)

            if len(short_window) >= SHORT_WINDOW_COUNT:
                df.loc[idx, "risk_score"] += REPEATED_POINTS
                reasons.append(
                    "Repeated transactions within 10 minutes"
                )

            if len(frequency_window) >= FREQUENCY_WINDOW_COUNT:
                df.loc[idx, "risk_score"] += FREQUENCY_POINTS
                reasons.append(
                    "High transaction frequency within 30 minutes"
                )

            if reasons:
                df.loc[idx, "risk_reasons"] = "; ".join(reasons)

            # Save this amount for future transactions only.
            amount_history.append(amount)

    df["risk_score"] = (
        df["risk_score"].clip(upper=100).astype(int)
    )

    df["risk_level"] = pd.cut(
        df["risk_score"],
        bins=[-1, 29, 59, 100],
        labels=["Low", "Medium", "High"],
    ).astype(str)

    df["is_flagged"] = df["risk_score"] >= FLAG_THRESHOLD

    return df.sort_values(
        ["risk_score", "timestamp"],
        ascending=[False, False],
    ).reset_index(drop=True)

