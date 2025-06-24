```python
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fixed budgets
BUDGETS = {
    "Marketing": 3000000,
    "Gear and Equipment": 500000,
    "PSO Fuel Card": 500000,
    "Winning Prize": 1000000,
    "International Tournament": 1000000
}

# CSV file for transactions
CSV_FILE = "transactions.csv"

# Initialize session state
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(columns=[
        "Sr. No", "Receiving Date", "Payment Method", "Description", 
        "Category", "Amount", "% of Funds Used", "Notes"
    ])

# Load transactions from CSV
def load_transactions():
    try:
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            # Convert dates with error handling
            df["Receiving Date"] = pd.to_datetime(df["Receiving Date"], errors='coerce')
            # Log invalid dates
            invalid_dates = df[df["Receiving Date"].isna()]
            if not invalid_dates.empty:
                logger.warning(f"Invalid dates found in CSV:\n{invalid_dates}")
                st.warning(f"Found {len(invalid_dates)} invalid date entries in transactions.csv. These rows will be ignored.")
            # Drop rows with invalid dates
            df = df.dropna(subset=["Receiving Date"])
            st.session_state.transactions = df
        else:
            st.session_state.transactions = pd.DataFrame(columns=[
                "Sr. No", "Receiving Date", "Payment Method", "Description", 
                "Category", "Amount", "% of Funds Used", "Notes"
            ])
    except Exception as e:
        logger.error(f"Error loading transactions: {str(e)}")
        st.error("Error loading transactions. Please check the CSV file format.")
        st.session_state.transactions = pd.DataFrame(columns=[
            "Sr. No", "Receiving Date", "Payment Method", "Description", 
            "Category", "Amount", "% of Funds Used", "Notes"
        ])

# Save transactions to CSV
def save_transactions():
    try:
        # Ensure dates are saved in YYYY-MM-DD format
        df = st.session_state.transactions.copy()
        df["Receiving Date"] = df["Receiving Date"].dt.strftime('%Y-%m-%d')
        df.to_csv(CSV_FILE, index=False)
    except Exception as e:
        logger.error(f"Error saving transactions: {str(e)}")
        st.error("Error saving transactions.")

# Download CSV
def download_csv():
    csv = st.session_state.transactions.to_csv(index=False)
    st.download_button(
        label="Download Transactions CSV",
        data=csv,
        file_name="transactions.csv",
        mime="text/csv"
    )

# Calculate summary
def calculate_summary(df):
    summary = []
    total_budget = sum(BUDGETS.values())
    total_used = 0
    for category, budget in BUDGETS.items():
        cat_df = df[df["Category"] == category]
        used = cat_df["Amount"].sum()
        remaining = budget - used
        percent_used = (used / budget * 100) if budget > 0 else 0
        percent_remaining = 100 - percent_used
        total_used += used
        summary.append({
            "Category": category,
            "Total Budget (PKR)": budget,
            "Used (PKR)": used,
            "Remaining (PKR)": remaining,
            "% Used": round(percent_used, 2),
            "% Remaining": round(percent_remaining, 2)
        })
    summary.append({
        "Category": "Total",
        "Total Budget (PKR)": total_budget,
        "Used (PKR)": total_used,
        "Remaining (PKR)": total_budget - total_used,
        "% Used": round(total_used / total_budget * 100, 2) if total_budget > 0 else 0,
        "% Remaining": round((total_budget - total_used) / total_budget * 100, 2) if total_budget > 0 else 0
    })
    return pd.DataFrame(summary)

# Export to PDF
def export_to_pdf(df):
    try:
        pdf_file = "Bano_Funds_Tracker.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Bano Funds Tracker", styles['Title']))
        
        # Transactions table
        data = [df.columns.tolist()] + df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.black),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.green)
        ]))
        elements.append(table)
        
        # Summary table
        summary_df = calculate_summary(df)
        elements.append(Paragraph("Summary", styles['Heading2']))
        data = [summary_df.columns.tolist()] + summary_df.values.tolist()
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.black),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.green)
        ]))
        elements.append(table)
        
        doc.build(elements)
        with open(pdf_file, 'rb') as f:
            st.download_button("Download PDF", f, file_name=pdf_file)
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}")
        st.error("Error generating PDF.")

# Custom CSS for theme
st.markdown("""
    <style>
    body, .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }
    .stButton > button {
        background-color: #00FF00;
        color: #000000;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div > select, .stDateInput > div > div > input {
        background-color: #1C2526;
        color: #FFFFFF;
        border-color: #00FF00;
    }
    .stDataFrame, .stTable {
        background-color: #1C2526;
        color: #FFFFFF;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #00FF00;
    }
    </style>
""", unsafe_allow_html=True)

# Login page
if not st.session_state.logged_in:
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username == "bano" and password == "pso2025":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid username or password")
else:
    # Load transactions
    load_transactions()
    
    st.title("Bano Funds Tracker")
    
    # Add transaction
    with st.form("add_transaction"):
        st.subheader("Add Transaction")
        date = st.date_input("Receiving Date")
        payment_method = st.selectbox("Payment Method", ["Cheque", "Deposit"])
        description = st.text_input("Description")
        category = st.selectbox("Category", list(BUDGETS.keys()))
        amount = st.number_input("Amount (PKR)", min_value=0.0)
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Add Transaction")
        
        if submit:
            if description and description.strip():
                percent_used = (amount / BUDGETS[category] * 100) if BUDGETS[category] > 0 else 0
                new_row = {
                    "Sr. No": len(st.session_state.transactions) + 1,
                    "Receiving Date": date,
                    "Payment Method": payment_method,
                    "Description": description,
                    "Category": category,
                    "Amount": amount,
                    "% of Funds Used": round(percent_used, 2),
                    "Notes": notes
                }
                st.session_state.transactions = pd.concat(
                    [st.session_state.transactions, pd.DataFrame([new_row])],
                    ignore_index=True
                )
                save_transactions()
                st.success("Transaction added!")
            else:
                st.error("Description cannot be empty!")
    
    # Display transactions
    st.subheader("Transaction Ledger")
    df = st.session_state.transactions.copy()
    
    # Filters
    with st.expander("Apply Filters"):
        categories = ["All"] + list(BUDGETS.keys())
        selected_category = st.selectbox("Filter by Category", categories)
        payment_methods = ["All"] + list(df["Payment Method"].unique()) if not df.empty else ["All"]
        selected_method = st.selectbox("Filter by Payment Method", payment_methods)
        date_range = st.date_input("Date Range", 
                                  [df["Receiving Date"].min() if not df.empty else datetime.now(), 
                                   df["Receiving Date"].max() if not df.empty else datetime.now()])
        
        if selected_category != "All":
            df = df[df["Category"] == selected_category]
        if selected_method != "All":
            df = df[df["Payment Method"] == selected_method]
        if date_range and len(date_range) == 2:
            df = df[(df["Receiving Date"] >= pd.to_datetime(date_range[0])) & 
                    (df["Receiving Date"] <= pd.to_datetime(date_range[1]))]
    
    # Display filtered transactions
    st.dataframe(df, use_container_width=True)
    
    # Edit/Delete transactions
    if not df.empty:
        st.subheader("Edit/Delete Transaction")
        sr_no = st.selectbox("Select Sr. No to Edit/Delete", df["Sr. No"])
        selected_row = df[df["Sr. No"] == sr_no].iloc[0]
        
        with st.form("edit_transaction"):
            edit_date = st.date_input("Edit Date", selected_row["Receiving Date"])
            edit_payment_method = st.selectbox("Edit Payment Method", ["Cheque", "Deposit"], 
                                              index=["Cheque", "Deposit"].index(selected_row["Payment Method"]))
            edit_description = st.text_input("Edit Description", selected_row["Description"])
            edit_category = st.selectbox("Edit Category", list(BUDGETS.keys()), 
                                        index=list(BUDGETS.keys()).index(selected_row["Category"]))
            edit_amount = st.number_input("Edit Amount (PKR)", min_value=0.0, value=float(selected_row["Amount"]))
            edit_notes = st.text_area("Edit Notes", selected_row["Notes"] if pd.notna(selected_row["Notes"]) else "")
            col_edit, col_delete = st.columns(2)
            edit_submit = col_edit.form_submit_button("Update Transaction")
            delete_submit = col_delete.form_submit_button("Delete Transaction")
            
            if edit_submit:
                if edit_description.strip():
                    percent_used = (edit_amount / BUDGETS[edit_category] * 100) if BUDGETS[edit_category] > 0 else 0
                    st.session_state.transactions.loc[
                        st.session_state.transactions["Sr. No"] == sr_no,
                        ["Receiving Date", "Payment Method", "Description", "Category", "Amount", "% of Funds Used", "Notes"]
                    ] = [
                        edit_date, edit_payment_method, edit_description, edit_category,
                        edit_amount, round(percent_used, 2), edit_notes
                    ]
                    save_transactions()
                    st.success("Transaction updated!")
                    st.rerun()
                else:
                    st.error("Description cannot be empty!")
            
            if delete_submit:
                st.session_state.transactions = st.session_state.transactions[
                    st.session_state.transactions["Sr. No"] != sr_no
                ]
                st.session_state.transactions["Sr. No"] = range(1, len(st.session_state.transactions) + 1)
                save_transactions()
                st.success("Transaction deleted!")
                st.rerun()
    
    # Summary table
    st.subheader("Funds Summary")
    summary_df = calculate_summary(st.session_state.transactions)
    st.dataframe(summary_df, use_container_width=True)
    
    # Visualizations
    st.subheader("Visualizations")
    view_type = st.selectbox("View Funds By", ["Total", "Yearly", "Quarterly"])
    
    # Pie chart for category spending
    pie_fig = px.pie(summary_df[:-1], values="Used (PKR)", names="Category", 
                     title="Category-wise Funds Usage", color_discrete_sequence=px.colors.sequential.Greens)
    pie_fig.update_layout({"paper_bgcolor": "black", "plot_bgcolor": "black", "font_color": "white"})
    st.plotly_chart(pie_fig)
    
    # Bar chart for quarterly/yearly usage
    if not st.session_state.transactions.empty:
        df = st.session_state.transactions.copy()
        df["Year"] = df["Receiving Date"].dt.year
        if view_type == "Quarterly":
            df["Quarter"] = df["Receiving Date"].dt.quarter
            group_df = df.groupby(["Year", "Quarter", "Category"])["Amount"].sum().reset_index()
            group_df["Period"] = group_df["Year"].astype(str) + " Q" + group_df["Quarter"].astype(str)
            bar_fig = px.bar(group_df, x="Period", y="Amount", color="Category", 
                             title="Funds Usage by Quarter", color_discrete_sequence=px.colors.sequential.Greens)
        else:
            group_df = df.groupby(["Year", "Category"])["Amount"].sum().reset_index()
            bar_fig = px.bar(group_df, x="Year", y="Amount", color="Category", 
                             title="Funds Usage by Year", color_discrete_sequence=px.colors.sequential.Greens)
        bar_fig.update_layout({"paper_bgcolor": "black", "plot_bgcolor": "black", "font_color": "white"})
        st.plotly_chart(bar_fig)
    
    # Export to PDF and CSV
    st.subheader("Export")
    if not st.session_state.transactions.empty:
        col_pdf, col_csv = st.columns(2)
        with col_pdf:
            export_to_pdf(st.session_state.transactions)
        with col_csv:
            download_csv()

# Run app only if main
if __name__ == "__main__":
    st.write("")
```

### Deployment Instructions
1. **Update Your Repository**:
   - Replace `app.py` (or `maincode.py`) with the updated code above.
   - Ensure `requirements.txt` includes:
     ```
     streamlit
     pandas
     plotly
     reportlab
     ```
   - Add a `.gitignore` file to exclude `transactions.csv`:
     ```
     transactions.csv
     ```
   - If you need to initialize `transactions.csv` for the first deployment, include an empty CSV with headers:
     ```
     Sr. No,Receiving Date,Payment Method,Description,Category,Amount,% of Funds Used,Notes
     ```
   - Push the changes to your GitHub repository.

2. **Redeploy on Streamlit Cloud**:
   - Log in to [Streamlit Cloud](https://cloud.streamlit.io).
   - Go to “Manage app” for your app and trigger a redeploy.
   - Verify that the app loads existing transactions from `transactions.csv` (if it exists in the cloud environment).

3. **Test the App**:
   - Access the app using the Streamlit Cloud URL.
   - Log in with username `bano` and password `pso2025`.
   - Add a test transaction and use the “Download Transactions CSV” button to verify that transactions are saved correctly.
   - Check that existing transactions persist after redeployment.

### Recommendations
- **Exclude `transactions.csv` from GitHub**: Add it to `.gitignore` to prevent accidental overwrites. This ensures that transactions entered via the app are preserved in the Streamlit Cloud environment.
- **Regular Backups**: Use the new “Download Transactions CSV” button to periodically back up `transactions.csv` to your local machine.
- **Monitor Logs**: After redeployment, check Streamlit Cloud logs for any errors related to `transactions.csv` or other issues.

If you’re concerned about specific transactions or need help checking the current state of `transactions.csv` in Streamlit Cloud, let me know, and I can guide you on accessing or debugging it!
