import streamlit as st
import pandas as pd
import asyncio
from playwright.async_api import async_playwright
import tempfile

st.set_page_config(page_title="ETA Tracker", layout="wide")
st.title("📦 Master B/L ETA Tracker")

st.markdown("""
Upload an Excel file with the following headers:
- **CARRIER**
- **Master BL**
- **SCI**

The app will fetch ETA from supported carrier websites (starting with ONE).
""")

uploaded_file = st.file_uploader("Upload Excel file", type=[".xlsx"])

# Supported carriers in this version
supported_carriers = ["ONE"]

results = []

async def track_one_bl(master_bl):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto("https://ecommerce.one-line.com/one-ecom/en/ecommerce/track")
            await page.fill("input[name='searchNo']", master_bl)
            await page.click("button:has-text('Track')")
            await page.wait_for_timeout(6000)
            content = await page.inner_text(".result-info")
        except Exception as e:
            content = f"Error fetching: {str(e)}"
        await browser.close()
        return content

if uploaded_file:
    df = pd.read_excel(uploaded_file, header=1)
    df = df.rename(columns={
        df.columns[0]: "CARRIER",
        df.columns[1]: "CONTAINER NO",
        df.columns[2]: "House BL",
        df.columns[3]: "Master BL",
        df.columns[4]: "SCI",
    })

    df = df.dropna(subset=["Master BL", "CARRIER", "SCI"])
    st.write("### Uploaded Data", df[["SCI", "CARRIER", "Master BL"]])

    if st.button("🔍 Start ETA Tracking"):
        with st.spinner("Tracking in progress..."):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            for _, row in df.iterrows():
                carrier = str(row["CARRIER"]).strip().upper()
                mbl = str(row["Master BL"]).strip()
                sci = str(row["SCI"]).strip()

                if carrier == "ONE":
                    raw_info = loop.run_until_complete(track_one_bl(mbl))
                    # Simple ETA extract
                    eta = "N/A"
                    for line in raw_info.splitlines():
                        if "ETA" in line:
                            eta = line.strip()
                            break
                    results.append({
                        "SCI": sci,
                        "Master BL": mbl,
                        "Carrier": carrier,
                        "ETA": eta,
                        "Raw Info": raw_info
                    })
                else:
                    results.append({
                        "SCI": sci,
                        "Master BL": mbl,
                        "Carrier": carrier,
                        "ETA": "Unsupported carrier",
                        "Raw Info": "Only ONE Line supported in this version"
                    })

            result_df = pd.DataFrame(results)
            st.success("Tracking complete!")
            st.write(result_df)

            # Offer Excel download
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                result_df.to_excel(tmp.name, index=False)
                st.download_button("📥 Download Result Excel", tmp.name, file_name="ETA_Results.xlsx")
