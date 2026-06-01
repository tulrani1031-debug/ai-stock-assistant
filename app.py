import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

# 1. 설정 및 자동 새로고침 (기존 유지)
st_autorefresh(interval=60000, key="refresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 2. 데이터 엔진
@st.cache_data(ttl=600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if df.empty or len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        if price_krw > budget: return None
        
        vol_spike = df['Volume'].iloc[-1] / df['Volume'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        high = curr * (1 + (std/curr)*1.5)
        low = curr * (1 - (std/curr)*1.2)
        
        return {
            "name": ticker, "price": curr, "vol_spike": vol_spike,
            "low": low, "high": high, "score": int(((df['Close'].rolling(5).mean().iloc[-1] > df['Close'].rolling(20).mean().iloc[-1])*40) + (vol_spike > 1.2)*30 + 30),
            "qty": int(budget / price_krw), "p_pct": ((high-curr)/curr)*100, 
            "p_amt": (high-curr)*int(budget / price_krw)*(1 if is_dom else rate)
        }
    except: return None

# 3. UI 구성
st.title("🔮 서윤의 주식 마법사 PRO")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

# 전체 주식 검색을 위한 입력창
st.sidebar.subheader("🔍 전체 종목 직접 검색")
search_query = st.sidebar.text_input("종목 티커 입력 (예: 005930.KS, AAPL):")

tab1, tab2, tab3, tab4 = st.tabs(["🚀 추천 TOP 5", "🔍 검색 분석", "⚡ 급등 포착", "🧩 포트폴리오"])

with tab1:
    col1, col2 = st.columns(2)
    # 기존 TOP 5 로직 유지
    for i, (label, pool, dom) in enumerate([("🇰🇷 국내 TOP 5", [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("카카오", "035720.KS"), ("NAVER", "035420.KS")], True), 
                                            ("🇺🇸 해외 TOP 5", [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("Palantir", "PLTR"), ("Microsoft", "MSFT")], False)]):
        with (col1 if i==0 else col2):
            st.subheader(label)
            recs = sorted([get_analysis(t, dom, budget, rate) for n, t in pool if get_analysis(t, dom, budget, rate)], key=lambda x: x['score'], reverse=True)[:5]
            for r in recs:
                # 텍스트가 겹치지 않게 박스형으로 정보 분리
                with st.expander(f"**{r['name']}** (AI 점수: {r['score']}점)", expanded=True):
                    st.write(f"💰 **현재가:** {'₩' if dom else '$'}{r['price']:.0f} | **수익률:** +{r['p_pct']:.1f}%")
                    st.write(f"📦 **구매가능:** {r['qty']}주 | **수익금:** {r['p_amt']:,.0f}원")
                    st.markdown("---") # 구분선 추가
                    st.write(f"📉 **저점:** {r['low']:,.0f} (2~4일 내)")
                    st.write(f"📈 **고점:** {r['high']:,.0f} (10~15일 내)")

with tab2:
    st.header("🔍 상세 검색 결과")
    if search_query:
        res = get_analysis(search_query, ".KS" in search_query, budget, rate)
        if res:
            st.success(f"{search_query} 분석 완료!")
            st.write(res) # 직접 검색 결과 표시
        else:
            st.error("종목을 찾을 수 없거나 예산을 초과했습니다.")

with tab3: # 기존 급등 포착 유지
    st.header("⚡ 지금 급등 중인 종목")