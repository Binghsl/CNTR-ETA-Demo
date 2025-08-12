import streamlit as st
import pandas as pd
import tempfile
import requests

st.set_page_config(page_title="Remote ETA Tracker", layout="wide")
st.title("📦 ONE Line ETA Tracker (Remote Agent)")

st.markdown("""
Upload an Excel file with the following columns:
- **SCI**
- **CARRIER** (currently supports only `ONE`)
- **Master BL**

ETA will be fetched remotely using an external agent (no API or Playwright needed locally).
""")

uploaded_file = st.file_uploader("Upload Excel", type=[".xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Uploaded Data", df)

    if st.button("🔍 Fetch ETA"):
        with st.spinner("Fetching ETA using remote agent..."):
            try:
                response = requests.post(
                    "https://eta-agent.bhsn.workers.dev/",
                    files={"file": uploaded_file.getvalue()}
                )
                if response.status_code == 200:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                        tmp.write(response.content)
                        tmp.flush()
                        result_df = pd.read_excel(tmp.name)
                        st.success("✅ ETA fetched successfully!")
                        st.write(result_df)
                        st.download_button("📥 Download Results", tmp.name, file_name="ETA_Results.xlsx")
                else:
                    st.error("Failed to fetch ETA. Status code: {}".format(response.status_code))
            except Exception as e:
                st.error(f"Error contacting remote agent: {str(e)}")
