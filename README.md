# Bank Transaction Fraud Detection System

A Python-based fraud detection prototype that analyzes bank transactions, assigns risk scores, and flags potentially suspicious activity using configurable, rule-based detection.

## Features

- Synthetic bank transaction dataset for demonstration
- Data cleaning and validation using Pandas and NumPy
- Risk scoring for large transactions, repeated transactions, high transaction frequency, and unusual spending compared with account history
- MySQL database integration for storing transaction records
- Interactive Streamlit dashboard for transaction exploration and risk review
- CSV upload and downloadable flagged-transaction reports
- Automated unit tests using Pytest

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic and risk analysis |
| Pandas and NumPy | Data processing and validation |
| MySQL | Transaction storage |
| Streamlit | Interactive dashboard |
| Pytest | Automated testing |
| Environment variables | Database configuration |

## How It Works

1. Load transaction data from a CSV file.
2. Validate and clean transaction records.
3. Apply configurable rules to calculate risk scores.
4. Assign risk levels and flag transactions for review.
5. Store transaction results in MySQL.
6. Explore transactions and download flagged reports through the dashboard.

## Getting Started

### Prerequisites

- Python
- MySQL Server
- Git

### Installation

Clone the repository and enter the project directory:

```bash
git clone https://github.com/ars2810/bank-fraud-detection.git
cd bank-fraud-detection
```

Create and activate a virtual environment on Windows:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Database Configuration

1. Create the MySQL database and application user using the provided `schema.sql` and your local MySQL administration tools.
2. Copy `.env.example` to `.env`.
3. Set your local database credentials in `.env`.
4. Never commit real credentials or share your `.env` file.

### Run the Tests

```bash
python -m pytest tests -v
```

### Run the Processing Pipeline

```bash
python -m src.run_pipeline
```

### Launch the Dashboard

```bash
python -m streamlit run app.py
```

## Limitations

This is an educational prototype that uses synthetic transaction data and rule-based detection. Risk scores are not probabilities of fraud, and the system has not been validated on real-world banking data. Flagged transactions require human review.

## Future Improvements

- Add more unit and integration tests.
- Evaluate detection quality using labeled data.
- Track false positives and false negatives.
- Explore machine-learning models when suitable labeled data is available.
- Add audit logging and stronger database access controls.
