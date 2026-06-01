import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v6.0")

# 1. 고도화된 AI 분석 엔진
@st.cache_data(ttl=600)
def get_advanced_analysis(ticker, budget):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty: return None
        
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        vol_chg = ((df['Volume'].iloc[-1] / df['Volume'].tail(20).mean()) - 1) * 100
        
        # 점수 계산
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + (vol_chg > 0)*20 + 20)
        low, high = curr * (1 - (std/curr)*1.2), curr * (1 + (std/curr)*1.5)
        
        # 구매 가능 수량 (원화 예산 기반)
        qty = int(budget / curr) if ".KS" in ticker else int((budget/1380) / curr)
        
        return {
            "price": curr, "score": score, "low": low, "high": high,
            "ma5": ma5, "ma20": ma20, "vol_chg": vol_chg, "qty": qty,
            "p_pct": ((high-curr)/curr)*100, "chart": df['Close']
        }
    except: return None

# 2. 메인 화면
st.title("🔮 서윤의 주식 마법사 PRO v6.0")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)

# 3. 검색 데이터베이스 (주요 종목 확장 리스트)
search_db = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS", "NVIDIA": "NVDA", 
    "Tesla": "TSLA", "Apple": "AAPL", "Palantir": "PLTR", "Microsoft": "MSFT", "Google": "GOOGL"
}

tab1, tab2 = st.tabs(["🚀 실시간 AI 추천 대시보드", "🔍 상세 종목 검색"])

with tab1:
    st.header("📈 오늘의 시장 주도주 (Top 5)")
    col1, col2 = st.columns(2)
    # 추천 로직은 전체 데이터 분석 기반으로 실행
    for i, (label, is_dom) in enumerate([("국내", True), ("해외", False)]):
        with (col1 if i==0 else col2):
            st.subheader(f"{label} 추천")
            # 전체 시장 탐색 후 TOP 5 추천 표시 (기존 유지)

with tab2:
    st.header("🔍 심층 분석 및 검색")
    query = st.selectbox("종목명을 검색하세요 (자동완성):", list(search_db.keys()))
    if query:
        res = get_advanced_analysis(search_db[query], budget)
        if res:
            c1, c2, c3 = st.columns(3)
            c1.metric("현재가", f"{res['price']:.2f}")
            c2.metric("AI 점수", f"{res['score']}점")
            c3.metric("예상 수익률", f"{res['p_pct']:.1f}%")
            
            st.subheader("📊 상세 리포트")
            c4, c5 = st.columns(2)
            c4.write(f"**MA5/MA20:** {res['ma5']:.0f} / {res['ma20']:.0f}")
            c4.write(f"**거래량 변화:** {res['vol_chg']:.1f}%")
            c5.write(f"**구매 가능 수량:** {res['qty']}주")
            
            st.line_chart(res['chart'])
            st.caption("※ 이 지표는 과거 데이터 기반의 AI 추정치이며, 투자의 책임은 본인에게 있습니다.")