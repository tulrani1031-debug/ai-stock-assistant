import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v7.1")

# [데이터 분석 엔진 - 유지]
@st.cache_data(ttl=600)
def get_full_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty: return None
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        low, high = curr * (1 - (std/curr)*1.2), curr * (1 + (std/curr)*1.5)
        qty = int(budget / (curr if is_dom else curr * rate))
        
        return {
            "price": curr, "score": int((ma5 > ma20)*40 + 30),
            "low": low, "high": high, "qty": qty, "ma5": ma5, "ma20": ma20,
            "cash": budget - (qty * (curr if is_dom else curr * rate)),
            "chart": df['Close'], "vol": df['Volume'].iloc[-1],
            "p_pct": ((high-curr)/curr)*100, "p_amt": (high-curr)*qty
        }
    except: return None

# [카드 렌더링 함수 - 유지]
def render_stock_card(name, ticker, is_dom, budget, rate):
    res = get_full_analysis(ticker, is_dom, budget, rate)
    if not res: return None
    with st.container(border=True):
        st.write(f"### {name}")
        c1, c2, c3 = st.columns(3)
        c1.metric("현재가", f"{res['price']:.2f}")
        c2.metric("AI 점수", f"{res['score']}점")
        c3.metric("예상 수익률", f"{res['p_pct']:.1f}%")
        st.write(f"구매 가능: {res['qty']}주 | 남은 현금: {res['cash']:,}원")
    return res

# [메인 로직 - 유지]
st.title("🔮 서윤의 주식 마법사 PRO v7.1")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

tab1, tab2 = st.tabs(["🚀 AI TOP 5 추천", "🔍 종목 상세 검색"])

with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🇰🇷 국내 TOP 5")
        kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS")]
        for n, t in kor_stocks: render_stock_card(n, t, True, budget, rate)
    with col2:
        st.subheader("🇺🇸 해외 TOP 5")
        us_stocks = [("NVIDIA", "NVDA"), ("Tesla", "TSLA")]
        for n, t in us_stocks: render_stock_card(n, t, False, budget, rate)

with tab2:
    st.subheader("🔍 종목 상세 분석")
    search_db = {"삼성전자": "005930.KS", "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL"}
    query = st.selectbox("분석할 종목을 선택하세요:", list(search_db.keys()))
    if query:
        data = render_stock_card(query, search_db[query], ".KS" in search_db[query], budget, rate)
        if data:
            st.line_chart(data['chart'])
            st.write(f"예상 고점: {data['high']:.2f} | 예상 저점: {data['low']:.2f}")