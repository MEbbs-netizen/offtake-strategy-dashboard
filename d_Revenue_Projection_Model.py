import streamlit as st
import plotly.graph_objects as go
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
        model.addConstr(gp.quicksum(x[s] for s in strategies) == 1)
        model.setObjective(gp.quicksum(values[s] * x[s] for s in strategies), GRB.MAXIMIZE)
        model.optimize()

        selected_strategy = [s for s in strategies if x[s].X > 0.5][0]
        revenue = values[selected_strategy]
        return selected_strategy, revenue, values

    except gp.GurobiError as e:
        st.error(f"Gurobi Error: {e}")
        return None, None, {}

def main():
    st.title("Revenue Projection Model")
    st.markdown("This tool simulates expected annual revenue for three offtake strategies under uncertain market conditions.")
    st.markdown("Adjust the inputs in the sidebar to reflect project assumptions and compare outcomes.")
    st.warning("⚠️ PPA Discount Applied: £2/MWh")

    cfd_val = st.sidebar.slider("CfD Base Revenue (£m)", 10, 30, 25)
    ppa_val = st.sidebar.slider("PPA Base Revenue (£m)", 10, 30, 18)
    merchant_val = st.sidebar.slider("Merchant Base Revenue (£m)", 10, 30, 20)

    selected_strategy, revenue, strategy_values = run_gurobi_strategy(cfd_val, ppa_val, merchant_val)

    if selected_strategy:
        st.success(f"Optimal Strategy: **{selected_strategy}** with projected revenue of **£{revenue:.2f}m**")

        fig = go.Figure()
        colors = {"CfD": "royalblue", "PPA": "indianred", "Merchant": "orange"}

        for strategy, value in strategy_values.items():
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=value,
                title={'text': strategy},
                gauge={
                    'axis': {'range': [0, max(strategy_values.values()) * 1.2]},
                    'bar': {'color': colors[strategy]}
                },
                domain={'row': 0, 'column': list(strategy_values.keys()).index(strategy)}
            ))

        fig.update_layout(
            grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
            title_text="Revenue Projection by Strategy"
        )

        st.plotly_chart(fig)

        # Notes and Insights
        st.markdown("---")
        st.subheader("📘 Notes & Insights")

        # Sort strategies by revenue
        sorted_strats = sorted(strategy_values.items(), key=lambda x: x[1], reverse=True)
        best = sorted_strats[0]
        second = sorted_strats[1]

        margin = best[1] - second[1]
        st.markdown(f"- The **{best[0]}** strategy offers the highest projected revenue: **£{best[1]:.2f}m**.")
        st.markdown(f"- The second-best option is **{second[0]}**, trailing by **£{margin:.2f}m**.")

        if margin < 1:
            st.warning("⚠️ The revenue difference between top strategies is small. Consider risk, stability, or external factors.")

if __name__ == "__main__":
    main()
