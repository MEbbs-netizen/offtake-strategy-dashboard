
import streamlit as st
import requests

def main():
    st.title("Renewable Strategy Dashboard")

    st.markdown("### Why This Dashboard Matters")
    st.markdown("""
    This interactive platform helps generation developers explore how different offtake arrangements (CfD, PPA, Merchant)
    perform under **zonal vs national pricing schemes**.

    It enables high-impact discussions around:
    - Revenue predictability and upside potential
    - Investment planning with NPV and IRR modeling
    - Locational arbitrage opportunities
    - Bidding and hedging strategies
    """)

    st.markdown("---")

    col1, col2 = st.columns([1, 2])
    with col1:
        st.subheader(" Modules")
        st.markdown("""
        - Zonal vs National Spread  
        - CfD Summary  
        - NPV & IRR Analysis  
        - ROI Comparison  
        - Gurobi Optimization  
        - Bidding Strategy Simulator
        - Scenario Stress test
        - Revenue & Risk Simulations
        """)
    with col2:
        image_url = "https://upload.wikimedia.org/wikipedia/commons/7/75/National_Grid_Zone_Map.png"
        try:
            response = requests.get(image_url)
            if response.status_code == 200:
                st.image(image_url, caption="Regional market zones (illustrative)", use_container_width=True)
        except:
            pass

if __name__ == "__main__":
    main()
