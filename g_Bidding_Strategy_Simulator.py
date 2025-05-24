import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import io

def main():
    st.title("Bidding Strategy Simulator")

    st.markdown("### Simulate Revenue Outcomes from Strike Price Bids")

    # User inputs
    bid_price = st.sidebar.slider("Bid Strike Price (£/MWh)", 30, 150, 80, step=5)
    market_price = st.sidebar.slider("Expected Market Price (£/MWh)", 30, 100, 60)
    generation = st.sidebar.number_input("Annual Generation (MWh)", 10000, 1000000, 300000, step=10000)

    # Simulated price scenarios
    prices = np.random.normal(loc=market_price, scale=8, size=1000)
    diff = bid_price - prices
    revenue = diff * generation
    revenue[revenue < 0] = 0  # No award below market

    # Chart
    st.subheader("Simulated Revenue Distribution")
    fig = px.histogram(revenue, nbins=50, title="Revenue from CfD Bid", labels={"value": "Annual Revenue (£)"})
    fig.update_layout(xaxis_title="Annual Revenue (£)", yaxis_title="Frequency", height=450)
    st.plotly_chart(fig)

    # Key stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Mean (£)", f"{revenue.mean():,.0f}")
    col2.metric("P10 (£)", f"{np.percentile(revenue, 10):,.0f}")
    col3.metric("P90 (£)", f"{np.percentile(revenue, 90):,.0f}")

    # Improved win probability based on simulation
    win_prob = np.mean(prices <= bid_price) * 100  # Probability bid price >= market price (win)
    win_prob = round(win_prob, 1)
    col4.metric("Win Probability", f"{win_prob}%")

    # Summary Table
    summary_df = pd.DataFrame({
        "Metric": ["Mean Revenue (£)", "P10 Revenue (£)", "P90 Revenue (£)", "Win Probability (%)"],
        "Value": [f"{revenue.mean():,.0f}",
                  f"{np.percentile(revenue, 10):,.0f}",
                  f"{np.percentile(revenue, 90):,.0f}",
                  f"{win_prob}%"]
    })

    st.markdown("### Summary Table")
    st.table(summary_df)

    # CSV Download button for summary
    csv_buffer = io.StringIO()
    summary_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="Download Summary as CSV",
        data=csv_data,
        file_name="bidding_strategy_summary.csv",
        mime="text/csv"
    )

    # Notes
    st.markdown("""
    ### 💡 Insights:
    - **Mean** revenue indicates the central expected value based on your bid.
    - **P10 / P90** capture the risk range — useful for evaluating downside and upside.
    - A **higher strike** improves potential earnings but reduces **award likelihood**.
    - This tool helps identify **bid levels that balance certainty vs profit**.
    """)

if __name__ == "__main__":
    main()
