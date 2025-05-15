import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Global Stock Screener", layout="wide")

st.title("🌍 Global Stock Screener")
st.markdown("""
Screening stocks based on:
- **P/E < 20**
- **Debt/Equity < 0.5**
- **ROE ≥ 15%**
- **ROIC (proxied with ROA) > 12%**
- **Earnings Growth YoY > 5%**
""")

# Define tickers from different markets
tickers = [
    # US
    'AAPL', 'MSFT', 'GOOGL', 'JNJ', 'UNH', 'TSLA',
    # Europe
    'NESN.SW', 'SIE.DE', 'SAN.PA', 'RDSA.AS', 'AZN.L',
    # Asia
    '6758.T', '005930.KS', '9984.T', '2317.TW', '0700.HK'
]

results = []

for ticker in tickers:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        pe = info.get("trailingPE", None)
        debt_equity = info.get("debtToEquity", None)
        roe = info.get("returnOnEquity", None)
        roic = info.get("returnOnAssets", None)  # Proxy for ROIC
        eps_growth = info.get("earningsQuarterlyGrowth", None)

        if None in (pe, debt_equity, roe, roic, eps_growth):
            continue

        # Convert to usable format
        debt_equity /= 100
        roe *= 100
        roic *= 100
        eps_growth *= 100

        if (
            pe < 20 and
            debt_equity < 0.5 and
            roe >= 15 and
            roic > 12 and
            eps_growth > 5
        ):
            results.append({
                "Ticker": ticker,
                "PE": round(pe, 2),
                "Debt/Equity": round(debt_equity, 2),
                "ROE (%)": round(roe, 2),
                "ROIC proxy (ROA %)": round(roic, 2),
                "EPS Growth YoY (%)": round(eps_growth, 2)
            })

    except Exception as e:
        st.warning(f"Data issue with {ticker}: {e}")

# Display results
df = pd.DataFrame(results)

if not df.empty:
    df.sort_values("ROIC proxy (ROA %)", ascending=False, inplace=True)
    st.success(f"Found {len(df)} stocks matching criteria.")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No stocks matched all criteria.")