# Bano Butt Funds Tracker - Streamlit App

import streamlit as st
import pandas as pd
import os
from datetime import datetime
from pathlib import Path
import altair as alt

# -----------------------------
# Configuration
# -----------------------------
PASSWORD = "psoadmin"
DATA_FILE = "bano_funds.xlsx"

FUND_CATEGORIES = {
    "Marketing/Advertisement": 3_000_000,
    "Gear and Expenses": 500_000,
    "PSO Fuel Card": 500_000,
    "Tournament Winning Prize": 1_000_000,
    "International Tournament Support": 1_000_000,
}

METHODS = ["Bank Transfer", "Cheque", "Fuel Card Update"]

# -----------------------------
# Authentication
# -----------------------------
def login():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if password == PASSWORD:
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Incorrect password")
        st.stop()

# -----------------------------
# File Handling
# -----------------------------
def load_data():
    if Path(DATA_FILE).exists():
        return pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Method"])
        df.to_excel(DATA_FILE, index=False)
        return df

def save_data(df):
    df.to_excel(DATA_FILE, index=False)

# -----------------------------
# Transaction Entry
# -----------------------------
def add_transaction():
    st.header("Add New Transaction")

    with st.form("transaction_form"):
        date = st.date_input("Date", value=datetime.today())
        description = st.text_input("Description")
        amount = st.number_input("Amount", min_value=0, step=1000)
        category = st.selectbox("Category", list(FUND_CATEGORIES.keys()))
        method = st.selectbox("Payment Method", METHODS)
        submitted = st.form_submit_button("Add Transaction")

        if submitted:
            df = load_data()
            new_row = pd.DataFrame({
                "Date": [date],
                "Description": [description],
                "Amount": [amount],
                "Category": [category],
                "Method": [method],
            })
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success("Transaction added successfully!")

# -----------------------------
# Dashboard
# -----------------------------
def dashboard():
    st.header("Dashboard")
    df = load_data()
    if df.empty:
        st.info("No transactions yet.")
        return

    df["Year"] = pd.to_datetime(df["Date"]).dt.year

    total_spent = df.groupby("Category")["Amount"].sum().reset_index()
    total_spent["Budget"] = total_spent["Category"].map(FUND_CATEGORIES)
    total_spent["Remaining"] = total_spent["Budget"] - total_spent["Amount"]
    total_spent["Used %"] = (total_spent["Amount"] / total_spent["Budget"]) * 100

    st.subheader("Fund Usage Overview")
    st.dataframe(total_spent)

    bar = alt.Chart(total_spent).mark_bar().encode(
        x=alt.X("Category", sort="-y"),
        y="Amount",
        color=alt.Color("Category", legend=None),
        tooltip=["Category", "Amount", "Budget", "Used %"]
    ).properties(height=400)
    st.altair_chart(bar, use_container_width=True)

    pie = alt.Chart(total_spent).mark_arc(innerRadius=50).encode(
        theta="Amount",
        color="Category",
        tooltip=["Category", "Amount", "Used %"]
    ).properties(title="Spending by Category")
    st.altair_chart(pie, use_container_width=True)

# -----------------------------
# App Layout
# -----------------------------
def main():
    st.set_page_config(page_title="Bano Butt Fund Tracker", layout="wide")
    login()

    tab1, tab2 = st.tabs(["🏠 Dashboard", "➕ Add Transaction"])

    with tab1:
        dashboard()
    with tab2:
        add_transaction()

if __name__ == "__main__":
    main()
