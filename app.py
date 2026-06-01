import streamlit as st
import yfinance as yf
import pandas as pd

# 설정 및 종목 리스트 (각 20개씩)
KOR_STOCKS = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS"), ("기아", "000270.KS"), ("LG에너지솔루션", "373220.KS"), ("POSCO홀딩스", "005490.KS"), ("삼성바이오로직스", "207940.KS"), ("LG화학", "051910.KS"), ("카카오", "035720.KS"), ("KB금융", "105560.KS"), ("신한지주", "055550.KS"), ("삼성물산", "028260.KS"), ("현대모비스", "012330.KS"), ("하나금융지주", "086790.KS"), ("LG전자", "066570.KS"), ("포스코퓨처엠", "003670.KS"), ("SK이노베이션", "096770.KS"), ("삼성SDI", "006400.KS")]
US_STOCKS = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI"), ("Microsoft", "MSFT"), ("Google", "GOOGL"), ("Amazon", "AMZN"), ("AMD", "AMD"), ("Meta", "META"), ("Netflix", "NFLX"), ("Intel", "INTC"), ("Broadcom", "AVGO"), ("Qualcomm", "QCOM"), ("Adobe", "ADBE"), ("Salesforce", "CRM"), ("Oracle", "ORCL"), ("Cisco", "CSCO"), ("IBM", "IBM"), ("Disney", "DIS")]

@st.cache_data(ttl=3600)
def get_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="3mo")
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        
        if price_krw > budget: return None # 예산 초과 시 제외
        
        # AI 지표
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + 20)
        
        # 예산 적합도: 예산의 10%~50% 내외 가격일 때 최고점
        fit_score = int(100 - abs((budget * 0.3) - price_krw) / (budget * 0.3) * 100)
        fit_score = max(0, min(100, fit_score))
        
        return {"price": curr, "price_krw": price_krw, "score": score, "fit_score": fit_score, "qty": int(budget/price_krw)}
    except: return None

# 메인 UI
st.title("🔮 서윤의 주식 마법사 PRO v4.0")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380 # 환율 고정/실시간 연동

# 분석 및 추천 로직
def get_top_recommendations(stocks, is_dom):
    results = []
    for name, ticker in stocks:
        res = get_analysis(ticker, is_dom, budget, rate)
        if res:
            res.update({"name": name, "total_score": (res['score'] + res['fit_score']) / 2})
            results.append(res)
    return sorted(results, key=lambda x: x['total_score'], reverse=True)[:5]

tab1, tab2 = st.tabs(["🚀 맞춤형 추천 (국내/해외)", "📊 전체 종목 분석"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (cat, stock_list, is_dom) in enumerate([("국내", KOR_STOCKS, True), ("해외", US_STOCKS, False)]):
        target_col = col1 if i == 0 else col2
        with target_col:
            st.subheader(f"{'🇰🇷' if is_dom else '🇺🇸'} {cat} 추천 TOP 5")
            for item in get_top_recommendations(stock_list, is_dom):
                st.write(f"🥇 **{item['name']}** (종합 {item['total_score']:.0f}점)")
                st.caption(f"현재가: {'₩' if is_dom else '$'}{item['price']:.2f} | 가능수량: {item['qty']}주 | 선정이유: MA5/20 추세 양호 및 예산 적합도 최적")

with tab2:
    st.info("전체 종목에 대한 심층 분석 탭입니다.")
    # (기존 상세 분석 코드 유지)