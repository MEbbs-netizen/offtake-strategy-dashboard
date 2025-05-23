import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
        paper_bgcolor=bg_color, plot_bgcolor=bg_color, font=dict(color=font_color)
    )
    st.plotly_chart(fig1)

    # ROI Bar Chart
    st.subheader("ROI by Reference Type")
    fig2 = px.bar(result_df, x="Reference_Type", y="ROI", text="ROI_Label", color="Reference_Type")
    fig2.update_layout(
        paper_bgcolor=bg_color, plot_bgcolor=bg_color, font=dict(color=font_color)
    )
    st.plotly_chart(fig2)

if __name__ == "__main__":
    main()
