import streamlit as st

def main():
    st.title("Summary of Findings")

    st.subheader("📊 Strategic Takeaways")

    st.markdown("#### CfD")
    st.success("""
- Best suited for low or volatile price zones
- Delivers stable, predictable revenue
- Strong performance observed for Offshore Wind and Onshore Wind CfDs.
    """)

    st.warning("""
- Mid-risk option depending on buyer reliability
- Suitable where bilateral pricing is strong
- May be viable for Solar PV in high-price zones.
    """)
    st.error("""
- High exposure to volatility
- Only suitable in consistently high-price locations
- Solar PV and Merchant strategies carry risk but potential upside.
    """)

    st.markdown("---")
    st.subheader("Zonal vs National Pricing")
    st.markdown("""
    - **Zonal** models reveal regional arbitrage opportunities and pricing risks.
    - **National** pricing offers simpler contracting but hides location-based differences.
    - Solar and Wind CfDs show different performance depending on their zone — use model to guide location-based contracting.
    """)

    st.subheader("Recommendations")
    st.markdown("""
    - Match project locations to strategy: coastal wind → CfD; high-sun, high-price regions → Merchant Solar or PPA.
    - Use revenue projections and stress tests to model risk.
    - Use optimization results to benchmark strategy robustness across zones and contracts.
    - Leverage insights from subsidy and ROI charts to prioritize investments.
    """)
if __name__ == '__main__':
    main()
