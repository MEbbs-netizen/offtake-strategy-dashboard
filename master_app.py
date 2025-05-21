import streamlit as st

st.set_page_config(
    page_title="Renewable Strategy Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)
import os

PAGES = {
    "Welcome": "a_Welcome.py",
    "Zonal vs National Spread": "a_Zonal_vs_National_Spread.py",
    "CfD Summary": "b_CfD_Summary.py",
    "NPV & IRR Analysis": "c_NPV_IRR_Analysis.py",
    "Gurobi Optimization": "c_Gurobi_Results.py",
    "Revenue Projection Model": "d_Revenue_Projection_Model.py",
    "ROI Analysis": "f_ROI_Analysis.py",
    "Bidding Strategy Simulator": "g_Bidding_Strategy_Simulator.py",
    "Scenario Stress Test": "i_Scenario_Stress_Test.py",
    "Strategy Radar": "j_Strategy_Radar.py",
    "Summary of Findings": "z_Summary_Findings.py"
}

st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
module_name = PAGES[selection][:-3]
exec(f"import {module_name} as page; page.main()")