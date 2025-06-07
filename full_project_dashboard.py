import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page settings
st.set_page_config(page_title="iFlex Sleeving Dashboard", layout="wide")

# Title
st.title("📊 iFlex Sleeving Dashboard")

# Load Excel file safely
try:
    df = pd.read_excel("project_data.xlsx", sheet_name="Dash", header=0)
    df.columns = df.columns.str.strip()  # Remove spaces from headers
    st.write("✅ Columns found:", df.columns.tolist())  # Debug print
except FileNotFoundError:
    st.error("❌ Error: 'project_data.xlsx' not found. Please make sure the file is in the same directory.")
    st.stop()
except Exception as e:
    st.error(f"❌ Unexpected error: {e}")
    st.stop()

# Ensure 'Date' column exists and is datetime
if "Date" in df.columns:
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    except Exception as e:
        st.error(f"❌ Failed to convert 'Date' to datetime: {e}")
        st.stop()
else:
    st.error("❌ Column 'Date' not found in the uploaded Excel file.")
    st.stop()

# Ensure 'Road Name' column exists
if "Road Name" not in df.columns:
    st.error("❌ Column 'Road Name' not found in the uploaded Excel file.")
    st.stop()

# Filter by Road Name
road_names = df["Road Name"].dropna().unique().tolist()
selected_roads = st.multiselect("Filter by Road Name", road_names, default=road_names)

filtered_df = df[df["Road Name"].isin(selected_roads)]

# Key Metrics
st.header("📌 Key Metrics")
total_assets = len(filtered_df)
total_iflex = filtered_df["Estimated Cost - iFlex (£)"].sum()
total_actual = filtered_df["Actual Cost"].sum()
cost_saved_pct = ((total_iflex - total_actual) / total_iflex * 100) if total_iflex else 0

installation_time = filtered_df.get("Installation Time - iFlex (hrs)", pd.Series([0]*len(filtered_df))).sum()
time_saved_pct = ((installation_time - installation_time * 0.13) / installation_time * 100) if installation_time else 0

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Assets", total_assets)
col2.metric("Total iFlex Cost", f"£{total_iflex:,.2f}")
col3.metric("Total Actual Cost", f"£{total_actual:,.2f}")
col4.metric("Cost Saved %", f"{cost_saved_pct:.1f}%")
col5.metric("Time Saved %", f"{time_saved_pct:.1f}%")

# Monthly Trend Chart
st.subheader("📈 Monthly Cost Trend")
if not filtered_df.empty:
    monthly_summary = filtered_df.groupby(filtered_df["Date"].dt.to_period("M")).agg({
        "Estimated Cost - iFlex (£)": "sum",
        "Actual Cost": "sum"
    }).reset_index()
    monthly_summary["Date"] = monthly_summary["Date"].dt.to_timestamp()

    fig, ax = plt.subplots()
    ax.bar(monthly_summary["Date"], monthly_summary["Estimated Cost - iFlex (£)"], label="iFlex Cost", color="skyblue")
    ax.bar(monthly_summary["Date"], monthly_summary["Actual Cost"], label="Actual Cost", color="orange", bottom=0)
    ax.set_ylabel("Cost (£)")
    ax.set_title("Monthly Cost Trend")
    ax.legend()
    st.pyplot(fig)
else:
    st.warning("No data available for selected filters.")

# Daily Summary Table
st.subheader("📅 Daily Summary Table")
if not filtered_df.empty:
    display_columns = ["Date", "Estimated Cost - iFlex (£)", "Actual Cost", 
                       "Installation Time - iFlex (hrs)", "Total Length (m)", 
                       "Cost Difference (£)", "Savings %"]
    
    if "Cost Difference (£)" not in filtered_df.columns:
        filtered_df["Cost Difference (£)"] = filtered_df["Estimated Cost - iFlex (£)"] - filtered_df["Actual Cost"]
    if "Savings %" not in filtered_df.columns:
        filtered_df["Savings %"] = ((filtered_df["Cost Difference (£)"] / filtered_df["Estimated Cost - iFlex (£)"]) * 100).round(2)
    
    st.dataframe(filtered_df[display_columns])
else:
    st.warning("No data to display in table.")
