
import pandas as pd

from src.risk_engine import detect_suspicious_transactions
from src.database import create_table, save_transactions

def main():
    # Load the synthetic transaction dataset
    input_file = "data/synthetic_transactions.csv"
    transactions = pd.read_csv(input_file)

    print(f"Loaded {len(transactions)} transactions.")

    # Apply the fraud detection rules
    results = detect_suspicious_transactions(transactions)

    print(f"Flagged transactions: {int(results['is_flagged'].sum())}")

    # Ensure the database table exists and save results
    create_table()
    saved_count = save_transactions(results)

    print(f"Successfully saved {saved_count} transactions to MySQL.")
    print("\nHighest-risk transactions:")
    print(
        results[
            ["transaction_id", "amount", "risk_score", "risk_level", "risk_reasons"]
        ].head(10).to_string(index=False)
    )

if __name__ == "__main__":
    main()
