import streamlit as st
import pandas as pd
import tempfile
import requests

st.set_page_config(page_title="ETA Tracker", layout="wide")
st.title("📦 Container ETA Tracker")

st.markdown("Upload an Excel file with columns: `SCI`, `CARRIER`, and `Master BL`")

uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("✅ Uploaded file preview:")
    st.dataframe(df)

    if st.button("🔍 Fetch ETA"):
        st.info("⏳ Contacting backend... please wait.")
        try:
            response = requests.post(
                "https://eta-agent.onrender.com/track",  # Replace with your actual backend URL
                files={"file": uploaded_file.getvalue()}
            )
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                    tmp.write(response.content)
                    tmp.flush()
                    result_df = pd.read_excel(tmp.name)
                    st.success("✅ ETA fetched!")
                    st.write(result_df)
                    st.download_button("📥 Download Results", tmp.name, file_name="ETA_Results.xlsx")
            else:
                st.error(f"❌ Error: Server returned status code {response.status_code}")
        except Exception as e:
            st.error(f"❌ Error contacting backend: {str(e)}")
else:
    st.warning("📂 Please upload an Excel file to begin.")