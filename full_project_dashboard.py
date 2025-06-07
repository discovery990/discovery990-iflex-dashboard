import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

# Load data with fallback
@st.cache_data
def load_data():
    try:
        df = pd.read_excel("project data.xlsx", sheet_name="Dash")
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        else:
            st.error("Date column not found in uploaded data.")
        return df.dropna(subset=["Road Name"])
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

df = load_data()

# Sidebar filter
st.sidebar.title("Filter by Road Name")
road_names = df["Road Name"].unique().tolist()
selected_roads = st.sidebar.multiselect("Select Road(s)", road_names, default=road_names)
filtered_df = df[df["Road Name"].isin(selected_roads)]

st.title("📊 iFlex Sleeving Dashboard")

# Metric display
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Assets", len(filtered_df))
col2.metric("Total iFlex Cost", f"£{filtered_df['Estimated Cost - iFlex (£)'].sum():,.2f}")
col3.metric("Total Actual Cost", f"£{filtered_df['Actual Cost'].sum():,.2f}")

try:
    cost_saved = 100 * (filtered_df['Estimated Cost - Epoxy (£)'].sum() - filtered_df['Estimated Cost - iFlex (£)'].sum()) / filtered_df['Estimated Cost - Epoxy (£)'].sum()
    time_saved = 100 * (filtered_df['Installation Time - Epoxy (hrs)'].sum() - filtered_df['Installation Time - iFlex (hrs)'].sum()) / filtered_df['Installation Time - Epoxy (hrs)'].sum()
    col4.metric("Cost Saved %", f"{cost_saved:.1f}%")
    col5.metric("Time Saved %", f"{time_saved:.1f}%")
except Exception:
    pass

# Monthly cost trend chart
if "Date" in filtered_df.columns:
    cost_month = filtered_df.copy()
    cost_month["Month"] = cost_month["Date"].dt.to_period("M").astype(str)
    monthly = cost_month.groupby("Month").agg({
        "Estimated Cost - iFlex (£)": "sum",
        "Actual Cost": "sum"
    }).reset_index()

    st.subheader("📅 Monthly Cost Trend")
    fig, ax = plt.subplots()
    ax.bar(monthly["Month"], monthly["Estimated Cost - iFlex (£)"], label="iFlex Cost", color="skyblue")
    ax.bar(monthly["Month"], monthly["Actual Cost"], bottom=monthly["Estimated Cost - iFlex (£)"], label="Actual Cost", color="orange")
    ax.set_ylabel("Cost (£)")
    ax.set_xlabel("Month")
    ax.set_title("Monthly iFlex vs Actual Cost")
    ax.legend()
    st.pyplot(fig)

# Daily table with summary
st.subheader("📅 Daily Summary Table")
summary = filtered_df[[
    "Date", "Estimated Cost - iFlex (£)", "Actual Cost", "Installation Time - iFlex (hrs)", "Total Length (m)"
]].copy()
summary["Cost Difference (£)"] = summary["Estimated Cost - iFlex (£)"] - summary["Actual Cost"]
summary["Savings %"] = 100 * summary["Cost Difference (£)"] / summary["Estimated Cost - iFlex (£)"]
summary = summary.sort_values("Date")
st.dataframe(summary.reset_index(drop=True))

# Export download
try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        summary.to_excel(writer, index=False, sheet_name="Summary")
    st.download_button("📥 Download Summary as Excel", data=output.getvalue(), file_name="daily_summary.xlsx")
except Exception as e:
    st.warning(f"Export failed: {e}")
