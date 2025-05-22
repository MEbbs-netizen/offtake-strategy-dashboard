import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def main():
    st.title("Scenario Stress Test")

    # Sidebar inputs
    gen = st.sidebar.slider("Annual Generation (MWh)", 50000, 500000, 250000, step=10000)
    base_price = st.sidebar.slider("Base Market Price (£/MWh)", 40, 120, 70)
    strike = st.sidebar.slider("CfD Strike Price (£/MWh)", 50, 150, 100)
    shock_pct = st.sidebar.slider("Price Shock (%)", -50, 50, -20, step=5)

    shocked_price = base_price * (1 + shock_pct / 100)

    # Revenue calculations
    base_revenue = {
        "CfD": strike * gen,
        "PPA": (base_price - 2) * gen,
        "Merchant": base_price * gen
    }

    shocked_revenue = {
        "CfD": strike * gen,
        "PPA": (shocked_price - 2) * gen,
        "Merchant": shocked_price * gen
    }

    # Combine into DataFrame
    df_base = pd.DataFrame.from_dict(base_revenue, orient="index", columns=["Base_Revenue"]).reset_index()
    df_shock = pd.DataFrame.from_dict(shocked_revenue, orient="index", columns=["Shocked_Revenue"]).reset_index()
    df = df_base.merge(df_shock, on="index")
    df.columns = ["Strategy", "Base_Revenue", "Shocked_Revenue"]
    df["Delta_Revenue"] = df["Shocked_Revenue"] - df["Base_Revenue"]
    df["Delta_%"] = 100 * df["Delta_Revenue"] / df["Base_Revenue"]

    # Donut chart for shocked revenue
    st.subheader(f"Revenue Under {shock_pct:+} % Price Shock")
    fig = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for i, row in df.iterrows():
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=row["Shocked_Revenue"] / 1e6,
            title={"text": f"{row['Strategy']} (£m)", "font": {"size": 18}},
            domain={"row": 0, "column": i},
            number={"font": {"size": 34}},
            delta={
                "reference": row["Base_Revenue"] / 1e6,
                "relative": True,
                "position": "top",
                "increasing": {"color": "green"},
                "decreasing": {"color": "red"},
            },
            gauge={
                "axis": {"range": [0, max(df['Shocked_Revenue']) / 1e6 * 1.2]},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray"
            }
        ))

    fig.update_layout(
        grid={'rows': 1, 'columns': len(df), 'pattern': "independent"},
        paper_bgcolor="white",
        plot_bgcolor="white",
        height=400
    )
    st.plotly_chart(fig)

    # Comparison table
    st.subheader("Revenue Comparison")
    st.dataframe(df[["Strategy", "Base_Revenue", "Shocked_Revenue", "Delta_Revenue", "Delta_%"]]
                 .style.format({
                     "Base_Revenue": "£{:,.0f}",
                     "Shocked_Revenue": "£{:,.0f}",
                     "Delta_Revenue": "£{:,.0f}",
                     "Delta_%": "{:+.1f} %"
                 }))

    # CSV export
    st.download_button(
        label="Download Results as CSV",
        data=df.to_csv(index=False),
        file_name="scenario_stress_test_results.csv",
        mime="text/csv"
    )

    # Interpretation
    st.subheader("Interpretation")
    best = df.loc[df["Shocked_Revenue"].idxmax()]
    worst = df.loc[df["Shocked_Revenue"].idxmin()]
    st.markdown(f"- Under a {shock_pct:+}% price shock, **{best['Strategy']}** achieves the highest revenue: £{best['Shocked_Revenue']:,.0f}.")
    st.markdown(f"- The lowest revenue is observed for **{worst['Strategy']}**: £{worst['Shocked_Revenue']:,.0f}.")
    st.markdown("- Use this analysis to evaluate revenue resilience across strategies under stressed market conditions.")

if __name__ == "__main__":
    main()
