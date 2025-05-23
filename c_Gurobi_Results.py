import streamlit as st
import plotly.graph_objects as go

# Detect browser theme using JavaScript
st.markdown("""
    <script>
    const theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? "dark" : "light";
    document.cookie = "theme=" + theme;
    </script>
""", unsafe_allow_html=True)

theme = st.query_params.get("theme", "light")
bg_color = '#ffffff' if theme == 'light' else '#000000'
font_color = '#000000' if theme == 'light' else '#ffffff'

import pandas as pd
import numpy as np
import plotly.express as px
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

def generate_insight(distribution):
    most_common = distribution.iloc[distribution['Count'].idxmax()]
    least_common = distribution.iloc[distribution['Count'].idxmin()]
    total = distribution['Count'].sum()

    insight = f"""
### 🧠 Insights

- The most frequently selected strategy is **{most_common['Strategy']}**, accounting for **{most_common['Count'] / total:.1%}** of simulations.
- The least favored strategy is **{least_common['Strategy']}**, with only **{least_common['Count'] / total:.1%}**.
- This suggests that under the current expected value assumptions, **{most_common['Strategy']}** is consistently more profitable or stable compared to alternatives.

Adjusting the expected value sliders could significantly impact this outcome, especially if assumptions about market conditions or contract preferences change.
"""
    return insight

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
    fig_line.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=font_color),
        height=450
    )
    st.plotly_chart(fig_line)

    # Donut chart
    st.subheader("Final Strategy Distribution")
    final_df = summary_df[summary_df['Simulations'] == summary_df['Simulations'].max()]
    fig_donut = go.Figure(data=[go.Pie(
        labels=final_df['Strategy'],
        values=final_df['Count'],
        hole=0.4,
        textinfo='label+percent',
        textfont_size=20,
        marker=dict(line=dict(color='#000000', width=2)),
        domain={'x': [0, 1], 'y': [0, 1]}
    )])
    fig_donut.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        font=dict(color=font_color),
        height=700
    )
    st.plotly_chart(fig_donut)

    # Auto-generated markdown insights
    st.markdown(generate_insight(final_df))

if __name__ == "__main__":
    main()
