import streamlit as st
import json
import urllib.request
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사", page_icon="🔮")

# 데이터 추출 엔진
def get_live_yahoo_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return 100.0

exchange_rate = get_live_yahoo_data("USDKRW=X")

st.sidebar.title("🤖 글로벌 AI 주식 비서")
menu = st.sidebar.radio("원하는 마법을 선택하세요:", ["🔮 실시간 AI 종목 추천 & 고점 추정", "📈 AI 타임머신 시뮬레이터"])

if menu == "🔮 실시간 AI 종목 추천 & 고점 추정":
    st.title("🔮 서윤의 주식 마법사 (수량 정밀 계산판)")
    
    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
        budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", min_value=1, value=100000 if '원화' in currency else 100, step=10)
    with col2:
        style = st.radio("투자 방식", ["온전한 1주만", "소수점 주문도 포함"])
        exclude_etf = st.checkbox("❌ ETF 제외하기")
    
    budget_krw = budget if "원화" in currency else int(budget * exchange_rate)

    if st.button("🧙‍♂️ 실시간 분석 및 수량 계산"):
        tab1, tab2 = st.tabs(["🇰🇷 국내 주식", "🇺🇸 미국 주식"])
        
        # 국내 주식 계산 로직
        with tab1:
            kor_pool = [
                {"ticker": "005930.KS", "name": "삼성전자", "news": "AI 반도체 공급 중심"},
                {"ticker": "000660.KS", "name": "SK하이닉스", "news": "AI 가속기 점유율 1위"}
            ]
            for s in kor_pool:
                price = int(get_live_yahoo_data(s["ticker"]))
                qty = budget_krw / price # 소수점 포함 계산
                
                with st.expander(f"{s['name']} (현재가: {price:,}원)", expanded=True):
                    st.write(f"📰 시황: {s['news']}")
                    col_a, col_b = st.columns(2)
                    col_a.metric("매수 가능 수량", f"{qty:.4f} 주")
                    if qty >= 1: col_b.success(f"✅ {int(qty)}주 매수 가능!")
                    else: col_b.info("🍂 소수점 주문으로 매수 가능")

        # 미국 주식 계산 로직
        with tab2:
            us_pool = ["NVDA", "PLTR", "TSLA", "AAPL", "SOFI"]
            for ticker in us_pool:
                price_usd = get_live_yahoo_data(ticker)
                price_krw = int(price_usd * exchange_rate)
                # 달러 기준 수량 계산
                budget_usd = budget if '$' in currency else budget / exchange_rate
                qty = budget_usd / price_usd
                
                with st.expander(f"{ticker} (현재가: ${price_usd:.2f})", expanded=True):
                    st.write(f"원화 환산가: {price_krw:,}원")
                    col_a, col_b = st.columns(2)
                    col_a.metric("매수 가능 수량", f"{qty:.4f} 주")
                    if qty >= 1: col_b.success(f"✅ {int(qty)}주 매수 가능!")
                    else: col_b.info("🍂 소수점 주문으로 매수 가능")

elif menu == "📈 AI 타임머신 시뮬레이터":
    st.title("📈 AI 타임머신 시뮬레이터")
    if st.button("🏁 시뮬레이션 가동"):
        st.line_chart(pd.DataFrame(np.random.randn(50, 2).cumsum(axis=0), columns=['투자 수익', '시장 지수']))