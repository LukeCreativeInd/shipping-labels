import streamlit as st
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO

st.set_page_config(page_title="Shipping Label Generator", layout="centered")
st.title("📦 Shipping Label Generator")

uploaded_file = st.file_uploader("Upload Manifest File (CSV or Excel)", type=["csv", "xlsx"])

df = None

if uploaded_file:
    file_type = uploaded_file.name.split(".")[-1].lower()

    try:
        if file_type == "csv":
            df = pd.read_csv(uploaded_file)
        elif file_type == "xlsx":
            df = pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or XLSX file.")
    except Exception as e:
        st.error(f"Error reading file: {e}")

    if df is not None:
        # Rename columns for consistency
        column_mapping = {
            "Deliver to": "Name",
            "Address 1": "Address1",
            "Address 2": "Address2",
            "Postal Code": "Postcode",
            "Phone No.": "Phone",
            "No. of Shipping Labels": "Carton Count"
        }
        df.rename(columns=column_mapping, inplace=True)

        if st.button("Generate Shipping Labels"):
            required_cols = ["Name", "Address1", "Address2", "State", "Postcode", "Phone", "Carton Count", "D.O. No.", "Group"]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                buffer = BytesIO()
                c = canvas.Canvas(buffer, pagesize=(4 * inch, 6 * inch))  # 4x6 inches

                for _, row in df.iterrows():
                    try:
                        carton_count = int(row["Carton Count"])
                    except:
                        carton_count = 1

                    for i in range(1, carton_count + 1):
                        # Order Number (Top left)
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(30, 770, str(row["D.O. No."]))

                        # "SHIP TO:"
                        c.setFont("Helvetica-Bold", 10)
                        c.drawString(30, 740, "SHIP TO:")

                        # Recipient Name
                        c.setFont("Helvetica", 14)
                        c.drawString(30, 715, str(row["Name"]))

                        # Address lines
                        c.setFont("Helvetica", 12)
                        c.drawString(30, 690, str(row["Address1"]))

                        if pd.notna(row["Address2"]) and str(row["Address2"]).strip():
                            c.drawString(30, 670, str(row["Address2"]))
                            y_postal = 650
                        else:
                            y_postal = 670

                        # State and Postcode (as City line)
                        c.drawString(30, y_postal, f"{row['State']} {row['Postcode']}")

                        # Phone
                        c.drawString(30, y_postal - 30, f"Phone: {row['Phone']}")

                        # Group (bottom left)
                        c.setFont("Helvetica", 12)
                        c.drawString(30, 30, str(row["Group"]))

                        # Carton Count (bottom right)
                        c.setFont("Helvetica-Bold", 16)
                        c.drawRightString(270, 30, f"{i}/{carton_count}")

                        c.showPage()

                c.save()
                buffer.seek(0)

                st.success("Shipping labels created!")
                st.download_button("Download Labels PDF", buffer, file_name="shipping_labels.pdf", mime="application/pdf")
