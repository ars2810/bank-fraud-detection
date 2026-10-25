CREATE DATABASE IF NOT EXISTS bank_fraud_db;
USE bank_fraud_db;
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
);

CREATE INDEX idx_account_timestamp
ON transactions (account_id, transaction_timestamp);

CREATE INDEX idx_flagged
ON transactions (is_flagged);