import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Global Stock Screener (FMP)", layout="wide")

st.title("🌍 Global Stock Screener - Financial Modeling Prep (FMP)")
st.markdown("""
Screening stocks based on:
- **P/E < 20**
- **Debt/Equity < 0.5**
- **ROE ≥ 15%**
- **ROIC > 12%**
- **Earnings Growth YoY > 5%**
""")

API_KEY = ?apikey=BAvEOX0Bmy1RSmRQwoiIjFlL2iJgyOUd

exchange_map = {
    "US": "NASDAQ",
    "Europe": "EURONEXT",
    "Asia": "HKEX",
    "Japan": "TSE"  # Tokyo Stock Exchange
}

region = st.selectbox("Select Region to Screen:", list(exchange_map.keys()))
exchange = exchange_map[region]

@st.cache_data(show_spinner=False)
def get_stock_list(exchange):
    url = f"https://financialmodelingprep.com/api/v3/stock-screener?exchange={exchange}&apikey={API_KEY}"
    r = requests.get(url)
    return r.json()

@st.cache_data(show_spinner=False)
def get_fundamentals(symbol):
    url = f"https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={API_KEY}"
    r1 = requests.get(url).json()

    url2 = f"https://financialmodelingprep.com/api/v3/key-metrics-ttm/{symbol}?apikey={API_KEY}"
    r2 = requests.get(url2).json()

    url3 = f"https://financialmodelingprep.com/api/v3/ratios-ttm/{symbol}?apikey={API_KEY}"
    r3 = requests.get(url3).json()

    url4 = f"https://financialmodelingprep.com/api/v3/income-statement-growth/{symbol}?limit=1&apikey={API_KEY}"
    r4 = requests.get(url4).json()

    return r1, r2, r3, r4

results = []
total_checked = 0

st.write(f"Loading stocks from **{exchange}**...")

stocks = get_stock_list(exchange)

for stock in stocks[:100]:  # limit to 100 per region
    symbol = stock.get("symbol")
    name = stock.get("companyName")

    try:
        profile, key_metrics, ratios, growth = get_fundamentals(symbol)

        pe = float(profile[0].get("pe")) if profile and profile[0].get("pe") else None
        roe = float(ratios[0].get("returnOnEquityTTM")) if ratios and ratios[0].get("returnOnEquityTTM") else None
        roic = float(key_metrics[0].get("roic")) if key_metrics and key_metrics[0].get("roic") else None
        debt_equity = float(ratios[0].get("debtEquityRatio")) if ratios and ratios[0].get("debtEquityRatio") else None
        eps_growth = float(growth[0].get("epsgrowth")) * 100 if growth and growth[0].get("epsgrowth") else None

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

    except:
        continue

    total_checked += 1
    if total_checked % 20 == 0:
        st.info(f"Checked {total_checked} stocks so far...")
    time.sleep(0.5)  # throttle to respect FMP limits

# Display results
df = pd.DataFrame(results)

if not df.empty:
    df.sort_values("ROIC (%)", ascending=False, inplace=True)
    st.success(f"Found {len(df)} matching stocks out of {total_checked} scanned.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks matched all criteria.")
