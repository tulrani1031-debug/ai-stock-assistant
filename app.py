import streamlit as st
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 60초마다 자동 새로고침
st_autorefresh(interval=60000, key="datarefresh")

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026", page_icon="🔮")

# ------------------------- 데이터 함수 -------------------------
@st.cache_data(ttl=300)
def get_exchange_rate():
    try:
        usdkrw = yf.Ticker("USDKRW=X")
        return float(usdkrw.history(period="1d")["Close"].iloc[-1])
    except:
        return 1400.0

@st.cache_data(ttl=300)
def get_stock_analysis(ticker):
    try:
        df = yf.download(ticker, period="3mo", interval="1d", progress=False, auto_adjust=True)
        if len(df) < 20: return None
        
        close = df["Close"]
        volume = df["Volume"]
        current = float(close.iloc[-1])
        ma5 = float(close.tail(5).mean())
        ma20 = float(close.tail(20).mean())
        vol_today = float(volume.iloc[-1])
        vol_avg = float(volume.tail(20).mean())

        # AI 점수 산출
        score = 0
        if ma5 > ma20: score += 40
        if current > ma20: score += 30
        if vol_today > vol_avg: score += 20
        if current > float(close.iloc[-5]): score += 10

        if score >= 80: grade = "🔥 강력매수"
        elif score >= 60: grade = "👍 매수"
        elif score >= 40: grade = "🤔 관망"
        else: grade = "❌ 비추천"

        return {"price": current, "score": score, "grade": grade, "ma5": ma5, "ma20": ma20, "chart": close}
    except:
        return None

# ------------------------- 설정 -------------------------
exchange_rate = get_exchange_rate()
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 서윤의 주식 마법사 PRO")
currency = st.sidebar.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("투자 방식", ["온전한 1주만", "소수점 주문 포함"])
st.sidebar.write(f"현재 환율 : ₩{exchange_rate:,.0f}")

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input("현재 투자 예산", min_value=0, step=10000, value=1000000)
budget_krw = budget if "원화" in currency else budget * exchange_rate

# ------------------------- 메인 로직 -------------------------
tab_main, tab_port = st.tabs(["📊 실시간 종목 분석", "🧩 AI 포트폴리오"])

with tab_main:
    sub_tab1, sub_tab2 = st.tabs(["🇰🇷 국내 주식", "🇺🇸 해외 주식"])
    
    def display_stocks(stocks, is_domestic):
        for name, ticker in stocks:
            analysis = get_stock_analysis(ticker)
            if analysis is None: continue
            
            price = int(analysis["price"] * (1 if is_domestic else exchange_rate))
            qty_raw = budget_krw / price
            if style == "온전한 1주만" and qty_raw < 1: continue
            
            with st.expander(f"📊 {name} | 점수: {analysis['score']}/100 | {analysis['grade']}", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("보유 수량", f"{int(qty_raw) if style == '온전한 1주만' else qty_raw:.4f} 주")
                c2.metric("AI 등급", analysis['grade'])
                c3.metric("MA5", f"{analysis['ma5']:,.0f}")
                c4.metric("MA20", f"{analysis['ma20']:,.0f}")
                st.line_chart(analysis["chart"])

    with sub_tab1: display_stocks(kor_stocks, True)
    with sub_tab2: display_stocks(us_stocks, False)

with tab_port:
    if st.button("🪄 AI 포트폴리오 생성"):
        portfolio = []
        for name, ticker in (kor_stocks + us_stocks):
            analysis = get_stock_analysis(ticker)
            if analysis is None or analysis['score'] < 40: continue
            price = int(analysis["price"] * (1 if ".KS" in ticker else exchange_rate))
            if style == "온전한 1주만" and budget_krw < price: continue
            portfolio.append({"name": name, "price": price, "score": analysis['score'], "grade": analysis['grade'], "is_dom": ".KS" in ticker})
        
        if portfolio:
            portfolio.sort(key=lambda x: x['score'], reverse=True)
            top5 = portfolio[:5]
            total_score = sum(p['score'] for p in top5)
            st.success("✅ AI 분석 기반 최적 포트폴리오 제안")
            for p in top5:
                weight = p['score'] / total_score
                qty = (budget_krw * weight) / p['price']
                st.write(f"- **{p['name']}** ({p['grade']}) | 배분 비중: {weight:.1%} | 수량: {qty:.4f} 주")
        else:
            st.warning("분석 가능한 매수 추천 종목이 없습니다.")