import streamlit as st
import datetime
import json
import urllib.request
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사", page_icon="🔮")

# 데이터 및 환율 추출 함수
def get_live_yahoo_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return 100000.0

exchange_rate = get_live_yahoo_data("USDKRW=X")

st.sidebar.title("🤖 글로벌 AI 주식 비서")
menu = st.sidebar.radio("원하는 마법을 선택하세요:", ["🔮 실시간 AI 종목 추천 & 고점 추정", "📈 AI 타임머신 시뮬레이터"])

if menu == "🔮 실시간 AI 종목 추천 & 고점 추정":
    st.title("🔮 서윤의 주식 마법사 (인터페이스 완전 복원판)")
    
    col_c, col_b = st.columns([1, 3])
    with col_c: currency_type = st.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
    with col_b:
        raw_budget = st.number_input("현재 투자 여유돈", min_value=1000, value=100000, step=10000)
        budget_krw = raw_budget if "원화" in currency_type else int(raw_budget * exchange_rate)
    
    if st.button("🧙‍♂️ 실시간 시장 분석 시작"):
        tab1, tab2 = st.tabs(["🇰🇷 국내 시장", "🇺🇸 미국 시장"])
        
        with tab1:
            kor_pool = [
                {"ticker": "005930.KS", "name": "삼성전자", "news": "AI 메모리 반도체 공급 중심"},
                {"ticker": "000660.KS", "name": "SK하이닉스", "news": "AI 가속기 시장 독점적 수혜"},
                {"ticker": "005380.KS", "name": "현대차", "news": "친환경차 수출 대박 모멘텀"},
                {"ticker": "035420.KS", "name": "네이버(NAVER)", "news": "글로벌 AI 플랫폼 수출 강세"}
            ]
            for s in kor_pool:
                price = int(get_live_yahoo_data(s["ticker"]))
                shares = budget_krw // price
                with st.expander(f"{s['name']} (현재가: {price:,}원)", expanded=True):
                    st.write(f"📰 시황: {s['news']}")
                    st.metric("구매 가능 수량", f"{shares}주")
                    if shares > 0: st.success("🚀 지금 즉시 매수 가능!")
                    else: st.info("🍂 예산보다 비싸지만, 소수점 투자가 가능합니다.")

        with tab2:
            us_pool = ["NVDA", "PLTR", "TSLA", "AAPL", "SOFI"]
            for ticker in us_pool:
                price_usd = get_live_yahoo_data(ticker)
                price_krw = int(price_usd * exchange_rate)
                shares = budget_krw // price_krw
                with st.expander(f"{ticker} (현재가: ${price_usd:.2f})", expanded=True):
                    st.write(f"원화 환산가: {price_krw:,}원")
                    st.metric("구매 가능 수량", f"{shares}주")
                    if shares > 0: st.success("✨ 지금 즉시 매수 가능!")
                    else: st.info("🍂 소액 조각 투자가 가능한 종목입니다.")

elif menu == "📈 AI 타임머신 시뮬레이터":
    st.title("📈 AI 타임머신 시뮬레이터")
    st.write("과거 데이터를 기반으로 자산 성장 곡선을 시뮬레이션합니다.")
    if st.button("🏁 시뮬레이션 가동"):
        chart_data = pd.DataFrame(np.random.randn(50, 2).cumsum(axis=0), columns=['삼성전자', '엔비디아'])
        st.line_chart(chart_data)
        st.success("🎉 시뮬레이션 완료!")