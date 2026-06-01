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
def get_analysis(ticker, is_dom, budget_krw, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1]) # 현지 통화 기준 가격
        std = df['Close'].rolling(20).std().iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        
        # 원화 기준 예산 계산
        budget_usd = budget_krw / rate
        
        price_in_currency = curr
        curr_krw = curr if is_dom else curr * rate
        
        low = curr * (1 - (std/curr)*0.8)
        high = curr * (1 + (std/curr)*1.2)
        qty = int((budget_krw / curr_krw))
        
        return {
            "price_orig": curr, "price_krw": curr_krw,
            "low": low, "high": high, "profit": ((high-curr)/curr)*100, 
            "qty": qty, "vol": vol_ratio
        }
    except: return None

# 3. 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO")
rate = get_realtime_rate()

# 자산 관리: 원화 및 달러 동시 표시
col_side1, col_side2 = st.sidebar.columns(2)
with col_side1:
    budget_krw = st.number_input("예산(KRW)", value=1000000, step=10000)
with col_side2:
    st.write("예산(USD)")
    st.info(f"${budget_krw/rate:,.2f}")

st.sidebar.metric("실시간 환율", f"{rate:,.2f} KRW")

kor_list = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("네이버", "035420.KS"), ("카카오", "035720.KS")]
usa_list = [("엔비디아", "NVDA"), ("테슬라", "TSLA"), ("애플", "AAPL"), ("팔란티어", "PLTR"), ("마이크로소프트", "MSFT")]

tab1, tab2 = st.tabs(["🚀 추천 종목 분석", "⚡ 급등 예정 포착"])

with tab1:
    col1, col2 = st.columns(2)
    for col, title, stocks, dom in [(col1, "🇰🇷 국내 종목", kor_list, True), (col2, "🇺🇸 해외 종목", usa_list, False)]:
        with col:
            st.subheader(title)
            for name, ticker in stocks:
                res = get_analysis(ticker, dom, budget_krw, rate)
                if res:
                    with st.expander(f"**{name}** (수익: +{res['profit']:.1f}%)", expanded=True):
                        # 해외 주식은 달러와 원화 병기
                        price_display = f"${res['price_orig']:.2f} (₩{res['price_krw']:,.0f})" if not dom else f"₩{res['price_krw']:,.0f}"
                        st.write(f"💰 현재가: {price_display}")
                        st.write(f"📦 매수 가능: {res['qty']}주")
                        st.write(f"📉 저점: {res['low']:,.0f} | 📈 고점: {res['high']:,.0f}")

with tab2:
    st.header("⚡ 지금 막 급등 시작하는 종목")
    for name, ticker in (kor_list + usa_list):
        res = get_analysis(ticker, ".KS" in ticker, budget_krw, rate)
        if res and 1.2 <= res['vol'] <= 3.0:
            st.warning(f"🚀 **{name}** - 거래량 {res['vol']:.1f}배 폭발! (매수 메타 확인)")