import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("Zonal vs National Price Spread")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]
    df["Year"] = df["Settlement_Date"].dt.year

    techs = df["Technology"].unique().tolist()
    selected = st.sidebar.multiselect("Select Technologies", techs, default=techs)
    df = df[df["Technology"].isin(selected)]

    st.subheader("Strike vs Market Spread (Avg £/MWh)")
    market_spread = df.groupby("Technology")["Price_Spread_Strike_vs_Market"].mean().sort_values().reset_index()
    fig1 = px.bar(market_spread, x="Price_Spread_Strike_vs_Market", y="Technology",
                  orientation="h", color="Price_Spread_Strike_vs_Market",
                  color_continuous_scale="Turbo")
    fig1.update_layout(xaxis_title="Spread (£/MWh)", yaxis_title="Technology", height=400)
    st.plotly_chart(fig1, use_container_width=True)
    st.caption("💡 Technologies like Offshore Wind show favorable spreads, indicating better strike price leverage in the market.")
    st.markdown("---")

    st.subheader("Strike vs IMRP Spread (Avg £/MWh)")
    imrp_spread = df.groupby("Technology")["Price_Spread_Strike_vs_IMRP"].mean().sort_values().reset_index()
    fig2 = px.bar(imrp_spread, x="Price_Spread_Strike_vs_IMRP", y="Technology",
                  orientation="h", color="Price_Spread_Strike_vs_IMRP",
                  color_continuous_scale="Plasma")
    fig2.update_layout(xaxis_title="Spread (£/MWh)", yaxis_title="Technology", height=400)
    st.plotly_chart(fig2, use_container_width=True)
    st.caption("💡 IMRP comparisons help assess how well different strategies align with regional benchmarks.")
    st.markdown("---")

    st.subheader("Yearly Strike vs Market Spread")
    yearly = df.groupby(["Year", "Technology"])["Price_Spread_Strike_vs_Market"].mean().reset_index()
    fig3 = px.line(yearly, x="Year", y="Price_Spread_Strike_vs_Market", color="Technology", markers=True)
    fig3.update_layout(
        xaxis_title="Year",
        yaxis_title="Spread (£/MWh)",
        height=500
    )
    st.plotly_chart(fig3, use_container_width=True)
    st.caption("💡 Long-term consistency or volatility in spread reveals strategy risk profiles over time.")

if __name__ == "__main__":
    main()
