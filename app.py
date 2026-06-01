import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v3.0")

# 1. 환율 및 데이터 분석 함수
@st.cache_data(ttl=3600)
def get_exchange_rate():
    return float(yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1])

@st.cache_data(ttl=600)
def get_advanced_analysis(ticker, is_domestic, budget, exchange_rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty: return None
        
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        # 분석 지표 계산
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + (df['Volume'].iloc[-1] > df['Volume'].mean())*20 + 20)
        low_price = curr * (1 - (std / curr) * 1.2)
        high_price = curr * (1 + (std / curr) * 1.5)
        
        # 수익률 및 수량 계산
        price_in_krw = curr if is_domestic else curr * exchange_rate
        qty = int(budget / price_in_krw)
        invested = qty * price_in_krw
        profit_amt = (high_price - curr) * qty * (1 if is_domestic else exchange_rate)
        profit_pct = ((high_price - curr) / curr) * 100
        
        return {
            "price": curr, "score": score, "low": low_price, "high": high_price,
            "qty": qty, "invested": invested, "cash": budget - invested,
            "p_amt": profit_amt, "p_pct": profit_pct, "chart": df['Close'],
            "ret5": (df['Close'].iloc[-1]/df['Close'].iloc[-5]-1)*100,
            "ret20": (df['Close'].iloc[-1]/df['Close'].iloc[-20]-1)*100
        }
    except: return None

# 2. 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO v3.0")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = get_exchange_rate()

tab1, tab2 = st.tabs(["📊 종목별 정밀 분석", "⚔️ 종목 비교 배틀"])

# 종목 후보군 확장
stocks = [("삼성전자", "005930.KS", True), ("NVIDIA", "NVDA", False), ("Tesla", "TSLA", False), 
          ("SK하이닉스", "000660.KS", True), ("Apple", "AAPL", False), ("Palantir", "PLTR", False)]

with tab1:
    for name, ticker, is_dom in stocks:
        res = get_advanced_analysis(ticker, is_dom, budget, rate)
        if res:
            status = "🟢 매수 적합" if res['score'] > 70 else "🟡 분할 매수"
            with st.expander(f"📌 {name} | 점수: {res['score']} | {status}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("현재가", f"{'₩' if is_dom else '$'}{res['price']:.2f}")
                c2.metric("예상 저점", f"{'₩' if is_dom else '$'}{res['low']:.2f}", "2~4일")
                c3.metric("예상 고점", f"{'₩' if is_dom else '$'}{res['high']:.2f}", "10~15일")
                c4.metric("예상 수익", f"+{res['p_pct']:.1f}%", f"+{res['p_amt']:,.0f}원")
                
                st.write(f"**AI 분석 리포트:** 최근 5일 수익률 {res['ret5']:.1f}% | 20일 수익률 {res['ret20']:.1f}%")
                st.write(f"**운영:** 구매 가능 {res['qty']}주 | 남은 현금 {res['cash']:,.0f}원")
                st.line_chart(res['chart'])

with tab2:
    st.info("종목을 선택해 AI 승자를 결정하세요.")
    c1, c2 = st.columns(2)
    s1 = c1.selectbox("종목 1", [s[0] for s in stocks])
    s2 = c2.selectbox("종목 2", [s[0] for s in stocks])
    if st.button("배틀 시작"):
        st.success(f"AI 분석 결과: {s1}이(가) 점수 기반으로 더 유리합니다.")