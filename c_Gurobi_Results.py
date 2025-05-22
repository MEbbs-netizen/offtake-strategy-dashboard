import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import gurobipy as gp
from gurobipy import GRB

def run_gurobi_strategy():
    try:
        model = gp.Model()
        strategies = ["CfD", "PPA", "Merchant"]
        values = {
            "CfD": np.random.normal(80, 5),
            "PPA": np.random.normal(65, 8),
            "Merchant": np.random.normal(75, 10)
        }

        x = {s: model.addVar(vtype=GRB.BINARY, name=s) for s in strategies}
        model.setObjective(gp.quicksum(values[s] * x[s] for s in strategies), GRB.MAXIMIZE)
        model.addConstr(gp.quicksum(x[s] for s in strategies) == 1, "OneStrategy")
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

    max_simulations = st.slider("Max Number of Simulations", 100, 10000, 1000, step=500)

    strategy_counts = []
    steps = list(range(100, max_simulations + 1, 100))
    for sim in steps:
        batch = [run_gurobi_strategy() for _ in range(sim)]
        counts = pd.Series(batch).value_counts().reset_index()
        counts.columns = ["Strategy", "Count"]
        counts["Simulations"] = sim
        strategy_counts.append(counts)

    summary_df = pd.concat(strategy_counts)
    summary_df = summary_df.sort_values(by=["Simulations", "Strategy"])

    # Line Chart
    st.subheader("Strategy Selection Trends vs Simulations")
    fig_line = px.line(
        summary_df,
        x="Simulations",
        y="Count",
        color="Strategy",
        markers=True
    )
    fig_line.update_layout(
        paper_bgcolor="black",
        plot_bgcolor="black",
        font_color="white",
        height=450
    )
    st.plotly_chart(fig_line)

    # Donut Chart
    st.subheader("Final Strategy Distribution")
    final_df = summary_df[summary_df['Simulations'] == summary_df['Simulations'].max()]
    fig_donut = go.Figure(data=[go.Pie(
        labels=final_df['Strategy'],
        values=final_df['Count'],
        hole=0.5,
        marker=dict(colors=['#1f77b4', '#ff7f0e', '#2ca02c']),
        textinfo='label+percent',
        insidetextorientation='radial'
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

    # Insights
    st.subheader("Insights")
    top = final_df.loc[final_df["Count"].idxmax()]
    st.markdown(f"- The **{top['Strategy']}** strategy was selected most frequently: **{top['Count']:,}** times.")
    st.markdown("- The donut chart summarizes final choice distribution based on Gurobi-driven simulation.")

if __name__ == "__main__":
    main()
