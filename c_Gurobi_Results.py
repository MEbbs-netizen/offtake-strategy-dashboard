import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import gurobipy as gp
from gurobipy import GRB

def run_gurobi_strategy(cfd_val, ppa_val, merchant_val):
    try:
        model = gp.Model()
        strategies = ["CfD", "PPA", "Merchant"]
        values = {
            "CfD": np.random.normal(cfd_val, 5),
            "PPA": np.random.normal(ppa_val, 8),
            "Merchant": np.random.normal(merchant_val, 10)
        }

        x = {s: model.addVar(vtype=GRB.BINARY, name=s) for s in strategies}
        model.setObjective(gp.quicksum(values[s] * x[s] for s in strategies), GRB.MAXIMIZE)
        model.addConstr(gp.quicksum(x[s] for s in strategies) == 1)
        model.setParam('OutputFlag', 0)
        model.optimize()

        for s in strategies:
            if x[s].X > 0.5:
                return s
    except gp.GurobiError:
        return "Error"
    return "Unknown"

def main():
    st.title("Gurobi Strategy Optimization (Simulated)")

    # User-defined expected values
    st.sidebar.markdown("### Expected Value Settings")
    cfd_val = st.sidebar.slider("Expected CfD Value", 60, 100, 80)
    ppa_val = st.sidebar.slider("Expected PPA Value", 40, 90, 65)
    merchant_val = st.sidebar.slider("Expected Merchant Value", 50, 100, 75)

    max_simulations = st.slider("Max Number of Simulations", 100, 10000, 1000, step=500)

    strategy_counts = []
    steps = list(range(100, max_simulations + 1, 100))
    for sim in steps:
        batch = [run_gurobi_strategy(cfd_val, ppa_val, merchant_val) for _ in range(sim)]
        counts = pd.Series(batch).value_counts().reset_index()
        counts.columns = ["Strategy", "Count"]
        counts["Simulations"] = sim
        strategy_counts.append(counts)

    summary_df = pd.concat(strategy_counts)
    summary_df = summary_df.sort_values(by=["Simulations", "Strategy"])

    # Line chart
    st.subheader("Strategy Selection Trends vs Simulations")
    fig_line = px.line(summary_df, x="Simulations", y="Count", color="Strategy", markers=True)
    fig_line.update_layout(paper_bgcolor="black", plot_bgcolor="black", font_color="white", height=450)
    st.plotly_chart(fig_line)

    # Donut chart
    st.subheader("Final Strategy Distribution")
    final_df = summary_df[summary_df['Simulations'] == summary_df['Simulations'].max()]
    fig_donut = go.Figure(data=[go.Pie(
        labels=final_df['Strategy'],
        values=final_df['Count'],
        hole=0.5,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c']),
        textinfo='label+percent'
    )])
    fig_donut.update_layout(
        showlegend=True,
        paper_bgcolor='black',
        plot_bgcolor='black',
        font=dict(color='white'),
        margin=dict(t=30, b=30, l=30, r=30),
        height=400
    )
    st.plotly_chart(fig_donut)

    st.subheader("Insights")
    top = final_df.loc[final_df["Count"].idxmax()]
    st.markdown(f"- The **{top['Strategy']}** strategy was selected most frequently: **{top['Count']:,}** times.")
    st.markdown("- These results reflect your expected value assumptions and Monte Carlo variation.")

if __name__ == "__main__":
    main()
