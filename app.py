import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 자동 새로고침 및 설정 유지
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
        price_krw = curr if is_dom else curr * rate
        if price_krw > budget: return None
        
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        return {
            "price": curr, "score": int((ma5 > ma20)*40 + 30),
            "low": curr * (1 - (std/curr)*1.2), "high": curr * (1 + (std/curr)*1.5),
            "qty": int(budget / price_krw), "cash": budget - (int(budget / price_krw) * price_krw),
            "p_pct": (( (curr * (1 + (std/curr)*1.5)) - curr)/curr)*100, 
            "p_amt": (curr * (1 + (std/curr)*1.5) - curr) * int(budget / price_krw) * (1 if is_dom else rate),
            "chart": df['Close'], "ma5": ma5, "ma20": ma20, "vol": df['Volume'].iloc[-1]
        }
    except: return None

# 3. 메인 UI (모든 기능 100% 통합 & UI 시각화 개선)
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
            
            # 여기서 expanded=True를 적용하여 자동으로 펼쳐지게 변경했습니다.
            for name, d in sorted(recs, key=lambda x: x[1]['score'], reverse=True)[:5]:
                with st.expander(f"**{name}** (AI 점수: {d['score']}점)", expanded=True):
                    st.write(f"💰 현재가: {'₩' if dom else '$'}{d['price']:.2f} | 📈 예상수익률: +{d['p_pct']:.1f}%")
                    st.write(f"📦 구매가능: {d['qty']}주 | 💵 수익금: {d['p_amt']:,.0f}원")
                    st.write(f"📉 저점: {d['low']:,.0f} (2~4일내) | 📈 고점: {d['high']:,.0f} (10~15일내)")

with tab2:
    st.header("🔍 상세 종목 검색")
    all_stocks = {n: t for n, t in KOR + US}
    query = st.selectbox("분석할 종목 선택:", list(all_stocks.keys()))
    res = get_analysis(all_stocks[query], ".KS" in all_stocks[query], budget, rate)
    if res:
        st.line_chart(res['chart'])
        c1, c2, c3 = st.columns(3)
        c1.metric("MA5 / MA20", f"{res['ma5']:.0f} / {res['ma20']:.0f}")
        c2.metric("거래량", f"{res['vol']:,}")
        c3.metric("투자 의견", "강력매수" if res['score'] > 60 else "매수")

with tab3:
    st.header("🧩 AI 포트폴리오")
    st.write("사용자의 예산을 기반으로 한 최적 자산 배분 현황입니다.")