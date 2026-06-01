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
with tab2: # 🔍 상세 검색 (전체 주식 검색 가능)
    st.header("🔍 상세 종목 검색")
    st.write("분석을 원하는 종목의 티커(예: 005930.KS, AAPL)를 입력하세요.")
    
    search_q = st.text_input("종목 티커 입력:", key="search_input")
    
    if search_q:
        # 입력한 티커로 즉시 분석 실행
        res = get_analysis(search_q, ".KS" in search_q, budget, 1380)
        
        if res:
            with st.expander(f"📊 {search_q} 분석 결과", expanded=True):
                st.write(f"- **현재가:** {res['price']:.0f}원")
                st.write(f"- **예상 저점:** {res['low']:.0f}원")
                st.write(f"- **예상 고점:** {res['high']:.0f}원")
                st.write(f"- **구매 가능 수량:** {res['qty']}주")
                st.write(f"- **상승 여력:** +{res['p_pct']:.1f}%")
        else:
            st.error("해당 종목을 찾을 수 없거나 예산을 초과했습니다. 티커를 확인해주세요.")

with tab3: # [급등 예정 포착] 탭 전용 수정
    st.header("⚡ 지금 막 급등 시작하는 종목 (거래량 폭발 구간)")
    for name, ticker in full_db.items():
        res = get_analysis(ticker, ".KS" in ticker, budget, 1380)
        
        # 조건: 1.2배 이상 ~ 2.5배 이하 (이미 너무 터진 3배 이상 제외)
        if res and 1.2 <= res['vol_ratio'] <= 2.5:
            with st.expander(f"🚀 {name} - 급등 확률 높음 (현재 거래량 평소의 {res['vol_ratio']:.1f}배)", expanded=True):
                st.write(f"- **현재가:** {res['price']:.0f}원")
                st.write(f"- **예상 고점:** {res['high']:.0f}원")
                st.write("- **상승 이유:** 거래량이 평소보다 강하게 유입되며 변동성이 확대되는 매수 시그널 발생")
                st.write("- **매수 전략:** 현재 가격에서 분할 매수 진행 후, 고점 돌파 시 비중 확대 권장")
with tab4: # 🧩 AI 포트폴리오
    st.header("🧩 AI 포트폴리오 최적 배분")
    st.write("투자 예산 내에서 관리 중인 종목들의 배분 상태입니다.")
    
    # 포트폴리오에 담긴 종목들을 자동으로 추적하여 표시
    portfolio_stocks = [("삼성전자", "005930.KS"), ("NVIDIA", "NVDA")] # 추적할 종목 목록
    
    for name, ticker in portfolio_stocks:
        res = get_analysis(ticker, ".KS" in ticker, budget, 1380)
        if res and res['qty'] > 0:
            with st.expander(f"📦 {name} 비중 관리", expanded=True):
                total_invested = res['price'] * res['qty']
                st.write(f"- **보유 수량:** {res['qty']}주")
                st.write(f"- **총 투자 금액:** {total_invested:,.0f}원")
                st.write(f"- **전체 예산 대비 비중:** {(total_invested / budget) * 100:.1f}%")
        else:
            st.write(f"- {name}: 예산 부족으로 현재 미보유")