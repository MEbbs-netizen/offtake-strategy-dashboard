import streamlit as st
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

    # Large gauge charts for shocked revenue
    st.subheader(f"Revenue Under {shock_pct:+} % Price Shock")
    fig = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    for i, row in df.iterrows():
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=row["Shocked_Revenue"] / 1e6,
            title={"text": f"{row['Strategy']} (£m)", "font": {"size": 22, "color": "white"}},
            domain={"x": [i / len(df), (i + 1) / len(df)], "y": [0, 1]},
            number={"font": {"size": 42, "color": "white"}},
            delta={
                "reference": row["Base_Revenue"] / 1e6,
                "relative": True,
                "position": "top",
                "increasing": {"color": "green"},
                "decreasing": {"color": "red"},
            },
            gauge={
                "axis": {"range": [0, max(df['Shocked_Revenue']) / 1e6 * 1.2], "tickcolor": "gray"},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))

    fig.update_layout(
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        height=550,
        margin=dict(l=10, r=10, t=40, b=10),
        font=dict(color=font_color)
    )
    st.plotly_chart(fig)

    # Revenue comparison table
    st.subheader("Revenue Comparison")
    st.dataframe(df[["Strategy", "Base_Revenue", "Shocked_Revenue", "Delta_Revenue", "Delta_%"]]
        .style.format({
            "Base_Revenue": "£{:,.0f}",
            "Shocked_Revenue": "£{:,.0f}",
            "Delta_Revenue": "£{:,.0f}",
            "Delta_%": "{:+.1f} %"
        }))

    # Findings and Insights
    st.subheader("Findings and Insights")
    insights = []

    max_gain = df.loc[df["Delta_Revenue"].idxmax()]
    max_loss = df.loc[df["Delta_Revenue"].idxmin()]

    if max_gain["Delta_Revenue"] > 0:
        insights.append(
            f"The **{max_gain['Strategy']}** strategy shows the highest gain under the stressed scenario, "
            f"with an increase of **£{max_gain['Delta_Revenue']:,.0f}** ({max_gain['Delta_%']:+.1f}%)."
        )

    if max_loss["Delta_Revenue"] < 0:
        insights.append(
            f"The **{max_loss['Strategy']}** strategy experiences the greatest decline, "
            f"with a decrease of **£{abs(max_loss['Delta_Revenue']):,.0f}** ({max_loss['Delta_%']:+.1f}%)."
        )

    if df[df["Strategy"] == "CfD"]["Delta_Revenue"].iloc[0] == 0:
        insights.append("The **CfD** strategy remains unaffected by market price shocks, demonstrating stability.")

    for insight in insights:
        st.markdown(f"- {insight}")

if __name__ == "__main__":
    main()
