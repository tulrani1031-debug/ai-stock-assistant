import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v3.0")

# 1. 데이터 분석 함수 (AI 추정치 산출)
@st.cache_data(ttl=600)
def get_advanced_analysis(ticker, is_domestic, budget):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty: return None
        
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        # AI 추정치 로직
        low_price = curr * (1 - (std / curr) * 1.2) # 변동성 기반 저점
        high_price = curr * (1 + (std / curr) * 1.5) # 변동성 기반 고점
        
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + (df['Volume'].iloc[-1] > df['Volume'].mean())*20 + 20)
        
        # 매수 타이밍 분석
        if curr < ma20 and score > 60: status = "🟢 지금 매수 적합"
        elif curr > high_price * 0.95: status = "🔴 관망 권장"
        else: status = "🟡 분할 매수 권장"
        
        # 재무 계산
        qty = int(budget / curr) if is_domestic else int((budget/1350) / curr) # 환율 임시 1350
        invested = qty * curr
        cash = budget - (invested if is_domestic else invested * 1350)
        profit_amt = (high_price - curr) * qty
        profit_pct = ((high_price - curr) / curr) * 100
        
        return {
            "price": curr, "score": score, "low": low_price, "high": high_price,
            "status": status, "qty": qty, "invested": invested, "cash": cash,
            "p_amt": profit_amt, "p_pct": profit_pct, "chart": df['Close']
        }
    except: return None

# 2. 메인 UI 및 로직
st.title("🔮 서윤의 주식 마법사 PRO v3.0")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)

tab1, tab2 = st.tabs(["📊 종목별 정밀 분석", "⚔️ 종목 비교 배틀"])

with tab1:
    stocks = [("삼성전자", "005930.KS", True), ("NVIDIA", "NVDA", False), ("Tesla", "TSLA", False)]
    for name, ticker, is_dom in stocks:
        res = get_advanced_analysis(ticker, is_dom, budget)
        if res:
            with st.expander(f"📌 {name} | 점수: {res['score']} | {res['status']}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("현재가", f"{'₩' if is_dom else '$'}{res['price']:.2f}")
                c2.metric("예상 저점", f"{'₩' if is_dom else '$'}{res['low']:.2f}", "2~4일 이내")
                c3.metric("예상 고점", f"{'₩' if is_dom else '$'}{res['high']:.2f}", "10~15일 이내")
                c4.metric("예상 수익", f"+{res['p_pct']:.1f}%", f"+{res['p_amt']:.0f}")
                
                st.write(f"**매수 타이밍 사유:** {res['status']} (AI 추정치 기반)")
                st.write(f"**자금 운영:** 구매 가능 {res['qty']}주 | 총 투자 {res['invested']:.0f} | 남은 현금 {res['cash']:.0f}")
                st.line_chart(res['chart'])
                st.caption("※ 이 지표는 이동평균선과 변동성을 활용한 AI 추정치이며, 미래를 확정하지 않습니다.")

with tab2:
    st.info("종목을 선택해 AI 승자를 결정하세요.")
    # (비교 로직 생략)