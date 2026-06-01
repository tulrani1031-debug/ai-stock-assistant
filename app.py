import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO")

# 1. AI 데이터 분석 함수 (yfinance 기반)
@st.cache_data(ttl=600)
def analyze_stock(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        df = t.history(period="6mo")
        if df.empty: return None
        
        curr = float(df['Close'].iloc[-1])
        ma5 = float(df['Close'].rolling(5).mean().iloc[-1])
        ma20 = float(df['Close'].rolling(20).mean().iloc[-1])
        vol = df['Volume'].iloc[-1]
        vol_avg = float(df['Volume'].rolling(20).mean().iloc[-1])
        
        # AI 점수 로직
        score = 0
        if ma5 > ma20: score += 30
        if curr > ma20: score += 30
        if vol > vol_avg: score += 20
        if curr > float(df['Close'].iloc[-10]): score += 20
        
        # 고점/저점 추정 (변동성 기반)
        std = float(df['Close'].tail(20).std())
        low_target = curr * (1 - (std / curr) * 1.5)
        high_target = curr * (1 + (std / curr) * 1.5)
        
        grade = "🔥 강력매수" if score >= 80 else "👍 매수" if score >= 60 else "🤔 관망" if score >= 40 else "❌ 비추천"
        
        return {
            "price": curr, "score": score, "grade": grade, "ma5": ma5, "ma20": ma20,
            "low": low_target, "high": high_target, "chart": df['Close']
        }
    except: return None

# 2. 데이터 준비
stocks = {"국내": [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")],
          "해외": [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]}

# 3. 사이드바 및 예산 입력
st.sidebar.title("🤖 주식 마법사 설정")
budget = st.sidebar.number_input("투자 예산 (원)", value=1000000, step=10000)

# 4. 분석 수행
all_data = {}
for cat, items in stocks.items():
    for name, ticker in items:
        res = analyze_stock(ticker)
        if res: all_data[name] = {**res, "ticker": ticker, "cat": cat}

# 5. 메인 화면: BEST PICK
st.title("🔮 서윤의 주식 마법사 PRO")
best_name = max(all_data, key=lambda x: all_data[x]['score'])
best = all_data[best_name]

st.subheader("👑 오늘의 BEST PICK")
col_b1, col_b2 = st.columns([1, 2])
with col_b1:
    st.metric(best_name, f"{best['price']:,.0f}원", f"{best['score']}점")
    st.write(f"투자의견: {best['grade']}")
with col_b2:
    st.write("추천 이유: 거래량 기반 상승 추세 유지 및 MA5 > MA20 골든크로스 근접.")

st.divider()

# 6. 탭 구성
tab1, tab2 = st.tabs(["📊 실시간 종목 분석", "🧩 AI 포트폴리오"])

with tab1:
    cat_tabs = st.tabs(["🇰🇷 국내 주식 TOP 5", "🇺🇸 해외 주식 TOP 5"])
    for i, cat in enumerate(["국내", "해외"]):
        with cat_tabs[i]:
            sorted_stocks = sorted([k for k, v in all_data.items() if v['cat'] == cat], 
                                  key=lambda x: all_data[x]['score'], reverse=True)
            for idx, name in enumerate(sorted_stocks[:5]):
                d = all_data[name]
                with st.expander(f"{idx+1}위 {name} - AI {d['score']}점 ({d['grade']})"):
                    c1, c2, c3, c4 = st.columns(4)
                    c1.metric("현재가", f"{d['price']:,.0f}원")
                    c2.metric("매수 타이밍", "🟢 적합" if d['score'] > 60 else "🟡 분할권장")
                    
                    # 수량 및 수익 분석
                    qty = int(budget * (d['score']/500) / d['price']) # 가중치 부여
                    c3.metric("구매 가능 수량", f"{qty}주")
                    c4.metric("예상 수익률", f"+{((d['high']-d['price'])/d['price']*100):.1f}%")
                    
                    st.line_chart(d['chart'])
                    st.caption("※ 본 분석은 이동평균선과 변동성을 기반으로 한 AI 추정치입니다.")

with tab2:
    st.subheader("💰 AI 자동 배분 포트폴리오")
    total_score = sum(d['score'] for d in all_data.values())
    for name, d in all_data.items():
        weight = d['score'] / total_score
        st.write(f"- **{name}**: 비중 {weight:.1%} (투자금 {int(budget*weight):,}원)")