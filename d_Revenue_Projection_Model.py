import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# Theme detection
st.markdown("""
    <script>
    const theme = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? "dark" : "light";
    document.cookie = "theme=" + theme;
    </script>
""", unsafe_allow_html=True)

theme = st.query_params.get("theme", "light")
bg_color = '#ffffff' if theme == 'light' else '#000000'
font_color = '#000000' if theme == 'light' else '#ffffff'

def main():
    st.title("Revenue Projection Model")
    st.markdown("This tool simulates expected annual revenue for three offtake strategies under uncertain market conditions.")
    st.markdown("Adjust the inputs in the sidebar to reflect project assumptions and compare outcomes.")

    # Sidebar controls
    gen = st.sidebar.slider("Annual Generation (MWh)", 50000, 500000, 250000, step=10000)
    base_price = st.sidebar.slider("Base Market Price (£/MWh)", 40, 120, 70)
    strike = st.sidebar.slider("CfD Strike Price (£/MWh)", 50, 150, 100)
    volatility = st.sidebar.slider("Market Price Volatility (sigma)", 0, 30, 10)
    ppa_discount = st.sidebar.slider("PPA Discount (£/MWh)", 0, 10, 2)

    st.markdown(f'⚠️ **PPA Discount Applied:** £{ppa_discount}/MWh')

    # Simulate 25 years of market prices
    np.random.seed(42)
    prices = np.random.normal(loc=base_price, scale=volatility, size=25)

    # Calculate revenue per strategy
    revenue = {
        "CfD": (strike * gen),
        "PPA": ((prices.mean() - ppa_discount) * gen),
        "Merchant": (prices.mean() * gen)
    }

    df = pd.DataFrame.from_dict(revenue, orient="index", columns=["Revenue"]).reset_index()
    df.columns = ["Strategy", "Revenue"]

    # Donut-style gauge chart
    fig = go.Figure()
    colors = ["#1f77b4", "#8c564b", "#ff7f0e"]

    for i, row in df.iterrows():
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=row["Revenue"] / 1e6,
            title={"text": f"<b>{row['Strategy']}</b><br><sub>£m</sub>", "font": {"size": 18}},
            domain={'row': 0, 'column': i},
            number={"font": {"size": 36, "color": font_color}, "valueformat": ".2f"},
            gauge={
                "axis": {"range": [None, max(df['Revenue']) / 1e6], "tickwidth": 1, "tickcolor": "gray"},
                "bar": {"color": colors[i]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))

    fig.update_layout(
        grid={'rows': 1, 'columns': 3, 'pattern': "independent"},
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        title={
            "text": "Revenue Projection by Strategy",
            "font": {"size": 28, "color": font_color},
            "x": 0.5
        },
        font=dict(color=font_color)
    )

    st.plotly_chart(fig)

    # Insight Section
    st.markdown("---")
    st.markdown("### 📘 Notes")
    st.markdown("- **CfD** guarantees revenue at the strike price regardless of market conditions.")
    st.markdown("- **PPA** typically trades at a discount to merchant prices due to contract structure.")
    st.markdown("- **Merchant** strategies carry more upside—and downside—depending on price volatility.")

    st.markdown("### 💡 Key Insight")
    best = df.loc[df["Revenue"].idxmax()]
    st.markdown(f"- **{best['Strategy']}** strategy yields the highest projected revenue: **£{best['Revenue'] / 1e6:.2f} million**.")

if __name__ == "__main__":
    main()
