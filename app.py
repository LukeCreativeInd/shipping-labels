import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from io import BytesIO
import math

st.set_page_config(page_title="Shipping Label Generator", layout="centered")
st.title("📦 Shipping Label Generator")

uploaded_file = st.file_uploader("Upload Manifest CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Assumed structure — adapt as needed
    required_cols = ["Name", "Address1", "Address2", "City", "State", "Postcode", "Phone", "Carton Count"]
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
    else:
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(288, 432))  # 4x6 inches in points

        for _, row in df.iterrows():
            try:
                carton_count = int(row["Carton Count"])
            except:
                carton_count = 1

            for i in range(1, carton_count + 1):
                c.setFont("Helvetica-Bold", 14)
                c.drawString(20, 400, f"To: {row['Name']}")
                c.setFont("Helvetica", 12)
                c.drawString(20, 380, row["Address1"])
                if row["Address2"]: c.drawString(20, 360, row["Address2"])
                c.drawString(20, 340, f"{row['City']}, {row['State']} {row['Postcode']}")
                c.drawString(20, 320, f"Phone: {row['Phone']}")
                c.drawString(20, 300, f"Carton {i} of {carton_count}")
                c.showPage()

        c.save()
        buffer.seek(0)

        st.success("Shipping labels created!")
        st.download_button("Download Labels PDF", buffer, file_name="shipping_labels.pdf", mime="application/pdf")
