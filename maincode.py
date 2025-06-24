import streamlit as st
import pandas as pd
import os
from datetime import datetime
from fpdf import FPDF
import matplotlib.pyplot as plt
from io import BytesIO
import tempfile

st.set_page_config(page_title="Bano Butt PSO Funds Dashboard", layout="wide")

# ---- CONSTANTS ---- #
CATEGORIES = {
    "Marketing/Advertisement": 3000000,
    "Gear and Expenses": 500000,
    "PSO Fuel Card": 500000,
    "Tournament Winning Prize": 1000000,
    "International Tournament Support": 1000000,
}

METHODS = ["Bank Transfer", "Cheque", "Fuel Card Update"]
EXCEL_FILE = "transactions.xlsx"
LOGO_FILE = "749475bc-71ad-470d-a6d5-abb42854ddc5.png"

# ---- Initialize Excel ---- #
if not os.path.exists(EXCEL_FILE):
    df_init = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Method"])
    df_init.to_excel(EXCEL_FILE, index=False)

# ---- Load Data ---- #
df = pd.read_excel(EXCEL_FILE, engine="openpyxl")
df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

# ---- Add Transaction ---- #
st.sidebar.header("Add Transaction")
desc = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0, step=100.0, format="%.2f")
category = st.sidebar.selectbox("Category", CATEGORIES.keys())
method = st.sidebar.selectbox("Method", METHODS)
date = st.sidebar.date_input("Date", value=datetime.today())

if st.sidebar.button("Add Transaction"):
    new_row = pd.DataFrame([{"Date": date, "Description": desc, "Amount": amount, "Category": category, "Method": method}])
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(EXCEL_FILE, index=False)
    st.sidebar.success("Transaction added!")

# ---- Summary Calculation ---- #
def generate_summary(df):
    summary = []
    for cat, total_budget in CATEGORIES.items():
        cat_df = df[df['Category'] == cat]
        used_total = cat_df['Amount'].sum()
        year1 = df['Date'].dt.year.min()
        used_y1 = cat_df[cat_df['Date'].dt.year == year1]['Amount'].sum()

        summary.append({
            "Year": "Year 1",
            "Category": cat,
            "Budget": total_budget / 2,
            "Used": used_y1,
            "Remaining": total_budget / 2 - used_y1,
            "Remaining %": round((1 - used_y1 / (total_budget / 2)) * 100, 2)
        })

        summary.append({
            "Year": "Total",
            "Category": cat,
            "Budget": total_budget,
            "Used": used_total,
            "Remaining": total_budget - used_total,
            "Remaining %": round((1 - used_total / total_budget) * 100, 2)
        })

    return pd.DataFrame(summary)

summary_df = generate_summary(df)
df_sorted = df.sort_values("Date", ascending=False)

# ---- Dashboard ---- #
st.title("🏆 Bano Butt PSO Funds Dashboard")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Year 1 Summary")
    st.dataframe(summary_df[summary_df['Year'] == "Year 1"].style.format({"Budget": "{:,.0f}", "Used": "{:,.0f}", "Remaining": "{:,.0f}"}))

with col2:
    st.subheader("Total Summary")
    st.dataframe(summary_df[summary_df['Year'] == "Total"].style.format({"Budget": "{:,.0f}", "Used": "{:,.0f}", "Remaining": "{:,.0f}"}))

st.subheader("All Transactions")
st.dataframe(df_sorted.style.format({"Amount": "{:,.0f}"}))

# ---- PDF Report Generation ---- #
def generate_pdf(transactions_df, summary_df):
    # Charts
    overall = summary_df[summary_df["Year"] == "Total"]
    categories = overall["Category"].tolist()
    used = overall["Used"].astype(float).tolist()
    budgets = overall["Budget"].astype(float).tolist()
    remaining = overall["Remaining"].astype(float).tolist()

    # Pie Chart
    fig1, ax1 = plt.subplots()
    ax1.pie(used, labels=categories, autopct='%1.1f%%')
    ax1.axis('equal')
    pie_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    fig1.savefig(pie_path)
    plt.close(fig1)

    # Bar Chart
    x = range(len(categories))
    fig2, ax2 = plt.subplots(figsize=(8, 4))
    ax2.bar(x, budgets, width=0.25, label="Budget", color='gray')
    ax2.bar([i + 0.25 for i in x], used, width=0.25, label="Used", color='red')
    ax2.bar([i + 0.5 for i in x], remaining, width=0.25, label="Remaining", color='green')
    ax2.set_xticks([i + 0.25 for i in x])
    ax2.set_xticklabels(categories, rotation=45, ha='right')
    ax2.legend()
    bar_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
    fig2.tight_layout()
    fig2.savefig(bar_path)
    plt.close(fig2)

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    if os.path.exists(LOGO_FILE):
        pdf.image(LOGO_FILE, x=80, w=50)
        pdf.ln(10)

    pdf.cell(200, 10, txt="Bano Butt – PSO Funds Report", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Visual Summary", ln=True)
    pdf.image(pie_path, w=160)
    pdf.ln(5)
    pdf.image(bar_path, w=180)
    pdf.ln(5)

    pdf.cell(200, 10, txt="Transactions", ln=True)
    pdf.set_font("Arial", "", 9)
    for idx, row in transactions_df.iterrows():
        line = f"{row['Date'].strftime('%Y-%m-%d')} | {row['Description']} | PKR {row['Amount']:,.0f} | {row['Category']} | {row['Method']}"
        pdf.multi_cell(0, 8, line)

    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(200, 10, txt="Summary", ln=True)
    pdf.set_font("Arial", "", 9)
    for idx, row in summary_df.iterrows():
        line = (
            f"{row['Year']} – {row['Category']} | Used: PKR {row['Used']:,.0f} "
            f"/ Budget: PKR {row['Budget']:,.0f} | Remaining: PKR {row['Remaining']:,.0f} "
            f"({row['Remaining %']}%)"
        )
        pdf.multi_cell(0, 8, line)

    output = BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# ---- Download PDF Button ---- #
pdf_file = generate_pdf(df_sorted, summary_df)
st.download_button("📄 Download Full Report as PDF", data=pdf_file, file_name="bano_pso_funds_report.pdf")
