import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Supply Chain AI Planner", layout="wide")

st.title("📦 Supply Chain Planning & Control System")

# -----------------------------
# SAMPLE DATA (EDITABLE BASE)
# -----------------------------
sales_data = pd.DataFrame({
    "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
    "Sales": [400,450,520,600,680,710]
})

inventory_data = {
    "TShirt": 300,
    "Shoes": 150,
    "Hat": 80
}

suppliers = pd.DataFrame({
    "Supplier": ["A","B","C"],
    "Cost": [10,8,9],
    "LeadTime": [5,8,6],
    "Reliability": [95,80,90]
})

# -----------------------------
# SIDEBAR
# -----------------------------
menu = st.sidebar.selectbox(
    "Navigation",
    ["Forecasting", "Inventory", "Suppliers", "KPIs", "AI Assistant"]
)

# =========================================================
# FORECASTING (IMPROVED + EDITABLE + MOVING AVERAGE)
# =========================================================
if menu == "Forecasting":
    st.header("📊 Demand Forecasting Module")

    growth = st.slider("Expected Growth %", 0, 50, 10)

    use_ma = st.checkbox("Use Moving Average (better accuracy)")

    sales = sales_data["Sales"].values

    # Simple growth model
    growth_forecast = sales * (1 + growth/100)

    # Moving average model
    if use_ma:
        ma = np.convolve(sales, np.ones(3)/3, mode="valid")
        ma = np.append([sales[0], sales[1]], ma)
        forecast = ma
    else:
        forecast = growth_forecast

    df = pd.DataFrame({
        "Month": sales_data["Month"],
        "Sales": sales,
        "Forecast": forecast
    })

    st.dataframe(df)

    fig = px.line(df, x="Month", y=["Sales","Forecast"])
    st.plotly_chart(fig, use_container_width=True)

    st.success(f"Next Month Forecast: {np.mean(forecast):.0f}")

# =========================================================
# INVENTORY (FULL EDITABLE LOGIC)
# =========================================================
if menu == "Inventory":
    st.header("📦 Inventory Planning Module")

    product = st.selectbox("Product", list(inventory_data.keys()))

    stock = st.number_input("Current Stock", value=inventory_data[product])

    lead_time = st.number_input("Lead Time (days)", value=5)

    demand = st.number_input("Daily Demand", value=20)

    service_level = st.slider("Service Level Factor", 0.1, 1.0, 0.5)

    safety_stock = demand * lead_time * service_level
    reorder_point = demand * lead_time + safety_stock

    col1, col2 = st.columns(2)

    col1.metric("Safety Stock", f"{safety_stock:.0f}")
    col2.metric("Reorder Point", f"{reorder_point:.0f}")

    if stock < reorder_point:
        st.error("🔴 REORDER REQUIRED")
    else:
        st.success("🟢 STOCK OK")

    holding_cost = st.number_input("Holding Cost per unit", value=2)

    eoq = np.sqrt((2 * demand * 100) / holding_cost)

    st.info(f"EOQ (Optimal Order Quantity): {eoq:.0f}")

# =========================================================
# SUPPLIERS (EDITABLE + SCORING MODEL)
# =========================================================
if menu == "Suppliers":
    st.header("🚚 Supplier Management Module")

    df = suppliers.copy()

    st.subheader("Edit Supplier Data")
    edited_df = st.data_editor(df, num_rows="dynamic")

    edited_df["Score"] = (
        edited_df["Reliability"] * 0.7
        - edited_df["LeadTime"] * 0.3
        - edited_df["Cost"] * 0.1
    )

    st.dataframe(edited_df)

    best_supplier = edited_df.loc[edited_df["Score"].idxmax(), "Supplier"]

    st.success(f"Best Supplier Recommendation: {best_supplier}")

    fig = px.bar(edited_df, x="Supplier", y="Score")
    st.plotly_chart(fig, use_container_width=True)

# =========================================================
# KPI DASHBOARD (REALISTIC + DYNAMIC INPUTS)
# =========================================================
if menu == "KPIs":
    st.header("📈 KPI Dashboard")

    actual = st.number_input("Actual Sales", value=700)
    forecast = st.number_input("Forecast Sales", value=720)

    inventory = st.number_input("Average Inventory", value=300)
    cogs = st.number_input("COGS", value=2400)

    on_time = st.number_input("On-time Deliveries", value=95)
    total_orders = st.number_input("Total Orders", value=100)

    # KPIs
    forecast_accuracy = 1 - abs(actual - forecast) / forecast
    inventory_turnover = cogs / inventory
    service_level = on_time / total_orders

    stockout_rate = st.slider("Stockout Rate %", 0.0, 0.2, 0.03)
    supplier_reliability = st.slider("Supplier Reliability %", 0.0, 1.0, 0.94)

    col1, col2, col3 = st.columns(3)

    col1.metric("Forecast Accuracy", f"{forecast_accuracy*100:.1f}%")
    col2.metric("Inventory Turnover", f"{inventory_turnover:.2f}")
    col3.metric("Service Level", f"{service_level*100:.1f}%")

    st.metric("Supplier Reliability", f"{supplier_reliability*100:.1f}%")

    risk = "Low"
    if stockout_rate > 0.05:
        risk = "High"

    st.subheader("Risk Assessment")
    st.info(f"Supply Chain Risk Level: {risk}")

# =========================================================
# AI ASSISTANT (DECISION SUPPORT)
# =========================================================
if menu == "AI Assistant":
    st.header("🤖 AI Decision Support System")

    stock = st.number_input("Current Stock", 100)
    forecast = st.number_input("Forecast Demand", 200)
    lead_time = st.number_input("Supplier Lead Time", 5)
    demand_trend = st.slider("Demand Trend %", -30, 50, 10)

    st.subheader("AI Recommendations")

    if stock < forecast:
        st.warning("🔴 Increase inventory to avoid stockout risk.")

    if lead_time > 7:
        st.warning("🔴 Consider switching supplier (high lead time).")

    if stock > forecast * 1.5:
        st.info("🟡 Overstock risk detected.")

    if demand_trend > 20:
        st.success("📈 High demand growth expected → increase procurement.")
