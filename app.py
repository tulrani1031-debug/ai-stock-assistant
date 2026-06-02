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

# 2. 분석 엔진 (급락 계산 로직 추가)
def get_analysis(ticker, is_dom, budget_krw, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        prev = float(df['Close'].iloc[-2])
        change_pct = ((curr - prev) / prev) * 100
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        
        std = df['Close'].rolling(20).std().iloc[-1]
        price_krw = curr if is_dom else curr * rate
        
        return {
            "price_orig": curr, "price_krw": price_krw,
            "change_pct": change_pct, "vol": vol_ratio,
            "qty": int(budget_krw / price_krw)
        }
    except: return None

# 3. 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO")
rate = get_realtime_rate()
budget_krw = st.sidebar.number_input("예산(KRW)", value=1000000, step=10000)

# 탭 구조: 추천, 급등, 급락
tab1, tab2, tab3 = st.tabs(["🚀 추천 종목", "⚡ 급등 예정", "📉 급하락 포착"])

full_list = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), 
             ("엔비디아", "NVDA"), ("테슬라", "TSLA"), ("애플", "AAPL"), ("팔란티어", "PLTR")]

with tab1:
    col1, col2 = st.columns(2)
    for col, title, stocks, dom in [(col1, "🇰🇷 국내 종목", kor_list, True), (col2, "🇺🇸 해외 종목", usa_list, False)]:
        with col:
            st.subheader(title)
            for name, ticker in stocks:
                res = get_analysis(ticker, dom, budget_krw, rate)
                if res:
                    with st.expander(f"**{name}** (예상수익: +{res['profit']:.1f}%)", expanded=True):
                        price_d = f"${res['price_orig']:.2f} (₩{res['price_krw']:,.0f})" if not dom else f"₩{res['price_krw']:,.0f}"
                        st.write(f"💰 현재가: {price_d} | 📦 매수: {res['qty']}주")
                        st.write(f"📉 저점: {res['low']:.0f} | 📈 고점: {res['high']:.0f}")

with tab2:
    st.header("⚡ 지금 막 급등 시작하는 종목")
    for name, ticker in full_list:
        res = get_analysis(ticker, ".KS" in ticker, budget_krw, rate)
        if res and res['vol'] > 1.2:
            st.warning(f"🚀 **{name}** - 거래량 {res['vol']:.1f}배 폭발!")

with tab3:
    st.header("📉 급하락 포착 (기술적 반등 구간)")
    for name, ticker in full_list:
        res = get_analysis(ticker, ".KS" in ticker, budget_krw, rate)
        # 3% 이상 하락 시 급락으로 간주
        if res and res['change_pct'] <= -3.0:
            st.error(f"📉 **{name}** - 가격 {res['change_pct']:.1f}% 하락! (과매도 구간 주의)")