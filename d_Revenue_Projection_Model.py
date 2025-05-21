
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

def main():
    st.title("Revenue Projection Model")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]

    base = df["Market_Reference_Price_GBP_Per_MWh"].mean()
    strike = df["Strike_Price_GBP_Per_MWh"].mean()
    gen = df["CFD_Generation_MWh"].mean()
    volatility = 10

    max_sims = st.sidebar.slider("Max Simulations", 100, 50000, 1000, step=100)
    sample_sizes = list(range(100, max_sims + 1, 100))

    results = {"Sample Size": [], "Strategy": [], "Mean Revenue": []}
    np.random.seed(42)

    for size in sample_sizes:
        tracker = {"CfD": [], "PPA": [], "Merchant": []}
        for _ in range(size):
            prices = np.random.normal(base, volatility, 25)
            rev = {
                "CfD": ((strike - prices) + prices).mean() * gen,
                "PPA": (prices.mean() - 2) * gen,
                "Merchant": prices.mean() * gen
            }
            for k in tracker:
                tracker[k].append(rev[k])

        for k in tracker:
            results["Sample Size"].append(size)
            results["Strategy"].append(k)
            results["Mean Revenue"].append(np.mean(tracker[k]))

    df_result = pd.DataFrame(results)

    st.subheader("Revenue vs Simulation Count (Bar Chart)")
    fig = px.bar(
        df_result,
        x="Sample Size",
        y="Mean Revenue",
        color="Strategy",
        barmode="group",
        height=500,
        template="plotly_dark"
    )
    fig.update_layout(
        xaxis_title="Number of Simulations",
        yaxis_title="Average Revenue (£)",
        legend_title="Strategy",
        bargap=0.15
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 🔍 Insight:")
    st.markdown("""
    - **CfD** shows high stability and converges rapidly with few simulations.
    - **PPA** and **Merchant** models vary more with volatility.
    - Use this chart to choose optimal simulation sample size.
    """)

if __name__ == "__main__":
    main()
