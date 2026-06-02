import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 설정 및 실시간 데이터 엔진
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")
st_autorefresh(interval=60000)

def get_market_data(targets):
    analysis_list = []
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
            analysis_list.append({
                "name": t.info.get('shortName', ticker),
                "ticker": ticker, "price": curr, "change": change, "vol": vol_ratio, "score": score
            })
        except: continue
    return analysis_list

# 공통 리스트
targets = ["005930.KS", "000660.KS", "005380.KS", "NVDA", "TSLA", "AAPL", "PLTR", "MSFT", "AMD", "META"]

# 2. UI 구조
st.title("🔮 서윤의 주식 마법사 PRO")
budget_krw = st.sidebar.number_input("예산(KRW)", value=1000000, step=10000)

tab1, tab2, tab3 = st.tabs(["🔥 실시간 시장 주도주 TOP 5", "⚡ 급등 예정", "📉 급하락 포착"])

# 분석 수행
data = get_market_data(targets)
leaders = sorted(data, key=lambda x: x['score'], reverse=True)

with tab1:
    st.subheader("현재 거래량과 변동성이 가장 활발한 TOP 5")
    cols = st.columns(5)
    for i, item in enumerate(leaders[:5]):
        with cols[i]:
            st.metric(label=item['name'], value=f"{item['price']:.2f}", delta=f"{item['change']:.2f}%")

with tab2:
    st.header("⚡ 지금 막 급등 시작하는 종목 (거래량 폭발)")
    for item in [d for d in data if d['vol'] > 1.5]:
        st.warning(f"🚀 **{item['name']}** - 거래량 {item['vol']:.1f}배 급증!")

with tab3:
    st.header("📉 급하락 포착 (과매도 구간)")
    for item in [d for d in data if d['change'] <= -3.0]:
        st.error(f"📉 **{item['name']}** - 가격 {item['change']:.1f}% 급락 중!")