import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def main():
    st.title("Scenario Stress Test")

    gen = st.sidebar.slider("Annual Generation (MWh)", 50000, 500000, 250000, step=10000)
    base_price = st.sidebar.slider("Base Market Price (£/MWh)", 40, 120, 70)
    strike = st.sidebar.slider("CfD Strike Price (£/MWh)", 50, 150, 100)
    shock_pct = st.sidebar.slider("Price Shock (%)", -50, 50, -20, step=5)

    shocked_price = base_price * (1 + shock_pct / 100)
    revenue = {
        "CfD": (strike * gen),
        "PPA": ((shocked_price - 2) * gen),
        "Merchant": (shocked_price * gen)
    }

    df = pd.DataFrame.from_dict(revenue, orient="index", columns=["Revenue"]).reset_index()
    df.columns = ["Strategy", "Revenue"]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=df["Strategy"], y=df["Revenue"], text=df["Revenue"].apply(lambda x: f"£{x:,.0f}"),
                         textposition="outside", marker_color=["#1f77b4", "#ff7f0e", "#2ca02c"]))
    fig.update_layout(title=f"Revenue Under {shock_pct:+} % Price Shock", yaxis_title="Annual Revenue (£)", height=400)
    st.plotly_chart(fig)