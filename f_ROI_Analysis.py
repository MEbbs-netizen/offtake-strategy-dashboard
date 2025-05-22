import streamlit as st
import pandas as pd
import plotly.express as px

def main():
    st.title("ROI Analysis")
    st.markdown("This section evaluates **total revenue** and **ROI** over the asset’s lifetime, factoring in:")
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

    # Simulation loop
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

    # Plot revenue
    st.subheader("📊 Total Revenue over Lifetime (Degraded Output)")
    st.markdown("_This reflects gross income from energy sales before cost deductions._")
    fig1 = px.bar(result_df, x="Reference_Type", y="Revenue", text="Revenue", color="Reference_Type")
    fig1.update_layout(yaxis_title="Total Revenue (£)", height=400)
    st.plotly_chart(fig1)

    # Plot ROI with benchmark
    st.subheader("📈 ROI Including O&M + Degradation")
    st.markdown("_Return on Investment after accounting for all capital and operational costs._")
    fig2 = px.bar(result_df, x="Reference_Type", y="ROI", text="ROI_Label", color="Reference_Type")
    fig2.update_layout(yaxis_title="Return on Investment", height=400)
    fig2.update_traces(textposition="outside")
    fig2.add_shape(
        type="line",
        x0=-0.5, x1=len(result_df["Reference_Type"]) - 0.5,
        y0=0.10, y1=0.10,
        line=dict(color="red", dash="dash"),
    )
    fig2.add_annotation(
        x=0.5, y=0.105,
        text="ROI Benchmark: 10%",
        showarrow=False,
        font=dict(color="red", size=12)
    )
    st.plotly_chart(fig2)

    # ROI Over Time
    st.subheader("⏳ ROI Over Time for Each Strategy")
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
        label="📥 Download ROI Results as CSV",
        data=result_df.to_csv(index=False),
        file_name="roi_analysis_results.csv",
        mime="text/csv"
    )

    # Notes
    st.markdown("### 🔍 Insight")
    st.markdown("""
    - Longer lifespans improve ROI but amplify degradation impact.
    - Reference pricing (IMRP vs BMRP) strongly affects total return.
    - Use these comparisons to support strategy or bidding assumptions.
    """)

if __name__ == "__main__":
    main()
