
import pandas as pd
import pytest

from src.risk_engine import detect_suspicious_transactions


def make_transaction(transaction_id, account_id, timestamp, amount):
    return {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "timestamp": timestamp,
        "amount": amount,
        "merchant_category": "Shopping",
        "transaction_type": "Online",
        "location": "Delhi",
    }


def test_large_transaction_is_flagged():
    data = pd.DataFrame([
        make_transaction("TXN001", "ACC001", "2026-01-01 10:00:00", 8500)
    ])

    result = detect_suspicious_transactions(data)

    assert result.iloc[0]["risk_score"] == 40
    assert bool(result.iloc[0]["is_flagged"])
    assert result.iloc[0]["risk_level"] == "Medium"


def test_repeated_transactions_are_flagged():
    data = pd.DataFrame([
        make_transaction("TXN001", "ACC001", "2026-01-01 10:00:00", 100),
        make_transaction("TXN002", "ACC001", "2026-01-01 10:03:00", 120),
        make_transaction("TXN003", "ACC001", "2026-01-01 10:06:00", 140),
    ])

    result = detect_suspicious_transactions(data)
    last = result.set_index("transaction_id").loc["TXN003"]

    assert last["risk_score"] == 35
    assert bool(last["is_flagged"])
    assert "Repeated transactions" in last["risk_reasons"]


def test_ordinary_transaction_is_not_flagged():
    data = pd.DataFrame([
        make_transaction("TXN001", "ACC001", "2026-01-01 10:00:00", 250)
    ])

    result = detect_suspicious_transactions(data)

    assert result.iloc[0]["risk_score"] == 0
    assert not bool(result.iloc[0]["is_flagged"])
    assert result.iloc[0]["risk_level"] == "Low"


def test_negative_amount_is_removed():
    data = pd.DataFrame([
        make_transaction("TXN001", "ACC001", "2026-01-01 10:00:00", -100)
    ])

    result = detect_suspicious_transactions(data)

    assert result.empty


def test_missing_column_raises_error():
    data = pd.DataFrame([
        {"transaction_id": "TXN001", "amount": 100}
    ])

    with pytest.raises(ValueError, match="Missing required columns"):
        detect_suspicious_transactions(data)



def test_unusual_spending_compared_with_account_history():
    data = pd.DataFrame([
        make_transaction("TXN001", "ACC100", "2026-01-01 09:00:00", 100),
        make_transaction("TXN002", "ACC100", "2026-01-02 09:00:00", 150),
        make_transaction("TXN003", "ACC100", "2026-01-03 09:00:00", 200),
        make_transaction("TXN004", "ACC100", "2026-01-04 09:00:00", 180),
        make_transaction("TXN005", "ACC100", "2026-01-05 09:00:00", 120),
        make_transaction("TXN006", "ACC100", "2026-01-06 09:00:00", 2000),
    ])

    result = detect_suspicious_transactions(data)
    unusual = result.set_index("transaction_id").loc["TXN006"]

    assert unusual["risk_score"] == 20
    assert unusual["risk_level"] == "Low"
    assert not bool(unusual["is_flagged"])
    assert "account history" in unusual["risk_reasons"]


def test_consistent_account_spending_does_not_trigger_history_rule():
    data = pd.DataFrame([
        make_transaction("TXN101", "ACC200", "2026-01-01 09:00:00", 200),
        make_transaction("TXN102", "ACC200", "2026-01-02 09:00:00", 220),
        make_transaction("TXN103", "ACC200", "2026-01-03 09:00:00", 190),
        make_transaction("TXN104", "ACC200", "2026-01-04 09:00:00", 210),
        make_transaction("TXN105", "ACC200", "2026-01-05 09:00:00", 205),
        make_transaction("TXN106", "ACC200", "2026-01-06 09:00:00", 215),
    ])

    result = detect_suspicious_transactions(data)
    last = result.set_index("transaction_id").loc["TXN106"]

    assert last["risk_score"] == 0
    assert not bool(last["is_flagged"])
    assert "account history" not in last["risk_reasons"]

