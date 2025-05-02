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
        column_mapping = {
            "Deliver to": "Name",
            "Address 1": "Address1",
            "Address 2": "Suburb",
            "Postal Code": "Postcode",
            "Phone No.": "Phone",
            "No. of Shipping Labels": "Carton Count"
        }
        df.rename(columns=column_mapping, inplace=True)

        if st.button("Generate Shipping Labels"):
            required_cols = ["Name", "Address1", "Suburb", "State", "Postcode", "Phone", "Carton Count", "D.O. No.", "Group"]
            missing_cols = [col for col in required_cols if col not in df.columns]

            if missing_cols:
                st.error(f"Missing required columns: {', '.join(missing_cols)}")
            else:
                buffer = BytesIO()
                label_width, label_height = 4 * inch, 6 * inch
                c = canvas.Canvas(buffer, pagesize=(label_width, label_height))

                for _, row in df.iterrows():
                    try:
                        carton_count = int(row["Carton Count"])
                    except:
                        carton_count = 1

                    for i in range(1, carton_count + 1):
                        phone = str(row["Phone"]).strip()
                        if phone.isdigit() and len(phone) == 9:
                            phone = "0" + phone

                        # Order Number
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(0.4 * inch, 5.7 * inch, str(row["D.O. No."]))

                        # SHIP TO label
                        c.setFont("Helvetica-Bold", 10)
                        c.drawString(0.4 * inch, 5.4 * inch, "SHIP TO:")

                        # Recipient Name + Address
                        c.setFont("Helvetica", 13)
                        c.drawString(0.4 * inch, 5.1 * inch, str(row["Name"]))
                        c.setFont("Helvetica", 12)
                        c.drawString(0.4 * inch, 4.85 * inch, str(row["Address1"]))
                        c.drawString(0.4 * inch, 4.65 * inch, str(row["Suburb"]))
                        c.drawString(0.4 * inch, 4.45 * inch, f"{row['State']} {row['Postcode']}")
                        c.drawString(0.4 * inch, 4.2 * inch, f"Phone: {phone}")

                        # Bottom info
                        c.setFont("Helvetica", 11)
                        c.drawString(0.4 * inch, 0.4 * inch, str(row["Group"]))
                        c.setFont("Helvetica-Bold", 16)
                        c.drawRightString(3.6 * inch, 0.4 * inch, f"{i}/{carton_count}")

                        c.showPage()

                c.save()
                buffer.seek(0)

                st.success("Shipping labels created!")
                st.download_button("Download Labels PDF", buffer, file_name="shipping_labels.pdf", mime="application/pdf")
