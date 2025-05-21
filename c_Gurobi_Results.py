import streamlit as st
import pandas as pd
import numpy as np
from gurobipy import Model, GRB
import plotly.express as px

def main():
    st.title("Gurobi Optimization Results")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]

    base_price = df["Market_Reference_Price_GBP_Per_MWh"].mean()
    strike = df["Strike_Price_GBP_Per_MWh"].mean()
    gen = df["CFD_Generation_MWh"].mean()
    volatility = 10

    max_sims = st.slider("Max Number of Simulations", 1000, 50000, 5000, step=1000)
    step_size = 1000

    sample_sizes = list(range(step_size, max_sims + 1, step_size))
    np.random.seed(1)

    strategy_counts = []

    for size in sample_sizes:
        counts = {"CfD": 0, "PPA": 0, "Merchant": 0}
        for _ in range(size):
            prices = np.random.normal(base_price, volatility, 25)
            rev = {
                "CfD": ((strike - prices) + prices).mean() * gen,
                "PPA": (prices.mean() - 2) * gen,
                "Merchant": prices.mean() * gen
            }

            m = Model(); m.setParam("OutputFlag", 0)
            x = {k: m.addVar(vtype=GRB.BINARY, name=k) for k in rev}
            m.addConstr(sum(x.values()) == 1)
            m.setObjective(sum(x[k] * v for k, v in rev.items()), GRB.MAXIMIZE)
            m.optimize()
            chosen = [k for k in rev if x[k].X > 0.5][0]
            counts[chosen] += 1

        for strat, count in counts.items():
            strategy_counts.append({"Simulations": size, "Strategy": strat, "Count": count})

    df_results = pd.DataFrame(strategy_counts)

    st.subheader("Strategy Selection Trends vs Simulations")
    fig = px.line(df_results, x="Simulations", y="Count", color="Strategy", markers=True)
    fig.update_layout(
        title="Optimal Strategy Frequency Across Monte Carlo Runs",
        xaxis_title="Number of Simulations",
        yaxis_title="Count of Selections",
        height=500
    )
    st.plotly_chart(fig)

    st.markdown("""
    ### 💡 Insights:
    - **CfD dominates** under this price regime, showing up in nearly all simulation cases.
    - **PPA and Merchant** selections are rare under low volatility or high strike prices.
    - Adjust volatility or strike assumptions in earlier pages to see strategic shifts here.
    - Gurobi selects the most **economically favorable strategy** based on simulated prices.
    """)