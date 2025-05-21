import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("CfD Summary")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]
    df["Year"] = df["Settlement_Date"].dt.year

    # Summarize by Technology
    agg = df.groupby(["Technology"]).agg({
        "CFD_Generation_MWh": "sum",
        "CFD_Payments_GBP": "sum",
        "Avoided_GHG_tonnes_CO2e": "sum"
    }).reset_index()
    agg["GHG_per_MWh"] = agg["Avoided_GHG_tonnes_CO2e"] / agg["CFD_Generation_MWh"]
    agg["Subsidy_per_MWh"] = agg["CFD_Payments_GBP"] / agg["CFD_Generation_MWh"]
    agg["Subsidy_per_tCO2"] = agg["CFD_Payments_GBP"] / agg["Avoided_GHG_tonnes_CO2e"]

    st.subheader("CfD Payments and Generation by Technology")
    fig = px.bar(agg, x="Technology", y=["CFD_Payments_GBP", "CFD_Generation_MWh"],
                 barmode="group",
                 labels={"value": "Total", "variable": "Metric"},
                 title="Total CfD Payments vs Generation")
    fig.update_layout(height=450)
    st.plotly_chart(fig)

    st.markdown("📌 **Insight:** Offshore Wind leads in both payment and output. Technologies with low payment but small scale may still be strategically important.")

    # Avg Subsidy Rate
    df["Subsidy_Rate"] = df["CFD_Payments_GBP"] / df["CFD_Generation_MWh"]
    avg_subsidy = df.groupby(["Technology", "Reference_Type"])["Subsidy_Rate"].mean().reset_index()

    st.subheader("Avg Subsidy Rate (£/MWh)")
    fig2 = px.bar(avg_subsidy, x="Technology", y="Subsidy_Rate", color="Reference_Type", barmode="group")
    fig2.update_layout(title="Avg Subsidy Rate by Technology and Reference Type", yaxis_title="£/MWh", height=400)
    st.plotly_chart(fig2)

    st.markdown("📌 **Note:** Some technologies show higher subsidy needs due to scale or maturity.")

    # Efficiency Ranking
    st.subheader("Strategy Efficiency Metrics")
    rank_df = agg[["Technology", "Subsidy_per_MWh", "Subsidy_per_tCO2"]].sort_values("Subsidy_per_MWh")
    rank_df["£/MWh Rank"] = rank_df["Subsidy_per_MWh"].rank()
    rank_df["£/tCO2 Rank"] = rank_df["Subsidy_per_tCO2"].rank()

    fig3 = px.bar(rank_df.sort_values("Subsidy_per_MWh"), x="Technology", y="Subsidy_per_MWh",
                  title="Cost Efficiency (£/MWh Generated)", color="Subsidy_per_MWh",
                  labels={"Subsidy_per_MWh": "£/MWh"})
    fig3.update_layout(height=400)
    st.plotly_chart(fig3)

    fig4 = px.bar(rank_df.sort_values("Subsidy_per_tCO2"), x="Technology", y="Subsidy_per_tCO2",
                  title="Carbon Efficiency (£/tCO2 Avoided)", color="Subsidy_per_tCO2",
                  labels={"Subsidy_per_tCO2": "£/tCO2"})
    fig4.update_layout(height=400)
    st.plotly_chart(fig4)

    st.markdown("📌 **Insight:** Ranking technologies by efficiency highlights where subsidy delivers the greatest environmental and economic return.")