
import os
from decimal import Decimal, InvalidOperation

import mysql.connector
import pandas as pd
from dotenv import load_dotenv


load_dotenv()


def get_connection():
    """Open a MySQL connection using local environment settings."""
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [key for key in required if not os.getenv(key)]

    if missing:
        raise ValueError(
            f"Missing database settings: {', '.join(missing)}. "
            "Check your .env file."
        )

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=10,
    )


def create_table():
    """Create the transactions table if it does not exist."""
    query = """
    CREATE TABLE IF NOT EXISTS transactions (
        transaction_id VARCHAR(30) PRIMARY KEY,
        account_id VARCHAR(30) NOT NULL,
        transaction_timestamp DATETIME NOT NULL,
        amount DECIMAL(12, 2) NOT NULL,
        merchant_category VARCHAR(50),
        transaction_type VARCHAR(30),
        location VARCHAR(50),
        risk_score INT NOT NULL DEFAULT 0,
        risk_level VARCHAR(10) NOT NULL DEFAULT 'Low',
        is_flagged BOOLEAN NOT NULL DEFAULT FALSE,
        risk_reasons VARCHAR(500)
    )
    """

    connection = get_connection()
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        cursor.close()
    finally:
        connection.close()


def save_transactions(df: pd.DataFrame) -> int:
    """Insert or update analyzed transactions in MySQL."""
    required = [
        "transaction_id", "account_id", "timestamp", "amount",
        "merchant_category", "transaction_type", "location",
        "risk_score", "risk_level", "is_flagged", "risk_reasons",
    ]

    missing = set(required) - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO transactions (
        transaction_id, account_id, transaction_timestamp, amount,
        merchant_category, transaction_type, location,
        risk_score, risk_level, is_flagged, risk_reasons
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        account_id = VALUES(account_id),
        transaction_timestamp = VALUES(transaction_timestamp),
        amount = VALUES(amount),
        merchant_category = VALUES(merchant_category),
        transaction_type = VALUES(transaction_type),
        location = VALUES(location),
        risk_score = VALUES(risk_score),
        risk_level = VALUES(risk_level),
        is_flagged = VALUES(is_flagged),
        risk_reasons = VALUES(risk_reasons)
    """

    records = []

    try:
        for row in df[required].itertuples(index=False, name=None):
            (
                transaction_id, account_id, timestamp, amount,
                category, transaction_type, location,
                score, level, flagged, reasons,
            ) = row

            # MySQL DATETIME does not store timezone information.
            timestamp = pd.Timestamp(timestamp).to_pydatetime().replace(
                tzinfo=None
            )

            try:
                amount = Decimal(str(amount))
            except InvalidOperation as exc:
                raise ValueError("Invalid transaction amount") from exc

            records.append((
                str(transaction_id),
                str(account_id),
                timestamp,
                amount,
                str(category),
                str(transaction_type),
                str(location),
                int(score),
                str(level),
                bool(flagged),
                str(reasons)[:500],
            ))

        cursor.executemany(query, records)
        connection.commit()
        return len(records)

    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


def load_transactions() -> pd.DataFrame:
    """Load stored transactions into a DataFrame."""
    connection = get_connection()

    try:
        query = """
        SELECT
            transaction_id,
            account_id,
            transaction_timestamp AS timestamp,
            amount,
            merchant_category,
            transaction_type,
            location,
            risk_score,
            risk_level,
            is_flagged,
            risk_reasons
        FROM transactions
        ORDER BY transaction_timestamp DESC
        """

        return pd.read_sql(query, connection)
    finally:
        connection.close()
