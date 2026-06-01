import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 환경 설정 및 새로고침
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 2. 데이터 분석 함수 (예산 필터 오류 수정)
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        
        # 예산 필터 적용 (예산을 초과해도 일단 정보를 가져오되, 구매 수량이 0인 경우 처리)
        qty = int(budget / price_krw) if price_krw <= budget else 0
        
        vol_avg = df['Volume'].rolling(20).mean().iloc[-1]
        vol_ratio = df['Volume'].iloc[-1] / vol_avg
        std = df['Close'].rolling(20).std().iloc[-1]
        high = curr * (1 + (std/curr)*1.5)
        
        return {
            "name": ticker, "price": curr, "vol_ratio": vol_ratio,
            "low": curr * (1 - (std/curr)*1.2), "high": high,
            "qty": qty, "p_pct": (((curr * (1 + (std/curr)*1.5)) - curr)/curr)*100,
            "score": int((df['Close'].rolling(5).mean().iloc[-1] > df['Close'].rolling(20).mean().iloc[-1])*40 + 30)
        }
    except: return None

# 3. 메인 UI 및 추천 로직
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("카카오", "035720.KS"), ("NAVER", "035420.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("Palantir", "PLTR"), ("Microsoft", "MSFT")]

tab1, tab2, tab3, tab4 = st.tabs(["🚀 추천 TOP 5", "🔍 전체 검색", "⚡ 급등 예정 포착", "🧩 포트폴리오"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (label, pool, dom) in enumerate([("🇰🇷 국내 TOP 5", kor_stocks, True), ("🇺🇸 해외 TOP 5", us_stocks, False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            # 추천 리스트 출력 (로직 수정 완료)
            recs = [get_analysis(t, dom, budget, rate) for n, t in pool]
            # 예산 내 종목이 부족해도 데이터를 띄우도록 처리
            for r in [r for r in recs if r]:
                with st.expander(f"종목: {r['name']} (AI점수: {r['score']}점)", expanded=True):
                    st.write(f"현재가: {'₩' if dom else '$'}{r['price']:.0f} | 수익률: +{r['p_pct']:.1f}%")
                    st.write(f"구매 가능 수량: {r['qty']}주 | 예상 고점: {r['high']:.0f}")