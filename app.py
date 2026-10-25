import streamlit as st
import pandas as pd

from src.database import load_transactions
from src.risk_engine import detect_suspicious_transactions


st.set_page_config(
    page_title="Bank Fraud Monitoring",
    page_icon="🛡️",
    layout="wide",
)

st.title("🛡️ Bank Transaction Fraud Monitoring")
st.caption(
    "Demo dashboard using synthetic transaction data. Flags are rule-based and require human review."
)

st.subheader("Upload Transactions")
uploaded_file = st.file_uploader(
    "Upload a CSV transaction file",
    type=["csv"],
    help="CSV must contain transaction_id, account_id, timestamp, amount, merchant_category, transaction_type, and location.",
)



if uploaded_file is not None:
    try:
        uploaded_transactions = pd.read_csv(uploaded_file)
        analyzed_upload = detect_suspicious_transactions(uploaded_transactions)

        st.success(
            f"Analyzed {len(analyzed_upload)} transactions from your uploaded CSV."
        )

        flagged_upload = analyzed_upload[analyzed_upload["is_flagged"]]
        
        st.download_button(
            label="Download Flagged Transactions Report",
            data=flagged_upload.to_csv(index=False).encode("utf-8"),
            file_name="flagged_transactions_report.csv",
            mime="text/csv",
        )


        st.metric("Flagged in uploaded file", len(flagged_upload))

        st.dataframe(
            analyzed_upload[
                [
                    "transaction_id",
                    "account_id",
                    "timestamp",
                    "amount",
                    "risk_score",
                    "risk_level",
                    "is_flagged",
                    "risk_reasons",
                ]
            ],
            use_container_width=True,
            hide_index=True,
        )

    except Exception as exc:
        st.error(f"Could not analyze the uploaded CSV: {exc}")

try:
    df = load_transactions()

    if df.empty:
        st.warning("No transactions found. Run the data pipeline first.")
        st.stop()

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["risk_score"] = pd.to_numeric(df["risk_score"], errors="coerce").fillna(0)
    df["is_flagged"] = df["is_flagged"].astype(bool)

    total = len(df)
    flagged = int(df["is_flagged"].sum())
    high_risk = int((df["risk_level"] == "High").sum())
    total_amount = df["amount"].sum()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Transactions", f"{total:,}")
    col2.metric("Flagged Transactions", f"{flagged:,}")
    col3.metric("High-Risk Transactions", f"{high_risk:,}")
    col4.metric("Total Transaction Value", f"₹{total_amount:,.2f}")

    st.subheader("Risk Level Distribution")
    risk_counts = (
        df["risk_level"].value_counts().reindex(["Low", "Medium", "High"], fill_value=0)
    )
    st.bar_chart(risk_counts)

    st.subheader("Transaction Explorer")

    search_query = st.text_input(
    "Search by Transaction ID or Account ID",
    placeholder="e.g. TXN0109 or ACC001",
)

    
    risk_filter = st.multiselect(
    "Filter by risk level",
    options=["Low", "Medium", "High"],
    default=["Medium", "High"],
    help="Choose one or more risk levels to display.",
)


    flagged_only = st.checkbox("Show only flagged transactions", value=True)

    filtered = df[df["risk_level"].isin(risk_filter)].copy()

    
    if search_query.strip():
        query = search_query.strip()

        search_mask = (
        filtered["transaction_id"].astype(str).str.contains(
            query, case=False, na=False, regex=False
        )
        | filtered["account_id"].astype(str).str.contains(
            query, case=False, na=False, regex=False
        )
    )

    filtered = filtered[search_mask]



    if flagged_only:
        filtered = filtered[filtered["is_flagged"]]

    st.dataframe(
        filtered[
            [
                "transaction_id",
                "account_id",
                "timestamp",
                "amount",
                "merchant_category",
                "location",
                "risk_score",
                "risk_level",
                "is_flagged",
                "risk_reasons",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Flagged Transaction Details")
    flagged_df = df[df["is_flagged"]].sort_values("risk_score", ascending=False)

    if flagged_df.empty:
        st.info("No transactions are currently flagged.")
    else:
        selected_id = st.selectbox(
            "Select a transaction",
            flagged_df["transaction_id"].tolist(),
        )
        selected = flagged_df[flagged_df["transaction_id"] == selected_id].iloc[0]

        st.write(f"**Risk score:** {int(selected['risk_score'])}/100")
        st.write(f"**Risk level:** {selected['risk_level']}")
        st.write(f"**Amount:** ₹{selected['amount']:,.2f}")
        st.write(f"**Reason:** {selected['risk_reasons']}")

except Exception as exc:
    st.error(f"Could not load dashboard data: {exc}")
    st.info("Check your MySQL server, .env settings, and database table.")
