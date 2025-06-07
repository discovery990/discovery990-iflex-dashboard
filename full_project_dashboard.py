import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Page settings
st.set_page_config(page_title="iFlex Sleeving Dashboard", layout="wide")

# Title
st.title("📊 iFlex Sleeving Dashboard")

# Load Excel file safely
try:
    df = pd.read_excel("project_data.xlsx")
except FileNotFoundError:
    st.error("❌ Error: 'project_data.xlsx' not found. Please make sure the file is in the same directory.")
    st.stop()

# Ensure 'Date' column exists and is datetime
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
else:
    st.error("❌ Column 'Date' not found in the uploaded Excel file.")
    st.stop()

# Ensure 'Road Name' column exists
if "Road Name" not in df.columns:
    st.error("❌ Column 'Road Name' not found in the data.")
    st.stop()

# Filter by Road Name
road_names = df["Road Name"].dropna().unique().tolist()
selected_roads = st.multiselect("Filter by Road Name", options=road_names, default=road_names)

filtered_df = df[df["Road Name"].isin(selected_roads)]

# Key Metrics
st.markdown("### 📌 Key Metrics")
total_assets = len(filtered_df)
total_iflex_cost = filtered_df["Estimated Cost - iFlex (£)"].sum()
total_actual_cost = filtered_df["Actual Cost"].sum()

col1, col2, col3 = st.columns(3)
col1.metric("Total Assets", f"{total_assets}")
col2.metric("Total iFlex Cost", f"£{total_iflex_cost:,.2f}")
col3.metric("Total Actual Cost", f"£{total_actual_cost:,.2f}")

# Cost & Time Savings %
try:
    total_epoxy_cost = filtered_df["Estimated Cost - Epoxy (£)"].sum()
    cost_saved_pct = ((total_epoxy_cost - total_iflex_cost) / total_epoxy_cost) * 100 if total_epoxy_cost else 0

    total_iflex_time = filtered_df["Installation Time - iFlex (hrs)"].sum()
    total_epoxy_time = filtered_df["Installation Time - Epoxy (hrs)"].sum()
    time_saved_pct = ((total_epoxy_time - total_iflex_time) / total_epoxy_time) * 100 if total_epoxy_time else 0

    col4, col5 = st.columns(2)
    col4.metric("Cost Saved %", f"{cost_saved_pct:.1f}%")
    col5.metric("Time Saved %", f"{time_saved_pct:.1f}%")
except:
    st.warning("⚠️ Could not calculate cost/time savings due to missing columns.")

# Total Length by Road
st.markdown("### 📏 Total Sleeved Length by Road")
if "Total Length (m)" in filtered_df.columns:
    total_length_chart = (
        filtered_df.groupby("Road Name")["Total Length (m)"]
        .sum()
        .sort_values(ascending=False)
    )
    st.bar_chart(total_length_chart)
else:
    st.warning("Missing column 'Total Length (m)' for length chart.")

# Optional: Daily Summary Table
st.markdown("### 📅 Daily Summary Table")
if "Day" in filtered_df.columns:
    st.dataframe(filtered_df.groupby("Day").agg({
        "Estimated Cost - iFlex (£)": "sum",
        "Actual Cost": "sum",
        "Installation Time - iFlex (hrs)": "sum",
        "Total Length (m)": "sum"
    }).round(2))
else:
    st.dataframe(filtered_df)

