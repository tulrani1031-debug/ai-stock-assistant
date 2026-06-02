import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import pandas as pd

# 1. 설정
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")
st_autorefresh(interval=60000)

# 2. 데이터 엔진 (한 번에 가져와서 캐싱)
@st.cache_data(ttl=60)
def get_market_data(all_tickers):
    results = []
    for ticker in all_tickers:
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if len(df) < 20: continue
            
            curr = float(df['Close'].iloc[-1])
            prev = float(df['Close'].iloc[-2])
            change = ((curr - prev) / prev) * 100
            
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / vol_avg
            
            std = df['Close'].rolling(20).std().iloc[-1]
            low = curr * (1 - (std/curr)*0.5)
            high = curr * (1 + (std/curr)*0.8)
            
            results.append({
                "name": t.info.get('shortName', ticker),
                "ticker": ticker,
                "price": curr,
                "change": change,
                "vol": vol_ratio,
                "low": low,
                "high": high,
                "is_dom": ".KS" in ticker
            })
        except: continue
    return results

# 종목 리스트
kor_tickers = ["005930.KS", "000660.KS", "005380.KS", "035420.KS", "035720.KS"]
usa_tickers = ["NVDA", "TSLA", "AAPL", "PLTR", "MSFT"]
data = get_market_data(kor_tickers + usa_tickers)

# 3. UI 구성
st.title("🔮 서윤의 주식 마법사 PRO")
tab1, tab2, tab3 = st.tabs(["🚀 추천 TOP 5", "⚡ 급등 예정", "📉 급하락 포착"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🇰🇷 국내 주식")
        for item in [d for d in data if d['is_dom']]:
            with st.expander(f"{item['name']} ({item['change']:.2f}%)"):
                st.write(f"현재가: {item['price']:.0f}원 | 저점: {item['low']:.0f}원 | 고점: {item['high']:.0f}원")
    with col2:
        st.subheader("🇺🇸 해외 주식")
        for item in [d for d in data if not d['is_dom']]:
            with st.expander(f"{item['name']} ({item['change']:.2f}%)"):
                st.write(f"현재가: ${item['price']:.2f} | 저점: ${item['low']:.2f} | 고점: ${item['high']:.2f}")

with tab2:
    st.subheader("⚡ 급등 신호 (거래량 1.2배 이상)")
    for item in [d for d in data if d['vol'] > 1.2]:
        st.warning(f"🚀 {item['name']} - 거래량 {item['vol']:.1f}배 폭발! (현재가: {item['price']:.2f})")

with tab3:
    st.subheader("📉 급하락 포착 (-2% 이상 하락)")
    for item in [d for d in data if d['change'] <= -2.0]:
        st.error(f"📉 {item['name']} - {item['change']:.1f}% 급락! (현재가: {item['price']:.2f})")