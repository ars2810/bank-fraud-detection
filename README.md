# Bank Transaction Fraud Detection System

A Python-based fraud detection prototype that analyzes bank transactions, assigns risk scores, and flags suspicious activity using configurable, rule-based detection.

## Features

- Synthetic bank transaction dataset for demonstration.
- Data cleaning and validation using Pandas and NumPy.
- Rule-based risk scoring for large transactions, repeated transactions, high transaction frequency, and unusual spending compared with account history.
- MySQL database integration for storing transaction records.
- Interactive Streamlit dashboard for exploring transactions and reviewing flagged activity.
- CSV upload and downloadable flagged-transaction reports.
- Automated unit tests using Pytest.

## Technology Stack

- **Language:** Python
- **Data Processing:** Pandas, NumPy
- **Database:** MySQL
- **Dashboard:** Streamlit
- **Testing:** Pytest
- **Configuration:** Environment variables using `.env`

## How It Works

1. Load transaction data from a CSV file.
2. Validate and clean the data.
3. Apply configurable rules to calculate transaction risk scores.
4. Assign risk levels and flag transactions for review.
5. Store transactions in MySQL and explore results through the dashboard.

## Run Locally

Activate your virtual environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

Configure your database credentials in a local `.env` file using `.env.example` as a template. Never commit real credentials.

Run the tests:

```bash
python -m pytest tests -v
```

Run the processing pipeline:

```bash
python -m src.run_pipeline
```

Launch the dashboard:

```bash
python -m streamlit run app.py
```

## Important Limitations

This is an educational prototype using synthetic transaction data and rule-based detection. Its risk scores are not probabilities of fraud, and its performance has not been validated on real-world banking data. Flagged transactions require human review.
