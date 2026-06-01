import streamlit as st
import yfinance as yf
import requests
from streamlit_autorefresh import st_autorefresh

# 1. 설정 및 실시간 환율
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")
st_autorefresh(interval=60000)

def get_realtime_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return requests.get(url).json()['rates']['KRW']
    except: return 1380.0

# 2. 분석 엔진
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / vol_avg
        std = df['Close'].rolling(20).std().iloc[-1]
        
        low = curr * (1 - (std/curr)*0.8)
        high = curr * (1 + (std/curr)*1.2)
        qty = int(budget / (curr if is_dom else curr * rate))
        
        return {"price": curr, "low": low, "high": high, "profit": ((high-curr)/curr)*100, "qty": qty, "vol": vol_ratio}
    except: return None

# 3. 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO")
rate = get_realtime_rate()
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
st.sidebar.metric("현재 환율", f"{rate:,.2f} KRW")

kor_list = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("네이버", "035420.KS"), ("카카오", "035720.KS")]
usa_list = [("엔비디아", "NVDA"), ("테슬라", "TSLA"), ("애플", "AAPL"), ("팔란티어", "PLTR"), ("마이크로소프트", "MSFT")]

tab1, tab2 = st.tabs(["🚀 추천 종목 분석", "⚡ 급등 예정 포착"])

with tab1:
    col1, col2 = st.columns(2)
    for col, title, stocks, dom in [(col1, "🇰🇷 국내 종목", kor_list, True), (col2, "🇺🇸 해외 종목", usa_list, False)]:
        with col:
            st.subheader(title)
            for name, ticker in stocks:
                res = get_analysis(ticker, dom, budget, rate)
                if res:
                    with st.expander(f"**{name}** (예상수익: +{res['profit']:.1f}%)", expanded=True):
                        st.write(f"💰 현재가: {res['price']:,.0f}원 | 📦 매수: {res['qty']}주")
                        st.write(f"📉 저점: {res['low']:,.0f}원 (2~4일 내)")
                        st.write(f"📈 고점: {res['high']:,.0f}원 (10~15일 내)")

with tab2:
    st.header("⚡ 지금 막 급등 시작하는 종목 (거래량 폭발)")
    for name, ticker in (kor_list + usa_list):
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and 1.2 <= res['vol'] <= 3.0:
            st.warning(f"🚀 **{name}** - 거래량 평소의 {res['vol']:.1f}배! (매수 메타 확인)")