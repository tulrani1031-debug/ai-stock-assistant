import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v5.0")

# 1. 데이터 처리 핵심 로직
@st.cache_data(ttl=600)
def get_full_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty: return None
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        # AI 수치
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + 30)
        fit = max(0, 100 - abs((budget * 0.3) - (curr * (1 if is_dom else rate))) / (budget * 0.3) * 100)
        low, high = curr * (1 - (std/curr)*1.2), curr * (1 + (std/curr)*1.5)
        
        return {
            "price": curr, "score": score, "fit": fit, "low": low, "high": high,
            "ma5": ma5, "ma20": ma20, "chart": df['Close'],
            "qty": int(budget / (curr if is_dom else curr * rate)),
            "cash": budget - (int(budget / (curr if is_dom else curr * rate)) * (curr if is_dom else curr * rate))
        }
    except: return None

# 2. UI 스타일링 및 카드 함수
def render_stock_card(name, ticker, is_dom, budget, rate):
    res = get_full_analysis(ticker, is_dom, budget, rate)
    if not res: return None
    
    with st.container(border=True):
        st.subheader(f"🚀 {name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("현재가", f"{'₩' if is_dom else '$'}{res['price']:.2f}")
        c2.metric("AI 점수", f"{res['score']}점", delta=f"적합도 {res['fit']:.0f}점")
        c3.metric("구매 가능", f"{res['qty']}주")
        
        st.progress(res['score']/100)
        st.caption(f"예상 수익률: {((res['high']-res['price'])/res['price']*100):.1f}% | 남은 현금: {res['cash']:,.0f}원")
    return (name, (res['score'] + res['fit']) / 2, res)

# 3. 메인 레이아웃
st.title("🔮 서윤의 주식 마법사 PRO v5.0")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

tab1, tab2 = st.tabs(["🚀 맞춤형 TOP 5 추천", "📊 상세 분석 대시보드"])

KOR = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS")]
US = [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL")]

with tab1:
    cols = st.columns(2)
    for i, (label, stocks, dom) in enumerate([("🇰🇷 국내", KOR, True), ("🇺🇸 해외", US, False)]):
        with cols[i]:
            st.header(label)
            for n, t in stocks: render_stock_card(n, t, dom, budget, rate)

with tab2:
    st.header("📊 심층 분석 대시보드")
    sel_stock = st.selectbox("분석할 종목 선택", [s[0] for s in KOR + US])
    # 선택된 종목에 대한 상세 정보 표시 로직
    target = next((s for s in KOR+US if s[0] == sel_stock), None)
    if target:
        data = get_full_analysis(target[1], ".KS" in target[1], budget, rate)
        c1, c2, c3 = st.columns(3)
        c1.metric("예상 고점", f"{data['high']:.2f}", "10~15일")
        c2.metric("예상 저점", f"{data['low']:.2f}", "2~4일")
        c3.metric("거래량 MA20", f"{data['ma20']:.2f}")
        st.line_chart(data['chart'])