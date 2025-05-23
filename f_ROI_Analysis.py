import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Theme detection
# Removed manual override for theme. Let Streamlit handle background/foreground color automatically.

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
            title={"text": f"<b>{row['Reference_Type']}</b><br><sub>£m</sub>", "font": {"size": 22}},
            domain={"x": [i * 0.33, (i + 1) * 0.33], "y": [0, 1]},
            number={"font": {"size": 48}, "valueformat": ".2f"},
            gauge={
                "axis": {"range": [0, max(result_df['Revenue']) / 1e6 * 1.2], "tickwidth": 1, "tickcolor": "gray"},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))
    fig1.update_layout(height=500, margin=dict(t=20, b=20))
    st.plotly_chart(fig1)

    # ROI donut-style (ENLARGED)
    st.subheader("ROI by Reference Type")
    fig2 = go.Figure()
    for i, row in result_df.iterrows():
        fig2.add_trace(go.Indicator(
            mode="gauge+number",
            value=row["ROI"] * 100,
            title={"text": f"<b>{row['Reference_Type']}</b><br><sub>ROI %</sub>", "font": {"size": 22}},
            domain={"x": [i * 0.33, (i + 1) * 0.33], "y": [0, 1]},
            number={"font": {"size": 48}, "valueformat": ".1f"},
            gauge={
                "axis": {"range": [-100, 100], "tickwidth": 1, "tickcolor": "gray"},
                "bar": {"color": colors[i % len(colors)]},
                "bgcolor": "black",
                "borderwidth": 2,
                "bordercolor": "white"
            }
        ))
    fig2.update_layout(height=500, margin=dict(t=20, b=20))
    st.plotly_chart(fig2)

    # Insights and Findings
    st.markdown("---")
    st.markdown("### 📘 Insights & Findings")
    best_roi = result_df.loc[result_df["ROI"].idxmax()]
    worst_roi = result_df.loc[result_df["ROI"].idxmin()]
    st.markdown(f"- **{best_roi['Reference_Type']}** achieved the highest ROI at **{best_roi['ROI_Label']}**.")
    st.markdown(f"- **{worst_roi['Reference_Type']}** had the lowest ROI at **{worst_roi['ROI_Label']}**.")
    st.markdown("This suggests the impact of market price assumptions and operational costs are substantial on financial returns across reference types.")

if __name__ == "__main__":
    main()
