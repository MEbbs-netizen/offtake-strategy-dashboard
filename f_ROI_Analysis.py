import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def main():
    st.title("ROI Analysis")
    st.markdown("This section evaluates total revenue and ROI over the asset’s lifetime, factoring in:")
    st.markdown("- Annual degradation in output")
    st.markdown("- Ongoing O&M costs")
    st.markdown("- Reference market pricing")
    st.markdown("Adjust inputs in the sidebar to simulate different investment scenarios.")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]

    # Sidebar Inputs
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

    # Simulation
    sim_data = []
    for ref in df["Reference_Type"].unique():
        total_revenue = 0
        total_cost = project_cost
        for year in range(1, asset_life + 1):
            avg_price = df[df["Reference_Type"] == ref]["Strike_Price_GBP"].mean()
            mwh = discounted_output(year)
            total_revenue += avg_price * mwh
            total_cost += mwh * om_cost_per_mwh
        roi = (total_revenue - total_cost) / total_cost * 100
        sim_data.append({"Reference": ref, "ROI (%)": roi})

    result_df = pd.DataFrame(sim_data)
    st.subheader("ROI by Reference Pricing")
    st.dataframe(result_df)

    fig = px.bar(result_df, x="Reference", y="ROI (%)", color="ROI (%)", color_continuous_scale="Viridis")
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()
