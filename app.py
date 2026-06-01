import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 설정 및 데이터 엔진
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 모든 탭에서 사용할 공통 데이터베이스
full_db = {
    "삼성전자": "005930.KS", "SK하이닉스": "000660.KS", "현대차": "005380.KS", 
    "카카오": "035720.KS", "NAVER": "035420.KS", "NVIDIA": "NVDA", 
    "Tesla": "TSLA", "Apple": "AAPL", "Palantir": "PLTR", "Microsoft": "MSFT"
}

@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / vol_avg
        std = df['Close'].rolling(20).std().iloc[-1]
        
        price_krw = curr if is_dom else curr * rate
        high = curr * (1 + (std/curr)*1.5)
        low = curr * (1 - (std/curr)*1.2)
        qty = int(budget / price_krw) if price_krw <= budget else 0
        
        return {
            "name": ticker, "price": curr, "vol_ratio": vol_ratio,
            "low": low, "high": high, "qty": qty,
            "p_pct": ((high-curr)/curr)*100, "score": int(vol_ratio * 20)
        }
    except: return None

# 2. 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

tab1, tab2, tab3, tab4 = st.tabs(["🚀 추천 TOP 5", "🔍 상세 검색", "⚡ 급등 예정", "🧩 포트폴리오"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (label, pool, dom) in enumerate([("🇰🇷 국내 TOP 5", [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS")], True), 
                                            ("🇺🇸 해외 TOP 5", [("NVIDIA", "NVDA"), ("Tesla", "TSLA")], False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            for name, ticker in pool:
                res = get_analysis(ticker, dom, budget, rate)
                if res:
                    with st.expander(f"{name} (점수: {res['score']}점)", expanded=True):
                        st.write(f"현재가: {res['price']:.0f} | 수익률: +{res['p_pct']:.1f}% | 구매: {res['qty']}주")

with tab2:
    st.header("🔍 전체 종목 검색")
    search_q = st.text_input("티커 입력 (예: 005930.KS, AAPL):")
    if search_q:
        res = get_analysis(search_q, ".KS" in search_q, budget, rate)
        if res:
            with st.expander(f"📊 {search_q} 분석 결과", expanded=True):
                st.write(f"현재가: {res['price']:.0f}원 | 예상 고점: {res['high']:.0f}원")
        else: st.error("종목을 찾을 수 없습니다.")

with tab3:
    st.header("⚡ 지금 막 급등 시작하는 종목")
    for name, ticker in full_db.items():
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and 1.2 <= res['vol_ratio'] <= 2.5:
            with st.expander(f"🚀 {name} (거래량 {res['vol_ratio']:.1f}배)", expanded=True):
                st.write(f"현재가: {res['price']:.0f} | 예상 고점: {res['high']:.0f}")
                st.write("상승 이유: 대량 거래 유입 및 변동성 확대 시작 단계")

with tab4:
    st.header("🧩 AI 포트폴리오")
    for name, ticker in full_db.items():
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and res['qty'] > 0:
            with st.expander(f"📦 {name} 비중", expanded=True):
                st.write(f"보유수량: {res['qty']}주 | 예산 점유: {(res['price']*res['qty']/budget)*100:.1f}%")