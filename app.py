import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 자동 새로고침 설정
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 데이터 분석 함수 (예산 기반 필터링 로직 수정)
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        
        # 예산보다 가격이 높으면 분석 대상에서 제외
        if price_krw > budget: return None
        
        vol_spike = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        return {
            "name": ticker, "price": curr, "vol_spike": vol_spike,
            "low": curr * (1 - (std/curr)*1.2), "high": curr * (1 + (std/curr)*1.5),
            "score": int((ma5 > ma20)*40 + (vol_spike > 1.2)*30 + 30),
            "qty": int(budget / price_krw), "p_pct": (((curr * (1 + (std/curr)*1.5)) - curr)/curr)*100
        }
    except: return None

# UI 구성
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380
search_db = {"삼성전자": "005930.KS", "NVIDIA": "NVDA", "Tesla": "TSLA", "SK하이닉스": "000660.KS", "Palantir": "PLTR", "현대차": "005380.KS", "Apple": "AAPL", "AMD": "AMD", "Microsoft": "MSFT", "카카오": "035720.KS"}

tab1, tab2, tab3, tab4 = st.tabs(["🚀 추천 TOP 5", "🔍 전체 검색", "⚡ 급등 포착", "🧩 포트폴리오"])

with tab1:
    col1, col2 = st.columns(2)
    # 예산 필터링이 완료된 리스트만 추출하여 5개씩 출력
    for i, (label, pool, dom) in enumerate([("🇰🇷 국내 TOP 5", [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("카카오", "035720.KS"), ("NAVER", "035420.KS")], True), 
                                            ("🇺🇸 해외 TOP 5", [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("Palantir", "PLTR"), ("Microsoft", "MSFT")], False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            # 예산 내 종목만 분석
            recs = [get_analysis(t, dom, budget, rate) for n, t in pool]
            valid_recs = sorted([r for r in recs if r], key=lambda x: x['score'], reverse=True)[:5]
            
            for r in valid_recs:
                st.divider()
                st.write(f"### {r['name']} (점수: {r['score']}점)")
                st.write(f"현재가: {'₩' if dom else '$'}{r['price']:.0f} | 수익률: +{r['p_pct']:.1f}%")
                st.write(f"구매 가능: {r['qty']}주 | 목표가: {r['high']:.0f}")

with tab3: # 급등주 탭
    st.header("⚡ 지금 급등 중인 종목")
    for name, ticker in search_db.items():
        res = get_analysis(ticker, ".KS" in ticker, budget, rate)
        if res and res['vol_spike'] > 1.2:
            st.warning(f"🔥 {name} (거래량 {res['vol_spike']:.1f}배)")
            st.write(f"매수 시점: 분할 매수 | 목표가: {res['high']:.0f} | 예상 도달: 10~15일")

# 기존 검색/포트폴리오 유지...