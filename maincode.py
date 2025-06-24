import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
USERNAME = "khizar"
PASSWORD = "waves123"
EXCEL_FILE = "transactions.xlsx"import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
USERNAME = "khizar"
PASSWORD = "waves123"
EXCEL_FILE = "transactions.xlsx"

CATEGORY_BUDGET = {
    "Marketing/Advertisement": 3000000,
    "Gear and Expenses": 500000,
    "PSO Fuel Card": 500000,
    "Tournament Winning Prize": 1000000,
    "International Tournament Support": 1000000
}

# ----------------- UTILITIES ------------------

def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Method"])
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def split_budget():
    split = {}
    for cat, total in CATEGORY_BUDGET.items():
        split[cat] = {
            "Year 1": total / 2,
            "Year 2": total / 2,
            "Total": total
        }
    return split

def determine_year(date):
    year1 = datetime.datetime.now().year
    return "Year 1" if pd.to_datetime(date).year == year1 else "Year 2"

def format_currency(value):
    return f"PKR {value:,.0f}"

# ---------------- LOGIN ------------------

def authenticate():
    st.title("🏦 Bano Butt Fund Tracker")
    st.subheader("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ------------------

def main_app():
    st.title("📊 Bano Butt x PSO Fund Dashboard")
    tabs = st.tabs(["➕ Add Transaction", "📅 Yearly Summary", "📘 Total Summary", "📈 Visualizations"])
    
    df = load_data()
    budget = split_budget()

    # Add transaction tab
    with tabs[0]:
        st.header("➕ Add New Transaction")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date")
            description = st.text_input("Description")
            amount = st.number_input("Amount (PKR)", min_value=0)
            category = st.selectbox("Category", list(CATEGORY_BUDGET.keys()))
            method = st.selectbox("Method", ["Bank Transfer", "Cheque", "Fuel Card Update"])
            submitted = st.form_submit_button("Submit")

            if submitted:
                new = pd.DataFrame([{
                    "Date": date,
                    "Description": description,
                    "Amount": amount,
                    "Category": category,
                    "Method": method
                }])
                df = pd.concat([df, new], ignore_index=True)
                save_data(df)
                st.success("✅ Transaction added successfully.")

    # Yearly summary tab
    with tabs[1]:
        st.header("📅 Fund Summary by Year")
        df["Year"] = df["Date"].apply(lambda x: determine_year(x))

        for year in ["Year 1", "Year 2"]:
            st.subheader(year)
            year_df = df[df["Year"] == year]
            group = year_df.groupby("Category")["Amount"].sum().to_dict()

            for cat in CATEGORY_BUDGET:
                used = group.get(cat, 0)
                limit = CATEGORY_BUDGET[cat] / 2
                remaining = limit - used
                pct = (used / limit) * 100 if limit > 0 else 0

                col1, col2 = st.columns([2, 5])
                col1.markdown(f"**{cat}**")
                col2.markdown(f"{format_currency(used)} / {format_currency(limit)} ({pct:.1f}%)")
                st.progress(min(pct/100, 1.0))

    # Total summary tab
    with tabs[2]:
        st.header("📘 Total Summary (2 Years Combined)")
        total_df = df.copy()
        total_group = total_df.groupby("Category")["Amount"].sum().to_dict()

        summary_data = []
        for cat in CATEGORY_BUDGET:
            total_budget = CATEGORY_BUDGET[cat]
            used = total_group.get(cat, 0)
            remaining = total_budget - used
            pct = (used / total_budget) * 100 if total_budget > 0 else 0

            summary_data.append({
                "Category": cat,
                "Budget": format_currency(total_budget),
                "Used": format_currency(used),
                "Remaining": format_currency(remaining),
                "Used %": f"{pct:.1f}%"
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

    # Visualization tab
    with tabs[3]:
        st.header("📈 Fund Usage Visualization")
        df["Year"] = df["Date"].apply(lambda x: determine_year(x))
        year = st.selectbox("Select Year", ["Year 1", "Year 2"])
        year_df = df[df["Year"] == year]
        group = year_df.groupby("Category")["Amount"].sum()

        # Pie chart
        st.subheader("Spending Breakdown (Pie Chart)")
        fig1, ax1 = plt.subplots()
        ax1.pie(group, labels=group.index, autopct='%1.1f%%', startangle=140)
        ax1.axis('equal')import streamlit as st
import pandas as pd
import datetime
import os
import matplotlib.pyplot as plt

# ---------------- CONFIG ----------------
USERNAME = "khizar"
PASSWORD = "waves123"
EXCEL_FILE = "transactions.xlsx"

CATEGORY_BUDGET = {
    "Marketing/Advertisement": 3000000,
    "Gear and Expenses": 500000,
    "PSO Fuel Card": 500000,
    "Tournament Winning Prize": 1000000,
    "International Tournament Support": 1000000
}

# ----------------- UTILITIES ------------------

def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Method"])
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def split_budget():
    split = {}
    for cat, total in CATEGORY_BUDGET.items():
        split[cat] = {
            "Year 1": total / 2,
            "Year 2": total / 2,
            "Total": total
        }
    return split

def determine_year(date):
    year1 = datetime.datetime.now().year
    return "Year 1" if pd.to_datetime(date).year == year1 else "Year 2"

def format_currency(value):
    return f"PKR {value:,.0f}"

# ---------------- LOGIN ------------------

def authenticate():
    st.title("🏦 Bano Butt Fund Tracker")
    st.subheader("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# ---------------- MAIN APP ------------------

def main_app():
    st.title("📊 Bano Butt x PSO Fund Dashboard")
    tabs = st.tabs(["➕ Add Transaction", "📅 Yearly Summary", "📘 Total Summary", "📈 Visualizations"])
    
    df = load_data()
    budget = split_budget()

    # Add transaction tab
    with tabs[0]:
        st.header("➕ Add New Transaction")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date")
            description = st.text_input("Description")
            amount = st.number_input("Amount (PKR)", min_value=0)
            category = st.selectbox("Category", list(CATEGORY_BUDGET.keys()))
            method = st.selectbox("Method", ["Bank Transfer", "Cheque", "Fuel Card Update"])
            submitted = st.form_submit_button("Submit")

            if submitted:
                new = pd.DataFrame([{
                    "Date": date,
                    "Description": description,
                    "Amount": amount,
                    "Category": category,
                    "Method": method
                }])
                df = pd.concat([df, new], ignore_index=True)
                save_data(df)
                st.success("✅ Transaction added successfully.")

    # Yearly summary tab
    with tabs[1]:
        st.header("📅 Fund Summary by Year")
        df["Year"] = df["Date"].apply(lambda x: determine_year(x))

        for year in ["Year 1", "Year 2"]:
            st.subheader(year)
            year_df = df[df["Year"] == year]
            group = year_df.groupby("Category")["Amount"].sum().to_dict()

            for cat in CATEGORY_BUDGET:
                used = group.get(cat, 0)
                limit = CATEGORY_BUDGET[cat] / 2
                remaining = limit - used
                pct = (used / limit) * 100 if limit > 0 else 0

                col1, col2 = st.columns([2, 5])
                col1.markdown(f"**{cat}**")
                col2.markdown(f"{format_currency(used)} / {format_currency(limit)} ({pct:.1f}%)")
                st.progress(min(pct/100, 1.0))

    # Total summary tab
    with tabs[2]:
        st.header("📘 Total Summary (2 Years Combined)")
        total_df = df.copy()
        total_group = total_df.groupby("Category")["Amount"].sum().to_dict()

        summary_data = []
        for cat in CATEGORY_BUDGET:
            total_budget = CATEGORY_BUDGET[cat]
            used = total_group.get(cat, 0)
            remaining = total_budget - used
            pct = (used / total_budget) * 100 if total_budget > 0 else 0

            summary_data.append({
                "Category": cat,
                "Budget": format_currency(total_budget),
                "Used": format_currency(used),
                "Remaining": format_currency(remaining),
                "Used %": f"{pct:.1f}%"
            })

        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)

    # Visualization tab
    with tabs[3]:
        st.header("📈 Fund Usage Visualization")
        df["Year"] = df["Date"].apply(lambda x: determine_year(x))
        year = st.selectbox("Select Year", ["Year 1", "Year 2"])
        year_df = df[df["Year"] == year]
        group = year_df.groupby("Category")["Amount"].sum()

        # Pie chart
        st.subheader("Spending Breakdown (Pie Chart)")
        fig1, ax1 = plt.subplots()
        ax1.pie(group, labels=group.index, autopct='%1.1f%%', startangle=140)
        ax1.axis('equal')
        st.pyplot(fig1)

        # Bar chart
        st.subheader("Spending Breakdown (Bar Chart)")
        fig2, ax2 = plt.subplots()
        ax2.bar(group.index, group.values, color='mediumseagreen')
        ax2.set_ylabel("Amount (PKR)")
        ax2.set_xticklabels(group.index, rotation=45, ha='right')
        st.pyplot(fig2)

# ---------------- ENTRY POINT ------------------

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    authenticate()
else:
    main_app()

        st.pyplot(fig1)

        # Bar chart
        st.subheader("Spending Breakdown (Bar Chart)")
        fig2, ax2 = plt.subplots()
        ax2.bar(group.index, group.values, color='mediumseagreen')
        ax2.set_ylabel("Amount (PKR)")
        ax2.set_xticklabels(group.index, rotation=45, ha='right')
        st.pyplot(fig2)

# ---------------- ENTRY POINT ------------------

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    authenticate()
else:
    main_app()


CATEGORY_BUDGET = {
    "Marketing/Advertisement": 3000000,
    "Gear and Expenses": 500000,
    "PSO Fuel Card": 500000,
    "Tournament Winning Prize": 1000000,
    "International Tournament Support": 1000000
}

# ------------- SETUP -------------------

def load_data():
    if not os.path.exists(EXCEL_FILE):
        df = pd.DataFrame(columns=["Date", "Description", "Amount", "Category", "Method"])
        df.to_excel(EXCEL_FILE, index=False)
    return pd.read_excel(EXCEL_FILE)

def save_data(df):
    df.to_excel(EXCEL_FILE, index=False)

def split_budget():
    split = {}
    for cat, total in CATEGORY_BUDGET.items():
        split[cat] = {
            "Year 1": total / 2,
            "Year 2": total / 2,
            "Total": total
        }
    return split

def determine_year(date):
    base_year = datetime.datetime.now().year
    return "Year 1" if date.year == base_year else "Year 2"

def authenticate():
    st.title("🏦 Bano Butt Fund Tracker")
    st.subheader("Login")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if user == USERNAME and pwd == PASSWORD:
            st.session_state["auth"] = True
            st.rerun()
        else:
            st.error("Invalid credentials")

# ----------------- MAIN APP ---------------------

def main_app():
    st.sidebar.title("📊 Dashboard")
    tab = st.sidebar.radio("Go to", ["➕ Add Transaction", "📅 Yearly Summary", "📈 Visualizations"])

    df = load_data()
    budget = split_budget()

    # ------- ADD TRANSACTION -------
    if tab == "➕ Add Transaction":
        st.header("Add New Transaction")
        with st.form("entry_form", clear_on_submit=True):
            date = st.date_input("Date")
            description = st.text_input("Description")
            amount = st.number_input("Amount (PKR)", min_value=0)
            category = st.selectbox("Category", list(CATEGORY_BUDGET.keys()))
            method = st.selectbox("Method", ["Bank Transfer", "Cheque", "Fuel Card Update"])
            submitted = st.form_submit_button("Submit")

            if submitted:
                new = pd.DataFrame([{
                    "Date": date,
                    "Description": description,
                    "Amount": amount,
                    "Category": category,
                    "Method": method
                }])
                df = pd.concat([df, new], ignore_index=True)
                save_data(df)
                st.success("Transaction added successfully.")

    # ------- YEARLY SUMMARY -------
    elif tab == "📅 Yearly Summary":
        st.header("Fund Summary by Year")
        df["Year"] = df["Date"].apply(lambda x: determine_year(pd.to_datetime(x)))

        summary = {}
        for year in ["Year 1", "Year 2"]:
            st.subheader(year)
            year_df = df[df["Year"] == year]
            group = year_df.groupby("Category")["Amount"].sum().to_dict()

            for cat in CATEGORY_BUDGET:
                used = group.get(cat, 0)
                limit = CATEGORY_BUDGET[cat] / 2
                remaining = limit - used
                pct = (used / limit) * 100 if limit > 0 else 0

                st.markdown(f"**{cat}**")
                st.write(f"Used: PKR {used:,.0f} / {limit:,.0f} ({pct:.2f}%)")
                st.progress(min(pct/100, 1.0))

    # ------- VISUALIZATION -------
    elif tab == "📈 Visualizations":
        st.header("Visualization - Fund Usage")

        df["Year"] = df["Date"].apply(lambda x: determine_year(pd.to_datetime(x)))
        year = st.selectbox("Select Year", ["Year 1", "Year 2"])
        year_df = df[df["Year"] == year]

        group = year_df.groupby("Category")["Amount"].sum()
        st.subheader("Spending per Category")

        fig1, ax1 = plt.subplots()
        ax1.pie(group, labels=group.index, autopct='%1.1f%%', startangle=140)
        ax1.axis('equal')
        st.pyplot(fig1)

        st.subheader("Bar Chart")
        fig2, ax2 = plt.subplots()
        ax2.bar(group.index, group.values, color='skyblue')
        ax2.set_ylabel("Amount (PKR)")
        ax2.set_xticklabels(group.index, rotation=45, ha='right')
        st.pyplot(fig2)

# ----------------- ENTRY POINT -------------------

if "auth" not in st.session_state:
    st.session_state["auth"] = False

if not st.session_state["auth"]:
    authenticate()
else:
    main_app()
