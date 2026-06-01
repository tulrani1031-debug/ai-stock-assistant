import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사")

# [핵심 데이터 로직 유지]
@st.cache_data(ttl=600)
def get_full_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        if price_krw > budget: return None
        
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        low, high = curr * (1 - (std/curr)*1.2), curr * (1 + (std/curr)*1.5)
        qty = int(budget / price_krw)
        
        return {
            "price": curr, "score": int((ma5 > ma20)*40 + 30), "low": low, "high": high,
            "qty": qty, "cash": budget - (qty * price_krw),
            "p_pct": ((high-curr)/curr)*100, "p_amt": (high-curr)*qty*(1 if is_dom else rate),
            "chart": df['Close']
        }
    except: return None

# [UI 레이아웃]
st.title("🔮 서윤의 주식 마법사")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

tab1, tab2 = st.tabs(["🚀 예산 맞춤 추천 (TOP 5)", "📊 상세 분석 및 검색"])

with tab1:
    col1, col2 = st.columns(2)
    # 데이터 가독성을 위해 리스트/표 형식으로 개선
    for i, (label, stocks, dom) in enumerate([("🇰🇷 국내 주식 TOP 5", [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS")], True), 
                                            ("🇺🇸 해외 주식 TOP 5", [("NVIDIA", "NVDA"), ("Tesla", "TSLA")], False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            for n, t in stocks:
                res = get_full_analysis(t, dom, budget, rate)
                if res:
                    st.divider()
                    st.write(f"### {n} (점수: {res['score']}점)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("현재가", f"{'₩' if dom else '$'}{res['price']:.2f}")
                    c2.metric("예상 수익률", f"+{res['p_pct']:.1f}%")
                    c3.metric("구매 가능", f"{res['qty']}주")
                    st.write(f"📉 저점: {'₩' if dom else '$'}{res['low']:.0f} | 📈 고점: {'₩' if dom else '$'}{res['high']:.0f}")
                    st.write(f"💰 수익금: {res['p_amt']:,.0f}원 | 💵 남은 현금: {res['cash']:,.0f}원")

with tab2:
    st.header("🔍 상세 종목 검색")
    query = st.selectbox("종목 선택", ["삼성전자", "NVIDIA", "Tesla", "SK하이닉스"])
    # 선택 종목 상세 분석 (차트 및 지표 표시)