import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

def main():
    st.title("ROI Analysis")
    st.markdown("This section evaluates total revenue and ROI over the asset’s lifetime, factoring in:")
    st.markdown("- Annual degradation in output")
    st.markdown("- Ongoing O&M costs")
    st.markdown("- Reference market pricing")
    st.markdown("Adjust inputs in the sidebar to simulate different investment scenarios.")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df = df[(df["Settlement_Date"] >= "2025-01-01") & (df["Settlement_Date"] <= "2060-12-31")]

    # Sidebar Inputs
    capex_per_mw = st.sidebar.number_input("CapEx (£/MW)", 500000, 3000000, 1000000, step=100000)
    capacity_mw = st.sidebar.slider("Installed Capacity (MW)", 10, 300, 100, step=10)
    om_cost_per_mwh = st.sidebar.number_input("O&M Cost (£/MWh)", 0, 100, 15)
    degradation_rate = st.sidebar.slider("Annual Degradation Rate (%)", 0.0, 5.0, 1.0, step=0.1) / 100
    asset_life = st.sidebar.slider("Project Lifetime (Years)", 5, 40, 25)

    # Base values
    project_cost = capex_per_mw * capacity_mw
    annual_gen = df["CFD_Generation_MWh"].mean()

    def discounted_output(year):
        return annual_gen * ((1 - degradation_rate) ** (year - 1))

    # Simulation
    sim_data = []
    for ref in df["Reference_Type"].unique():
        total_revenue = 0
        total_cost = project_cost
        for year in range(1, asset_life + 1):
            avg_price = df[df["Reference_Type"] == ref]["Strike_Price_GBP_Per_MWh"].mean()
            output = discounted_output(year)
            rev = avg_price * output
            om_cost = om_cost_per_mwh * output
            total_revenue += rev
            total_cost += om_cost
        roi = (total_revenue - total_cost) / total_cost
        sim_data.append({"Reference_Type": ref, "Revenue": total_revenue, "Cost": total_cost, "ROI": roi})

    result_df = pd.DataFrame(sim_data)
    result_df["ROI_Label"] = result_df["ROI"].apply(lambda x: f"{x:.1%}")

    # Donut: Total Revenue
    st.subheader("Total Revenue Over Project Lifetime")
    st.markdown("Gross energy revenue over the life of the asset, factoring in output degradation.")

    fig1 = go.Figure()
    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]
    for i, row in result_df.iterrows():
        fig1.add_trace(go.Indicator(
            mode="gauge+number",
            value=row["Revenue"] / 1e6,
            title={"text": f"<b>{row['Reference_Type']}</b><br><sub>£m</sub>", "font": {"size": 18}},
            domain={"row": 0, "column": i},
            number={"font": {"size": 36, "color": "white"}},
            gauge={
                "axis": {"range": [0, max(result_df['Revenue']) / 1e6 * 1.2]},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))
    fig1.update_layout(
        grid={'rows': 1, 'columns': len(result_df), 'pattern': "independent"},
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=400
    )
    st.plotly_chart(fig1)

    # Donut: ROI Indicators
    st.subheader("Adjusted ROI by Strategy")
    fig2 = go.Figure()
    for i, row in result_df.iterrows():
        fig2.add_trace(go.Indicator(
            mode="gauge+number",
            value=row["ROI"] * 100,
            title={"text": f"<b>{row['Reference_Type']}</b><br><sub>% ROI</sub>", "font": {"size": 18}},
            domain={"row": 0, "column": i},
            number={"suffix": "%", "font": {"size": 32, "color": "white"}},
            gauge={
                "axis": {"range": [-100, 100], "tickwidth": 1},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))
    fig2.update_layout(
        grid={'rows': 1, 'columns': len(result_df), 'pattern': "independent"},
        paper_bgcolor="black",
        plot_bgcolor="black",
        height=400
    )
    st.plotly_chart(fig2)

    # ROI Over Time
    st.subheader("Cumulative ROI Over Time")
    roi_by_year = []
    for ref in df["Reference_Type"].unique():
        yearly_output = [discounted_output(y) for y in range(1, asset_life + 1)]
        avg_price = df[df["Reference_Type"] == ref]["Strike_Price_GBP_Per_MWh"].mean()
        annual_revenue = [avg_price * gen for gen in yearly_output]
        annual_om_cost = [om_cost_per_mwh * gen for gen in yearly_output]
        cumulative_cost = project_cost
        for year in range(asset_life):
            cumulative_cost += annual_om_cost[year]
            roi_y = (sum(annual_revenue[:year + 1]) - cumulative_cost) / cumulative_cost
            roi_by_year.append({
                "Year": year + 1,
                "ROI": roi_y,
                "Reference_Type": ref
            })

    roi_time_df = pd.DataFrame(roi_by_year)
    fig3 = px.line(roi_time_df, x="Year", y="ROI", color="Reference_Type", markers=True)
    fig3.update_layout(yaxis_tickformat=".0%", height=450, yaxis_title="Cumulative ROI")
    st.plotly_chart(fig3)

    # CSV Export
    st.download_button(
        label="Download ROI Results as CSV",
        data=result_df.to_csv(index=False),
        file_name="roi_analysis_results.csv",
        mime="text/csv"
    )

    # Insight
    st.markdown("### Interpretation")
    st.markdown("""
    - ROI is sensitive to O&M costs and degradation rates.
    - Revenue is most affected by pricing reference and asset life.
    - Use this to assess strategy risks and long-term value impact.
    """)

if __name__ == "__main__":
    main()
