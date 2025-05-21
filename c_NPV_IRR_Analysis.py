import streamlit as st
import pandas as pd
import numpy as np
from numpy_financial import irr
import plotly.graph_objects as go

def main():
    st.title("💰 NPV and IRR Analysis")

    st.markdown("""
### 📈 Objective
Evaluate project economics using Net Present Value (NPV) and Internal Rate of Return (IRR) based on CfD cashflows.

📌 **Key Insight:** A positive NPV and IRR > discount rate indicate attractive investment potential.
    """)

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df["Year"] = df["Settlement_Date"].dt.year
    cf = df.groupby("Year")["CFD_Payments_GBP"].sum().reset_index()

    rate = st.sidebar.slider("Discount Rate (%)", 2.0, 12.0, 6.0) / 100
    cashflows = cf["CFD_Payments_GBP"].values
    dcf = [cf / (1 + rate)**i for i, cf in enumerate(cashflows)]
    npv = sum(dcf)

    try:
        irr_val = irr(cashflows)
        irr_display = f"{irr_val*100:.2f}%" if np.isfinite(irr_val) else "Not Defined"
    except:
        irr_display = "Not Computable"

    st.subheader("📉 Financial Summary")
    col1, col2 = st.columns(2)
    col1.metric("NPV (£)", f"{npv:,.0f}")
    col2.metric("IRR", irr_display)

    st.markdown("📌 **Interpretation:** NPV > 0 and IRR > discount rate → investable economics.")

    st.subheader("📊 Cashflow Timeline")
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cf["Year"],
        y=cashflows,
        name="Nominal Cashflow",
        marker_color="green"
    ))
    fig.add_trace(go.Scatter(
        x=cf["Year"],
        y=dcf,
        name="Discounted Cashflow",
        mode="lines+markers",
        line=dict(color="red", width=3)
    ))
    fig.update_layout(
        title="🧮 Nominal vs Discounted CfD Payments",
        xaxis_title="Year",
        yaxis_title="Payments (£)",
        barmode="group",
        template="plotly_white",
        margin=dict(t=60, b=40)
    )
    st.plotly_chart(fig)

    st.markdown("💡 Discounted cashflows show time value of money impact.")