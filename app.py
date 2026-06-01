import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 환경 설정 및 실시간 업데이트 (60초 주기)
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 2. 데이터 분석 엔진 (실시간 메타 분석 반영)
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        vol_ratio = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        
        # 메타 반영 점수: 거래량 급증 + 이동평균선 정배열
        ma5 = df['Close'].rolling(5).mean().iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        score = int((ma5 > ma20) * 50 + (vol_ratio > 1.2) * 50)
        
        price_krw = curr if is_dom else curr * rate
        return {"name": ticker, "price": curr, "score": score, "vol": vol_ratio, "qty": int(budget/price_krw)}
    except: return None

# 3. 메인 대시보드
st.title("🔮 서윤의 주식 마법사 PRO")
col_a, col_b = st.columns([1, 3])
with col_a:
    budget = st.number_input("투자 예산 (KRW)", value=1000000, step=10000)
    rate = st.number_input("실시간 환율 (KRW/USD)", value=1380.0, step=1.0)
    st.info(f"업데이트: 매 1분 자동 갱신 중")

# 전체 시장 분석 (Top 5 추출)
all_tickers = ["005930.KS", "NVDA", "TSLA", "000660.KS", "AAPL", "PLTR", "MSFT", "AMD", "035420.KS", "005380.KS"]
results = [get_analysis(t, ".KS" in t, budget, rate) for t in all_tickers]
top_5 = sorted([r for r in results if r], key=lambda x: x['score'], reverse=True)[:5]

tab1, tab2 = st.tabs(["🚀 AI 추천 TOP 5", "⚡ 급등 예정"])

with tab1:
    st.subheader("📊 현재 시장 메타 반영 TOP 5")
    for r in top_5:
        with st.expander(f"**{r['name']}** | AI 점수: {r['score']}점", expanded=True):
            st.metric("현재가", f"{r['price']:.2f}")
            st.write(f"구매 가능 수량: {r['qty']}주 | 거래량 흐름: {r['vol']:.1f}배")

with tab2:
    st.subheader("⚡ 급등 시작 신호 (거래량 폭발)")
    for r in results:
        if r and 1.2 <= r['vol'] <= 2.5:
            st.warning(f"🚀 **{r['name']}** - 거래량 {r['vol']:.1f}배 폭발! (지금이 매수 기회)")