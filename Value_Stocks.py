import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="Global Stock Screener (EODHD)", layout="wide")

st.title("🌍 Global Stock Screener - EOD Historical Data")
st.markdown("""
Screening stocks based on:
- **P/E < 20**
- **Debt/Equity < 0.5**
- **ROE ≥ 15%**
- **ROIC > 12%**
- **Earnings Growth YoY > 5%**
""")

API_KEY = "6825d98dd66162.06437288"

exchange_map = {
    "US": ["US"],
    "Europe": ["LSE", "XETRA", "SW", "PA", "MI"],
    "Asia": ["TSE", "HK", "KO"]
}

region = st.selectbox("Select Region to Screen:", list(exchange_map.keys()))

@st.cache_data(show_spinner=False)
def get_exchange_symbols(exchange_code):
    url = f"https://eodhistoricaldata.com/api/exchange-symbol-list/{exchange_code}?api_token={API_KEY}&type=Common+Stock"
    r = requests.get(url)
    try:
        data = r.json()
        if isinstance(data, list):
            return data
        else:
            return []
    except:
        return []

@st.cache_data(show_spinner=False)
def get_fundamentals(symbol):
    url = f"https://eodhistoricaldata.com/api/fundamentals/{symbol}?api_token={API_KEY}"
    r = requests.get(url)
    return r.json()

results = []
total_checked = 0

st.write(f"Loading stocks from **{region}** exchanges...")

for ex in exchange_map[region]:
    symbols = get_exchange_symbols(ex)
    if not isinstance(symbols, list):
        continue

    for stock in symbols[:100]:  # limit to 100 per exchange
        code = stock.get("Code")
        name = stock.get("Name")
        symbol = f"{code}.{ex}"

        try:
            data = get_fundamentals(symbol)
            val = data.get("Valuation", {})
            fin = data.get("Financials", {}).get("quarterly", {}).get("balance_sheet", {})
            highlights = data.get("Highlights", {})
            growth = data.get("Growth", {})

            pe = highlights.get("PERatio")
            debt = fin.get("totalDebt", {})
            equity = fin.get("totalEquity", {})
            debt_equity = None
            if debt and equity:
                last_debt = list(debt.values())[0]
                last_equity = list(equity.values())[0]
                if last_equity != 0:
                    debt_equity = last_debt / last_equity

            roe = highlights.get("ReturnOnEquityTTM")
            roic = highlights.get("ReturnOnInvestedCapitalTTM")
            eps_growth = growth.get("EarningsPerShare")

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
        time.sleep(1)  # Respect EODHD rate limits

# Display results
df = pd.DataFrame(results)

if not df.empty:
    df.sort_values("ROIC (%)", ascending=False, inplace=True)
    st.success(f"Found {len(df)} matching stocks out of {total_checked} scanned.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks matched all criteria.")
