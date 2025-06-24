import streamlit as st
import pandas as pd
from datetime import datetime
import os
from io import BytesIO
from fpdf import FPDF

# --- Config ---
st.set_page_config(page_title="Bano Butt Funds Tracker", layout="wide")
PASSWORD = "psoadmin"
EXCEL_FILE = "bano_funds.xlsx"
CATEGORIES = {
    "Marketing/Advertisement": 3000000,
    "Gear and Expenses": 500000,
    "PSO Fuel Card": 500000,
    "Tournament Winning Prize": 1000000,
    "International Tournament Support": 1000000,
}
METHODS = ["Bank Transfer", "Cheque", "Fuel Card update"]

# --- Utility Functions ---
def format_currency(amount):
    return f"₨ {amount:,.0f}"

def load_data():
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        df["Date"] = pd.to_datetime(df["Date"])
        return df
    else:
        return pd.DataFrame(columns=["Description", "Amount", "Category", "Method", "Date"])

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def get_summary(df):
    df["Year"] = df["Date"].dt.year
    summaries = []

    for year in df["Year"].unique():
        year_data = df[df["Year"] == year]
        for cat, budget in CATEGORIES.items():
            used = year_data[year_data["Category"] == cat]["Amount"].sum()
            remaining = budget - used
            summaries.append({
                "Year": year,
                "Category": cat,
                "Budget": budget,
                "Used": used,
                "Remaining": remaining,
                "Remaining %": round((remaining / budget) * 100, 2)
            })

    # Add overall total row
    for cat, budget in CATEGORIES.items():
        used = df[df["Category"] == cat]["Amount"].sum()
        remaining = budget - used
        summaries.append({
            "Year": "Total",
            "Category": cat,
            "Budget": budget,
            "Used": used,
            "Remaining": remaining,
            "Remaining %": round((remaining / budget) * 100, 2)
        })

    return pd.DataFrame(summaries)

def generate_pdf(transactions_df, summary_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt="Bano Butt – PSO Funds Report", ln=True, align='C')

    # Transactions
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Transactions", ln=True)
    pdf.set_font("Arial", "", 10)
    for idx, row in transactions_df.iterrows():
        line = f"{row['Date'].strftime('%Y-%m-%d')} | {row['Description']} | {format_currency(row['Amount'])} | {row['Category']} | {row['Method']}"
        pdf.multi_cell(0, 10, line)

    # Summary
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Summary", ln=True)
    pdf.set_font("Arial", "", 10)
    for idx, row in summary_df.iterrows():
        line = (
            f"{row['Year']} - {row['Category']} | Used: {format_currency(row['Used'])} "
            f"/ Budget: {format_currency(row['Budget'])} | Remaining: {format_currency(row['Remaining'])} "
            f"({row['Remaining %']}%)"
        )
        pdf.multi_cell(0, 10, line)

    pdf_output = BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# --- Login Page ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Bano Butt Funds Tracker")
    pw = st.text_input("Enter password to continue", type="password")
    if pw == PASSWORD:
        st.session_state.logged_in = True
        st.success("Login successful!")
    else:
        st.stop()

# --- Main App Interface ---
st.title("💰 Bano Butt – PSO Funds Tracker")

# Load and display data
df = load_data()
summary_df = get_summary(df)

# Sidebar: Add transaction
st.sidebar.header("➕ Add Transaction")
with st.sidebar.form("transaction_form"):
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%.2f")
    category = st.selectbox("Category", CATEGORIES.keys())
    method = st.selectbox("Payment Method", METHODS)
    date = st.date_input("Date", datetime.today())
    submitted = st.form_submit_button("Add Transaction")

    if submitted and description and amount > 0:
        new_entry = {
            "Description": description,
            "Amount": amount,
            "Category": category,
            "Method": method,
            "Date": pd.to_datetime(date)
        }
        df = df.append(new_entry, ignore_index=True)
        save_data(df)
        st.success("Transaction added.")

# Dashboard Tabs
tab1, tab2, tab3 = st.tabs(["📋 Transactions", "📊 Summary", "📄 Export Report"])

# Tab 1: Transactions
with tab1:
    st.subheader("All Transactions")
    df_sorted = df.sort_values(by="Date", ascending=False)
    df_display = df_sorted.copy()
    df_display["Amount"] = df_display["Amount"].apply(format_currency)
    st.dataframe(df_display, use_container_width=True)

# Tab 2: Summary
with tab2:
    st.subheader("Remaining Funds Overview (Per Year and Total)")
    summary_display = summary_df.copy()
    summary_display["Budget"] = summary_display["Budget"].apply(format_currency)
    summary_display["Used"] = summary_display["Used"].apply(format_currency)
    summary_display["Remaining"] = summary_display["Remaining"].apply(format_currency)
    st.dataframe(summary_display, use_container_width=True)

# Tab 3: PDF Export
with tab3:
    st.subheader("Export Report")
    pdf_file = generate_pdf(df_sorted, summary_df)
    st.download_button(
        label="📄 Download PDF Report",
        data=pdf_file,
        file_name="bano_funds_report.pdf",
        mime="application/pdf"
    )
