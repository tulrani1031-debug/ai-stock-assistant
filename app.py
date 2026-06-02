import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 설정
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")
st_autorefresh(interval=60000)

# 데이터 엔진
def get_market_data(targets):
    results = []
    for ticker in targets:
        try:
            t = yf.Ticker(ticker)
            df = t.history(period="1mo")
            if len(df) < 20: continue
            curr = float(df['Close'].iloc[-1])
            vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
            vol_ratio = df['Volume'].iloc[-1] / vol_avg
            change = ((curr - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100
            score = vol_ratio * (1 + (abs(change)/100))
            results.append({"name": t.info.get('shortName', ticker), "price": curr, "change": change, "vol": vol_ratio, "score": score})
        except: continue
    return results

targets = ["005930.KS", "000660.KS", "005380.KS", "NVDA", "TSLA", "AAPL", "PLTR", "MSFT", "AMD", "META"]
data = get_market_data(targets)
data.sort(key=lambda x: x['score'], reverse=True)

# 2. UI 구성 (처음의 깔끔한 스타일로 복구)
st.title("🔮 서윤의 주식 마법사 PRO")
tab1, tab2, tab3 = st.tabs(["🔥 실시간 시장 주도주", "⚡ 급등 예정", "📉 급하락 포착"])

with tab1:
    st.subheader("현재 가장 뜨거운 종목 TOP 5")
    cols = st.columns(5)
    for i, item in enumerate(data[:5]):
        with cols[i]:
            st.metric(label=item['name'], value=f"{item['price']:.2f}", delta=f"{item['change']:.2f}%")
            st.caption(f"거래량: {item['vol']:.1f}배")

with tab2:
    st.subheader("⚡ 거래량이 폭발하는 급등 신호")
    for item in [d for d in data if d['vol'] > 1.2]:
        with st.expander(f"🚀 {item['name']} (거래량 {item['vol']:.1f}배 급증)"):
            st.write(f"현재가: {item['price']:.2f} | 변동률: {item['change']:.2f}%")

with tab3:
    st.subheader("📉 기술적 반등이 필요한 급하락 종목")
    for item in [d for d in data if d['change'] <= -2.0]:
        with st.expander(f"📉 {item['name']} ({item['change']:.1f}% 하락 중)"):
            st.write(f"과매도 구간 주의! 현재가: {item['price']:.2f}")