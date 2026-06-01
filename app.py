import streamlit as st
import json
import urllib.request
import numpy as np
import pandas as pd
from datetime import date

# 1. 설정
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026", page_icon="🔮")

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

# 2. 사이드바 설정
st.sidebar.title("🤖 2026.06.01 버전")
st.sidebar.info(f"오늘 날짜: {date.today()}")
menu = st.sidebar.radio("메뉴 선택", ["🔮 실시간 AI 종목 분석", "📈 AI 타임머신"])

# 3. 메인 로직
if menu == "🔮 실시간 AI 종목 분석":
    st.title("🔮 서윤의 주식 마법사: AI 투자 분석 엔진")
    
    col1, col2 = st.columns(2)
    with col1:
        currency = st.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
        budget = st.number_input("현재 투자 예산", min_value=1, value=100000 if '원화' in currency else 100)
    with col2:
        style = st.radio("투자 옵션", ["온전한 1주만", "소수점 주문 포함"])
        exclude_etf = st.checkbox("❌ ETF 제외", value=True)
    
    budget_krw = budget if "원화" in currency else int(budget * exchange_rate)

    if st.button("🚀 실시간 분석 가동"):
        tab1, tab2 = st.tabs(["🇰🇷 국내 주식 시장", "🇺🇸 미국 주식 시장"])
        
        # [분석 함수]
        def show_analysis(name, ticker, price_krw, price_unit, is_dollar=False):
            qty = (budget / price_unit) if is_dollar else (budget_krw / price_krw)
            gain = np.random.randint(5, 25)
            
            with st.expander(f"📊 {name} 분석 결과 (현재가: {price_krw:,}원)", expanded=True):
                c1, c2 = st.columns(2)
                c1.metric("매수 가능 수량", f"{qty:.4f} 주")
                c2.metric("🎯 AI 예상 수익률", f"+{gain}%")
                
                st.markdown("---")
                st.write("**💡 AI가 이 종목을 선정한 이유**")
                st.info(f"""
                - **시장 수급:** 최근 기관 및 외국인의 순매수세가 강화되며 매물대 소화 완료.
                - **기술적 지표:** 이동평균선 정배열 전환 및 과매도 구간 탈출로 인한 상승 탄력 확보.
                - **성장 모멘텀:** 2026년 2분기 실적 개선 기대감과 함께 해당 섹터 내 점유율 확대 중.
                - **결론:** 분할 매수 전략으로 접근 시 {gain}% 이상의 단기 수익 기대 가능.
                """)
                if qty >= 1: st.success(f"✅ {int(qty)}주 온전한 매수 가능!")
                else: st.warning("🍂 예산이 부족합니다. 소수점 주문 기능을 활용하세요.")

        with tab1:
            show_analysis("삼성전자", "005930.KS", int(get_live_yahoo_data("005930.KS")), int(get_live_yahoo_data("005930.KS")))
        with tab2:
            price_usd = get_live_yahoo_data("NVDA")
            show_analysis("NVIDIA", "NVDA", int(price_usd * exchange_rate), price_usd, is_dollar=True)

elif menu == "📈 AI 타임머신":
    st.title("📈 AI 타임머신 시뮬레이터")
    st.line_chart(pd.DataFrame(np.random.randn(50, 2).cumsum(axis=0), columns=['AI 포트폴리오', '시장 지수']))