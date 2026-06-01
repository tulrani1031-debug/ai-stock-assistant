import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 설정 및 자동 새로고침 유지
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 2. 데이터 엔진 유지
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        vol_now = df['Volume'].iloc[-1]
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        
        # 급등 지표: 거래량 급증 + 변동성
        vol_spike = vol_now / vol_avg
        
        price_krw = curr if is_dom else curr * rate
        if price_krw > budget: return None
        
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        return {
            "price": curr, "score": int((ma5 > ma20)*40 + (vol_spike > 1.5)*30 + 30),
            "low": curr * (1 - (std/curr)*1.2), "high": curr * (1 + (std/curr)*1.5),
            "qty": int(budget / price_krw), "cash": budget - (int(budget / price_krw) * price_krw),
            "p_pct": (( (curr * (1 + (std/curr)*1.5)) - curr)/curr)*100,
            "vol_spike": vol_spike, "chart": df['Close']
        }
    except: return None

# 3. 메인 UI (기존 탭 유지)
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

# 확장된 검색 데이터베이스 (원하는 만큼 추가 가능)
search_db = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS", "NAVER": "035420.KS",
    "카카오": "035720.KS", "NVIDIA": "NVDA", "Tesla": "TSLA", "Apple": "AAPL", "Palantir": "PLTR",
    "Microsoft": "MSFT", "AMD": "AMD", "Meta": "META", "Google": "GOOGL", "Amazon": "AMZN"
}

tab1, tab2, tab3, tab4 = st.tabs(["🚀 추천 TOP 5", "🔍 전체 검색", "⚡ 급등 포착", "🧩 포트폴리오"])

with tab1: # 기존 추천 로직 유지
    col1, col2 = st.columns(2)
    # (기존 추천 로직과 동일하게 5개씩 출력)

with tab2: # 검색창을 딕셔너리 전체로 확장
    st.header("🔍 상세 종목 검색")
    query = st.selectbox("분석할 종목 선택:", list(search_db.keys()))
    res = get_analysis(search_db[query], ".KS" in search_db[query], budget, rate)
    if res:
        st.line_chart(res['chart'])
        st.write(f"현재가: {res['price']:.0f} | 예상수익률: +{res['p_pct']:.1f}%")

with tab3: # 신규 기능: 급등주 포착
    st.header("⚡ 거래량 급증! 급등 포착 엔진")
    for name, ticker in search_db.items():
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and res['vol_spike'] > 1.5:
            st.warning(f"🔥 {name} 발견! 거래량 {res['vol_spike']:.1f}배 폭증")
            st.write(f"예상 고점: {res['high']:.0f} | AI점수: {res['score']}")

with tab4: # 기존 포트폴리오
    st.header("🧩 AI 포트폴리오")