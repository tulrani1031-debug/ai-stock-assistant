import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh
import requests

# 1. 환경 설정
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 실시간 환율 가져오기 (무료 API)
def get_realtime_rate():
    try:
        url = "https://api.exchangerate-api.com/v4/latest/USD"
        return requests.get(url).json()['rates']['KRW']
    except: return 1380.0

# 2. 데이터 분석 엔진
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        
        # 메타 분석 점수
        score = int((df['Close'].iloc[-1] > df['Close'].rolling(20).mean().iloc[-1]) * 50 + (vol_ratio > 1.2) * 50)
        
        price_krw = curr if is_dom else curr * rate
        return {"price": curr, "score": score, "vol": vol_ratio, "qty": int(budget/price_krw)}
    except: return None

# 3. 메인 대시보드
st.title("🔮 서윤의 주식 마법사 PRO")
rate = get_realtime_rate()
st.sidebar.metric("실시간 환율 (USD/KRW)", f"{rate:,.2f}원")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)

# 국내/해외 종목 리스트 (한글 명칭 매핑)
kor_list = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("네이버", "035420.KS"), ("카카오", "035720.KS")]
usa_list = [("엔비디아", "NVDA"), ("테슬라", "TSLA"), ("애플", "AAPL"), ("팔란티어", "PLTR"), ("마이크로소프트", "MSFT")]

tab1, tab2 = st.tabs(["🚀 추천 종목 (국내/해외 분리)", "⚡ 급등 예정"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (col, title, stocks, dom) in enumerate([(col1, "🇰🇷 국내 TOP 5", kor_list, True), (col2, "🇺🇸 해외 TOP 5", usa_list, False)]):
        with col:
            st.subheader(title)
            for name, ticker in stocks:
                res = get_analysis(ticker, dom, budget, rate)
                if res:
                    st.write(f"### {name}")
                    st.metric("현재가", f"{res['price']:.2f}")
                    st.write(f"AI 점수: {res['score']}점 | 구매가능: {res['qty']}주")
                    st.divider()

with tab2:
    st.header("⚡ 급등 신호 포착 (거래량 폭발)")
    for name, ticker in (kor_list + usa_list):
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and 1.2 <= res['vol'] <= 3.0:
            st.warning(f"🚀 **{name}** - 거래량 평소의 {res['vol']:.1f}배! (매수 메타 확인)")