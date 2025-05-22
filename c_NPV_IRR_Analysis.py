import streamlit as st
import pandas as pd
import numpy as np
from numpy_financial import irr
import plotly.graph_objects as go
from fpdf import FPDF
from io import BytesIO

def main():
    st.title("💰 NPV and IRR Analysis")

    df = pd.read_csv("data/cfd_processed.csv", parse_dates=["Settlement_Date"])
    df["Year"] = df["Settlement_Date"].dt.year
    df = df[df["Year"] <= 2060]
    cf = df.groupby("Year")["CFD_Payments_GBP"].sum().reset_index()

    rate = st.sidebar.slider("Discount Rate (%)", 2.0, 12.0, 6.0) / 100
    cashflows = cf["CFD_Payments_GBP"].values
    dcf = [cf / (1 + rate)**i for i, cf in enumerate(cashflows)]
    npv = sum(dcf)

    try:
        irr_val = irr(cashflows)
        irr_display = f"{irr_val*100:.2f}%" if np.isfinite(irr_val) else "Not Defined"
    except:
        irr_display = "Not Computable"

    cumulative_dcf = np.cumsum(dcf)
    payback_idx = np.argmax(cumulative_dcf >= 0)
    payback_year = cf["Year"].iloc[payback_idx] if cumulative_dcf[payback_idx] >= 0 else "Not Achieved"

    st.subheader("Financial Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("NPV (£)", f"{npv:,.0f}")
    col2.metric("IRR", irr_display)
    col3.metric("Payback Year", payback_year)

    st.markdown("📌 **Interpretation:** NPV > 0 and IRR > discount rate → investable economics.")

    fig = go.Figure()
    fig.add_trace(go.Bar(x=cf["Year"], y=cashflows, name="Nominal", marker_color="green"))
    fig.add_trace(go.Scatter(x=cf["Year"], y=dcf, name="Discounted", mode="lines+markers", line=dict(color="red", width=3)))
    fig.update_layout(
        title="Nominal vs Discounted CfD Payments",
        xaxis_title="Year",
        yaxis_title="Payments (£)",
        barmode="group",
        template="plotly_white",
        margin=dict(t=60, b=40),
        xaxis=dict(range=[cf["Year"].min(), 2060])
    )
    st.plotly_chart(fig)

    st.markdown("### ℹ️ What This Means")
    st.markdown(
        f"- **NPV** is the total value today of all future CfD cashflows.  \n"
        f"- **IRR** is the effective annual return on the project.  \n"
        f"- **Payback Year ({payback_year})** is when cumulative **discounted** returns cover the initial outlay.  \n"
        f"- Discounting reflects time value of money – future income is worth less today."
    )

    st.download_button(
        label="Download Cashflows as CSV",
        data=cf.assign(Discounted=dcf).to_csv(index=False),
        file_name="cfd_cashflows_summary.csv",
        mime="text/csv"
    )

    if st.button("Generate PDF Report"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 16)
        pdf.cell(0, 10, "NPV and IRR Analysis Report", ln=True)

        pdf.set_font("Helvetica", "", 12)
        pdf.cell(0, 10, f"Discount Rate: {rate*100:.1f}%", ln=True)
        pdf.cell(0, 10, f"NPV: £{npv:,.0f}", ln=True)
        pdf.cell(0, 10, f"IRR: {irr_display}", ln=True)
        pdf.cell(0, 10, f"Payback Year: {payback_year}", ln=True)

        pdf.ln(5)
        pdf.multi_cell(0, 8, "Interpretation: NPV > 0 and IRR > discount rate → investable economics.")
        pdf.multi_cell(0, 8, f"Payback Year ({payback_year}) means discounted returns exceed investment by then.")

        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, "Cashflow Table", ln=True)

        pdf.set_font("Helvetica", "", 10)
        for i in range(len(cf)):
            y = cf["Year"].iloc[i]
            n = cf["CFD_Payments_GBP"].iloc[i]
            d = dcf[i]
            pdf.cell(0, 8, f"{y}: Nominal = £{n:,.0f}, Discounted = £{d:,.0f}", ln=True)

        try:
            import plotly.io as pio
            chart_img = BytesIO()
            pio.write_image(fig, chart_img, format="png")
            chart_img.seek(0)
            pdf.add_page()
            pdf.image(chart_img, x=10, y=30, w=190)
        except Exception:
            pdf.add_page()
            pdf.set_font("Helvetica", "I", 12)
            pdf.multi_cell(0, 10, "⚠️ Chart image not included. Please install 'kaleido' to enable chart rendering.")

        # Use UTF-8 friendly output
        pdf_bytes = pdf.output(dest="S").encode("utf-8")
        st.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name="npv_irr_report.pdf",
            mime="application/pdf"
        )

if __name__ == "__main__":
    main()
