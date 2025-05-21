import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def main():
    st.title("Strategy Radar Comparison")

    st.markdown("### Strategy Attribute Comparison Radar")

    radar_data = {
        "Attribute": ["Revenue Stability", "Upside Potential", "Downside Risk", "Simplicity", "Market Exposure"],
        "CfD": [9, 3, 2, 8, 2],
        "PPA": [6, 6, 5, 6, 5],
        "Merchant": [2, 9, 9, 3, 9]
    }

    df = pd.DataFrame(radar_data)

    fig = go.Figure()
    for strategy in ["CfD", "PPA", "Merchant"]:
        fig.add_trace(go.Scatterpolar(
            r=df[strategy],
            theta=df["Attribute"],
            fill='toself',
            name=strategy
        ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=True,
        title="Strategy Attribute Comparison Radar",
        height=500
    )
    st.plotly_chart(fig)

    st.markdown("""
    ### 🧠 Interpretation:

    - **Revenue Stability**: CfD dominates with predictable returns.
    - **Upside Potential**: Merchant performs best when market prices soar.
    - **Downside Risk**: CfD offers safety; Merchant is highly exposed.
    - **Simplicity**: CfDs are contractually simple; PPAs can be complex depending on buyers.
    - **Market Exposure**: Merchant strategy is fully exposed to wholesale prices, offering both risk and opportunity.

    📌 Use this radar to balance your **risk appetite**, **regulatory comfort**, and **market outlook** when choosing an offtake structure.
    """)