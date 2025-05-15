import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Global Stock Screener (Finnhub)", layout="wide")

st.title("🌍 Global Stock Screener - Finnhub")
st.markdown("""
Screening stocks based on:
- **P/E < 20**
- **Debt/Equity < 0.5**
- **ROE ≥ 15%**
- **ROIC > 12%**
- **Earnings Growth YoY > 5%**
""")

API_KEY = "d0isuihr01qofpon3nu0d0isuihr01qofpon3nug"

# Exchanges by region
exchange_map = {
    "US": ["US"],
    "Europe": ["XETR", "LSE", "SWX", "EPA", "BIT"],
    "Asia": ["TSE", "HKEX", "KRX"]
}

region = st.selectbox("Select Region to Screen:", list(exchange_map.keys()))
st.write(f"Loading stocks from **{region}** exchanges...")

@st.cache_data(show_spinner=False)
def get_symbols(exchange):
    url = f"https://finnhub.io/api/v1/stock/symbol?exchange={exchange}&token={API_KEY}"
    resp = requests.get(url)
    return resp.json()

@st.cache_data(show_spinner=False)
def get_metrics(symbol):
    url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={API_KEY}"
    resp = requests.get(url)
    return resp.json()

results = []
total_checked = 0

for ex in exchange_map[region]:
    symbols = get_symbols(ex)
    for stock in symbols[:300]:  # limit per exchange for free tier
        symbol = stock.get("symbol")
        name = stock.get("description")

        try:
            metrics = get_metrics(symbol)
            data = metrics.get("metric", {})

            pe = data.get("peNormalizedAnnual")
            debt_equity = data.get("totalDebt/totalEquityAnnual")
            roe = data.get("roeAnnual")
            roic = data.get("roicAnnual")
            eps_growth = data.get("epsGrowth")

            if None in (pe, debt_equity, roe, roic, eps_growth):
                continue

            if (
                pe < 20 and
                debt_equity < 0.5 and
                roe >= 15 and
                roic > 12 and
                eps_growth > 5
            ):
                results.append({
                    "Symbol": symbol,
                    "Company": name,
                    "PE": round(pe, 2),
                    "Debt/Equity": round(debt_equity, 2),
                    "ROE (%)": round(roe, 2),
                    "ROIC (%)": round(roic, 2),
                    "EPS Growth YoY (%)": round(eps_growth, 2)
                })

        except Exception as e:
            continue

        total_checked += 1
        if total_checked % 50 == 0:
            st.info(f"Checked {total_checked} stocks so far...")
        time.sleep(0.2)  # Respect Finnhub rate limit

# Display results
df = pd.DataFrame(results)

if not df.empty:
    df.sort_values("ROIC (%)", ascending=False, inplace=True)
    st.success(f"Found {len(df)} matching stocks out of {total_checked} scanned.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks matched all criteria.")
