import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("ROI Analysis")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]

    st.markdown("### 💰 Adjusted ROI: Including O&M, Degradation, and Asset Lifetime")

    # Inputs
    capex_per_mw = st.sidebar.number_input("CapEx (£/MW)", 500000, 3000000, 1000000, step=100000)
    capacity_mw = st.sidebar.slider("Installed Capacity (MW)", 10, 300, 100, step=10)
    om_cost_per_mwh = st.sidebar.number_input("O&M Cost (£/MWh)", 0, 100, 15)
    degradation_rate = st.sidebar.slider("Annual Degradation Rate (%)", 0.0, 5.0, 1.0, step=0.1) / 100
    asset_life = st.sidebar.slider("Project Lifetime (Years)", 5, 40, 25)

    # Base values
    project_cost = capex_per_mw * capacity_mw
    annual_gen = df["CFD_Generation_MWh"].mean()

    def discounted_output(year):
        return annual_gen * ((1 - degradation_rate) ** (year - 1))

    # Simulate adjusted revenue with degradation and O&M
    sim_data = []
    for ref in df["Reference_Type"].unique():
        total_revenue = 0
        total_cost = project_cost
        for year in range(1, asset_life + 1):
            avg_price = df[df["Reference_Type"] == ref]["Strike_Price_GBP_Per_MWh"].mean()
            output = discounted_output(year)
            rev = avg_price * output
            om_cost = om_cost_per_mwh * output
            total_revenue += rev
            total_cost += om_cost
        roi = (total_revenue - total_cost) / total_cost
        sim_data.append({"Reference_Type": ref, "Revenue": total_revenue, "Cost": total_cost, "ROI": roi})

    result_df = pd.DataFrame(sim_data)
    result_df["ROI_Label"] = result_df["ROI"].apply(lambda x: f"{x:.1%}")

    # Plot revenue
    st.subheader("Total Revenue over Lifetime (with Degradation)")
    fig1 = px.bar(result_df, x="Reference_Type", y="Revenue", text="Revenue", color="Reference_Type")
    fig1.update_layout(yaxis_title="Total Revenue (£)", height=400)
    st.plotly_chart(fig1)

    # Plot ROI
    st.subheader("ROI Including O&M + Degradation")
    fig2 = px.bar(result_df, x="Reference_Type", y="ROI", text="ROI_Label", color="Reference_Type")
    fig2.update_layout(yaxis_title="Return on Investment", height=400)
    fig2.update_traces(textposition="outside")
    st.plotly_chart(fig2)

    st.markdown("""
    ### 🔍 Insight:
    - **ROI now accounts for ongoing O&M and performance loss over time.**
    - A longer asset life improves ROI but increases sensitivity to degradation.
    - Use this tool to compare net profitability under realistic lifecycle conditions.
    """)