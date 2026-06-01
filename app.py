import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 v7.5")

# 1. 데이터 및 분석 엔진 (기존 기능 100% 유지)
@st.cache_data(ttl=600)
def get_full_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if len(df) < 20: return None
        
        curr = float(df['Close'].iloc[-1])
        price_krw = curr if is_dom else curr * rate
        
        # 예산 필터링 (한 주도 못 사는 종목 제외)
        if price_krw > budget: return None 
        
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + 30)
        low, high = curr * (1 - (std/curr)*1.2), curr * (1 + (std/curr)*1.5)
        qty = int(budget / price_krw)
        
        return {
            "name": ticker, "price": curr, "score": score, "low": low, "high": high,
            "qty": qty, "ma5": ma5, "ma20": ma20, "is_dom": is_dom,
            "p_pct": ((high-curr)/curr)*100, "p_amt": (high-curr)*qty*(1 if is_dom else rate),
            "cash": budget - (qty * price_krw), "chart": df['Close']
        }
    except: return None

# 2. 메인 UI 및 예산 설정
st.title("🔮 서윤의 주식 마법사 PRO v7.5")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380

# 종목 후보군 (전체 시장 대상 분석을 위해 확장)
KOR_LIST = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("LG에너지솔루션", "373220.KS"), ("기아", "000270.KS"), ("카카오", "035720.KS"), ("셀트리온", "068270.KS"), ("삼성바이오로직스", "207940.KS"), ("포스코퓨처엠", "003670.KS")]
US_LIST = [("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("Palantir", "PLTR"), ("Microsoft", "MSFT"), ("AMD", "AMD"), ("Meta", "META"), ("SoFi", "SOFI"), ("Amazon", "AMZN"), ("Google", "GOOGL")]

tab1, tab2 = st.tabs(["🚀 예산 맞춤 TOP 5 추천", "🔍 상세 분석 대시보드"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (label, stocks, dom) in enumerate([("🇰🇷 국내 TOP 5", KOR_LIST, True), ("🇺🇸 해외 TOP 5", US_LIST, False)]):
        with (col1 if i==0 else col2):
            st.header(label)
            recs = []
            for n, t in stocks:
                res = get_full_analysis(t, dom, budget, rate)
                if res: recs.append((n, res))
            
            # AI 점수순 정렬
            recs = sorted(recs, key=lambda x: x[1]['score'], reverse=True)[:5]
            
            for name, d in recs:
                with st.container(border=True):
                    st.subheader(f"{name} (AI 점수: {d['score']}점)")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("현재가", f"{'₩' if dom else '$'}{d['price']:.2f}")
                    c2.metric("예상 수익률", f"+{d['p_pct']:.1f}%")
                    c3.metric("구매 가능", f"{d['qty']}주")
                    st.write(f"📉 **예상 저점:** {'₩' if dom else '$'}{d['low']:.2f} (2~4일내) | 📈 **예상 고점:** {'₩' if dom else '$'}{d['high']:.2f} (10~15일내)")
                    st.write(f"💰 **예상 수익금:** {d['p_amt']:,.0f}원 | 💵 **남은 현금:** {d['cash']:,.0f}원")

with tab2:
    st.header("🔍 검색 및 상세 대시보드")
    all_stocks = {n: t for n, t in KOR_LIST + US_LIST}
    sel = st.selectbox("종목 선택", list(all_stocks.keys()))
    res = get_full_analysis(all_stocks[sel], ".KS" in all_stocks[sel], budget, rate)
    if res:
        st.line_chart(res['chart'])
        st.write(f"MA5: {res['ma5']:.2f} / MA20: {res['ma20']:.2f}")