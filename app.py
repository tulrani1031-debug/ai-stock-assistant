import streamlit as st
import yfinance as yf
import requests
from streamlit_autorefresh import st_autorefresh
from datetime import datetime, timedelta

# 1. 실시간 환율
def get_realtime_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return requests.get(url).json()['rates']['KRW']
    except: return 1380.0

# 2. 분석 엔진 (저점/고점 및 수익률 계산 로직)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        
        curr = float(df['Close'].iloc[-1])
        std = df['Close'].rolling(20).std().iloc[-1]
        
        # 저점/고점 산출
        low = curr * (1 - (std/curr)*0.8) # 2~4일 내 반등 예상 저점
        high = curr * (1 + (std/curr)*1.2) # 10~15일 내 도달 예상 고점
        
        profit_pct = ((high - curr) / curr) * 100
        qty = int(budget / (curr if is_dom else curr * rate))
        
        return {"price": curr, "low": low, "high": high, "profit": profit_pct, "qty": qty}
    except: return None

# 3. 메인 화면
st.set_page_config(layout="wide")
st_autorefresh(interval=60000)
rate = get_realtime_rate()
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)

kor_list = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("네이버", "035420.KS"), ("카카오", "035720.KS")]
usa_list = [("엔비디아", "NVDA"), ("테슬라", "TSLA"), ("애플", "AAPL"), ("팔란티어", "PLTR"), ("마이크로소프트", "MSFT")]

col1, col2 = st.columns(2)

# 출력 로직
for col, title, stocks, dom in [(col1, "🇰🇷 국내 종목", kor_list, True), (col2, "🇺🇸 해외 종목", usa_list, False)]:
    with col:
        st.subheader(title)
        for name, ticker in stocks:
            res = get_analysis(ticker, dom, budget, rate)
            if res:
                # 가독성을 높이기 위한 카드형 구성
                with st.expander(f"**{name}** (예상 수익률: +{res['profit']:.1f}%)", expanded=True):
                    st.write(f"💰 현재가: {res['price']:,.0f}원")
                    st.write(f"📉 저점매수: {res['low']:,.0f}원 (2~4일 내)")
                    st.write(f"📈 고점매도: {res['high']:,.0f}원 (10~15일 내)")
                    st.write(f"📦 예상 수량: {res['qty']}주")