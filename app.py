import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt

# Load Data
# -------------------------------
st.title("🌍 Geospatial Customer Insights Dashboard")

uploaded_file = st.file_uploader("Upload your customer CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("✅ Data loaded successfully!")
else:
    # Fallback to your sample CSV
    df = pd.read_csv("sample_customers_1000.csv")
    st.warning("⚠️ Using default sample data.")


# Sidebar Filters
st.sidebar.header("🔍 Filters")

states = df["State"].unique()
selected_state = st.sidebar.selectbox("Select State:", ["All"] + list(states))

if selected_state != "All":
    cities = df[df["State"] == selected_state]["City"].unique()
else:
    cities = df["City"].unique()
selected_city = st.sidebar.selectbox("Select City:", ["All"] + list(cities))

min_revenue = int(df["Revenue"].min())
max_revenue = int(df["Revenue"].max())
revenue_range = st.sidebar.slider(
    "Revenue Range:",
    min_value=min_revenue,
    max_value=max_revenue,
    value=(min_revenue, max_revenue)
)

# Filter data
filtered_df = df.copy()
if selected_state != "All":
    filtered_df = filtered_df[filtered_df["State"] == selected_state]
if selected_city != "All":
    filtered_df = filtered_df[filtered_df["City"] == selected_city]
filtered_df = filtered_df[
    (filtered_df["Revenue"] >= revenue_range[0]) &
    (filtered_df["Revenue"] <= revenue_range[1])
]

# Title
st.title("🌍 Customer Geospatial Dashboard")

# Summary Stats
st.subheader("📊 Summary Statistics")
st.write(f"**Total Customers:** {len(filtered_df)}")
st.write(f"**Total Revenue:** ₹{filtered_df['Revenue'].sum():,}")

# Data Table
st.subheader("📋 Filtered Data")
st.dataframe(filtered_df)

# Map
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium

# Load your CSV
df = pd.read_csv("sample_customers_1000.csv")

# Center the map
m = folium.Map(
    location=[20.5937, 78.9629],
    zoom_start=4,
    tiles="cartodbpositron"
)

marker_cluster = MarkerCluster().add_to(m)

for _, row in filtered_df.iterrows():
    folium.CircleMarker(
        location=[row["Latitude"], row["Longitude"]],
        radius=5,
        popup=f"<b>{row['CustomerName']}</b><br>Revenue: ₹{row['Revenue']}",
        color="blue",
        fill=True,
        fill_opacity=0.7
    ).add_to(marker_cluster)

# Show map
st_folium(m, width=900, height=600)

# Revenue by City
st.subheader("🏙️ Revenue by City")
city_revenue = filtered_df.groupby("City")["Revenue"].sum().sort_values(ascending=False)
st.bar_chart(city_revenue)

# Summarize revenue by city
revenue_by_city = (
    filtered_df.groupby("City")["Revenue"]
    .sum()
    .sort_values(ascending=False)
)

# Top and bottom cities
if not revenue_by_city.empty:
    top_city = revenue_by_city.idxmax()
    top_revenue = revenue_by_city.max()
    bottom_city = revenue_by_city.idxmin()
    bottom_revenue = revenue_by_city.min()

    st.subheader("🏆 Top & Bottom Revenue Locations")

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🌟 **Top City:** {top_city}\n\n💰 Revenue: ₹{top_revenue:,.2f}")
    with col2:
        st.warning(f"🔻 **Lowest City:** {bottom_city}\n\n💰 Revenue: ₹{bottom_revenue:,.2f}")

    # Business Tip
    st.info(
        f"💡 **Tip:** Consider launching targeted promotions in **{bottom_city}** to boost revenue. "
        f"Offering loyalty rewards or special discounts can help attract more customers."
    )
else:
    st.write("No revenue data available for the selected filters.")

# Ensure 'Date' column is datetime
df["Date"] = pd.date_range(start="2023-01-01", periods=len(df), freq="D")
filtered_df = df.copy()
if "Date" in filtered_df.columns:
    filtered_df["Date"] = pd.to_datetime(filtered_df["Date"], errors="coerce")

# Allow user to pick a city for trend
selected_city = st.selectbox(
    "📈 Select a City to View Monthly Revenue Trend:",
    options=sorted(filtered_df["City"].unique())
)

# Filter data for selected city
city_data = filtered_df[filtered_df["City"] == selected_city]

if not city_data.empty:
    # Group by Month
    city_data["Month"] = city_data["Date"].dt.to_period("M")
    monthly_revenue = (
        city_data.groupby("Month")["Revenue"]
        .sum()
        .sort_index()
    )

    # Plot trend
    st.subheader(f"📊 Monthly Revenue Trend - {selected_city}")
    fig_trend, ax_trend = plt.subplots()
    monthly_revenue.plot(kind="line", marker="o", ax=ax_trend)
    ax_trend.set_xlabel("Month")
    ax_trend.set_ylabel("Revenue (₹)")
    ax_trend.set_title(f"Revenue Trend for {selected_city}")
    plt.xticks(rotation=45)
    st.pyplot(fig_trend)
else:
    st.warning("No data available for this city.")

# -------------------------------
# 📄 Generate Insights Text
# -------------------------------
# Define summary variables for insights
total_customers = len(filtered_df)
total_revenue = filtered_df['Revenue'].sum()
max_revenue = revenue_by_city.max() if not revenue_by_city.empty else 0
min_revenue = revenue_by_city.min() if not revenue_by_city.empty else 0
business_tip = (
    f"Consider launching targeted promotions in {bottom_city} to boost revenue. "
    f"Offering loyalty rewards or special discounts can help attract more customers."
) if not revenue_by_city.empty else "No tip available."

insights_text = f"""
Business Insights Summary

Total Customers: {total_customers}
Total Revenue: ₹{total_revenue:,.2f}

Top City: {top_city} - Revenue ₹{max_revenue:,.2f}
Lowest City: {bottom_city} - Revenue ₹{min_revenue:,.2f}

Tip to Attract More Customers:
{business_tip}
"""

st.download_button(
    label="📄 Download Insights as Text",
    data=insights_text,
    file_name="business_insights_summary.txt",
    mime="text/plain"
)
