import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 환경 설정
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사")

# 2. 데이터 엔진 유지
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        if price_krw > budget: return None
        
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        return {
            "price": curr, "score": int((ma5 > ma20)*40 + 30),
            "low": curr * (1 - (std/curr)*1.2), "high": curr * (1 + (std/curr)*1.5),
            "qty": int(budget / price_krw), "cash": budget - (int(budget / price_krw) * price_krw),
            "p_pct": (( (curr * (1 + (std/curr)*1.5)) - curr)/curr)*100, 
            "p_amt": (curr * (1 + (std/curr)*1.5) - curr) * int(budget / price_krw) * (1 if is_dom else rate)
        }
    except: return None

# 3. 메인 UI (가독성 개선 버전)
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

tab1, tab2, tab3 = st.tabs(["🚀 추천 TOP 5", "🔍 상세 검색", "🧩 AI 포트폴리오"])

KOR = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
US = [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("Palantir", "PLTR"), ("Microsoft", "MSFT")]

with tab1:
    col1, col2 = st.columns(2)
    for i, (label, pool, dom) in enumerate([("🇰🇷 국내 TOP 5", KOR, True), ("🇺🇸 해외 TOP 5", US, False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            recs = []
            for n, t in pool:
                res = get_analysis(t, dom, budget, rate)
                if res: recs.append((n, res))
            
            for name, d in sorted(recs, key=lambda x: x[1]['score'], reverse=True)[:5]:
                # 줄바꿈을 적용하여 텍스트 깨짐 방지
                with st.expander(f"{name} (AI {d['score']}점)", expanded=True):
                    st.write(f"현재가: {'₩' if dom else '$'}{d['price']:.0f}")
                    st.write(f"예상 수익: +{d['p_pct']:.1f}% ({d['p_amt']:,.0f}원)")
                    st.write(f"구매 가능 수량: {d['qty']}주 (남은 현금: {d['cash']:,.0f}원)")
                    st.write(f"📉 예상 저점: {d['low']:,.0f} (2~4일 내)")
                    st.write(f"📈 예상 고점: {d['high']:,.0f} (10~15일 내)")

with tab2:
    st.header("🔍 상세 종목 검색")
    all_stocks = {n: t for n, t in KOR + US}
    query = st.selectbox("분석할 종목 선택:", list(all_stocks.keys()))
    res = get_analysis(all_stocks[query], ".KS" in all_stocks[query], budget, rate)
    if res:
        st.write(f"### {query} 상세 정보")
        st.write(f"현재가: {res['price']:.0f} | AI점수: {res['score']}")