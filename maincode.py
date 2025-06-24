```python
import streamlit as st
import pandas as pd
import plotly.express as px
import json
from datetime import datetime

# Fixed budgets
BUDGETS = {
    "Marketing": 3000000,
    "Gear and Equipment": 500000,
    "PSO Fuel Card": 500000,
    "Winning Prize": 1000000,
    "International Tournament": 1000000
}

# JSON file for transactions
DATA_FILE = "data.json"

# Initialize session state for data
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'budgets' not in st.session_state:
    st.session_state.budgets = BUDGETS

# Function to save data to JSON
def save_data():
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump({
                'transactions': st.session_state.transactions,
                'budgets': st.session_state.budgets
            }, f, default=str)  # Convert datetime to string for JSON
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")

# Function to load data from JSON
def load_data():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                st.session_state.transactions = data.get('transactions', [])
                st.session_state.budgets = data.get('budgets', BUDGETS)
                # Convert transaction dates back to datetime
                for t in st.session_state.transactions:
                    t["Receiving Date"] = pd.to_datetime(t["Receiving Date"])
        else:
            st.session_state.transactions = []
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.session_state.transactions = []

# Load data on start
load_data()

# Convert transactions to DataFrame for processing
def get_transactions_df():
    df = pd.DataFrame(st.session_state.transactions)
    if not df.empty:
        df["Receiving Date"] = pd.to_datetime(df["Receiving Date"])
    return df

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

# Streamlit app
st.title("Bano Funds Tracker")

# Custom CSS for mobile-friendly black/green/white theme
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

# Add transaction form
with st.form("transaction_form"):
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
            transaction = {
                "Sr. No": len(st.session_state.transactions) + 1,
                "Receiving Date": date,
                "Payment Method": payment_method,
                "Description": description,
                "Category": category,
                "Amount": amount,
                "% of Funds Used": round(percent_used, 2),
                "Notes": notes
            }
            st.session_state.transactions.append(transaction)
            save_data()
            st.success("Transaction added!")
        else:
            st.error("Description cannot be empty!")

# Display transactions
st.subheader("Transaction Ledger")
df = get_transactions_df()
if not df.empty:
    st.dataframe(df, use_container_width=True)

    # Filters
    with st.expander("Apply Filters"):
        categories = ["All"] + list(BUDGETS.keys())
        selected_category = st.selectbox("Filter by Category", categories)
        payment_methods = ["All"] + list(df["Payment Method"].unique())
        selected_method = st.selectbox("Filter by Payment Method", payment_methods)
        date_range = st.date_input("Date Range", [df["Receiving Date"].min(), df["Receiving Date"].max()])

        if selected_category != "All":
            df = df[df["Category"] == selected_category]
        if selected_method != "All":
            df = df[df["Payment Method"] == selected_method]
        if date_range and len(date_range) == 2:
            df = df[(df["Receiving Date"] >= pd.to_datetime(date_range[0])) & 
                    (df["Receiving Date"] <= pd.to_datetime(date_range[1]))]

    # Display filtered transactions
    st.dataframe(df, use_container_width=True)

# Summary table
st.subheader("Funds Summary")
summary_df = calculate_summary(df)
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
if not df.empty:
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

# Deployment Instructions
"""
To deploy this app to Streamlit Cloud:
1. Update your GitHub repository:
   - Save this script as app.py.
   - Create requirements.txt with:
     streamlit
     pandas
     plotly
   - Add .gitignore with:
     data.json
   - Optionally include an empty data.json for first deployment.
2. Push changes to GitHub.
3. Deploy on Streamlit Cloud:
   - Log in to Streamlit Cloud (https://cloud.streamlit.io).
   - Connect your GitHub repository and select app.py as the main file.
   - Deploy the app and check logs for errors.
4. Test the app:
   - Access the app URL.
   - Add transactions and verify data persistence.
   - Check visualizations and summary table.
"""
```

### Key Differences from Latest Code
The original code differs from the latest version you’re using (`maincode.py`) in several ways, as your requirements evolved:
1. **Storage**: Uses JSON (`data.json`) instead of CSV (`transactions.csv`).
2. **No Login**: Lacks the username/password login (`bano`/`pso2025`) you later requested.
3. **Missing Features**:
   - No edit/delete transaction functionality.
   - No PDF export.
   - No CSV download button.
4. **Less Robust Error Handling**: Doesn’t handle invalid dates as robustly as the latest version (no `errors='coerce'` or logging for CSV issues).
5. **Dependencies**: Requires only `streamlit`, `pandas`, and `plotly` (no `reportlab` for PDF export).

### Why You Might Not Want to Use This Version
The original code is less feature-complete and less robust than the latest version you’re working with. Specifically:
- **CSV Storage**: You requested CSV storage for easier manual editing, which the latest code supports.
- **Login**: You added a requirement for a fixed username/password, which this code lacks.
- **Edit/Delete and Exports**: The latest code includes critical features like editing/deleting transactions and PDF/CSV exports, which are missing here.
- **Error Handling**: The original code doesn’t handle invalid dates or file errors as well, which could cause issues similar to the `ValueError` you faced earlier with date parsing.

I recommend sticking with the latest version (from my previous response, artifact ID `206a628f-efa8-4024-ab96-57d83afc668d`) unless you specifically need the JSON-based version for a particular reason (e.g., reverting to an earlier design). The latest version addresses all your requirements, includes robust error handling, and fixes the syntax issues (e.g., curly quotes) that caused problems.

### Deployment Instructions for This Code
If you want to test this original code:
1. **Update Your Repository**:
   - Save the code as `app.py`.
   - Create `requirements.txt`:
     ```
     streamlit
     pandas
     plotly
     ```
   - Add `.gitignore`:
     ```
     data.json
     ```
   - Optionally include an empty `data.json` (e.g., `{}`) for the first deployment.
   - Commit and push to your GitHub repository.

2. **Redeploy on Streamlit Cloud**:
   - Log in to [Streamlit Cloud](https://cloud.streamlit.io).
   - Go to “Manage app” and trigger a redeploy.
   - Check logs for errors.

3. **Test the App**:
   - Access the app URL (no login required).
   - Add transactions and verify they save to `data.json`.
   - Check the summary table and visualizations.

### Important Notes
- **Data Loss Risk**: If you switch to this JSON-based version, existing transactions in `transactions.csv` (from your current app) won’t be loaded, as this code uses `data.json`. To migrate data, you’d need to convert `transactions.csv` to the JSON format expected by this script, which I can help with if needed.
- **Recommendation**: Use the latest code unless you have a specific reason to revert (e.g., testing or preferring JSON storage). The latest version is more robust and includes all requested features.
- **Login**: This version has no login, unlike your current app. If you need the login feature (`bano`/`pso2025`), stick with the latest code.

If you want to proceed with this original code or need help migrating data from `transactions.csv` to `data.json`, let me know! Alternatively, if you’re still facing issues with the current `maincode.py` (e.g., syntax errors, deployment problems), please share the latest error logs or describe the specific problems, and I’ll help fix them to get your app running smoothly.
