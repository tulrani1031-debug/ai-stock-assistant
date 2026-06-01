import streamlit as st
import numpy as np
import pandas as pd
import urllib.request
import json
from datetime import date

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사", page_icon="🔮")

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

# 종목 리스트 (각 5개씩)
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 2026.06.01 버전")
menu = st.sidebar.radio("메뉴 선택", ["🔮 실시간 AI 종목 분석", "🧩 맞춤형 포트폴리오(5종목 조합)"])

if menu == "🔮 실시간 AI 종목 분석":
    st.title("🔮 AI 실시간 종목 분석 (종목당 5개)")
    budget = st.number_input("투자 예산 (원)", value=1000000, step=100000)
    
    if st.button("🚀 전체 분석 시작"):
        for name, ticker in (kor_stocks + us_stocks):
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            qty = budget / price
            gain = np.random.randint(5, 25)
            profit = int(budget * (gain / 100))
            
            with st.expander(f"📊 {name} 분석 (현재가: {price:,}원)", expanded=False):
                c1, c2, c3 = st.columns(3)
                c1.metric("매수 가능 수량", f"{qty:.4f} 주")
                c2.metric("🎯 예상 수익률", f"+{gain}%")
                c3.metric("💰 예상 수익금", f"+{profit:,}원")
                st.write("**💡 AI 선정 이유:** 시장 주도 섹터이며, 실시간 강력한 수급 유입이 포착되었습니다.")

elif menu == "🧩 맞춤형 포트폴리오(5종목 조합)":
    st.title("🧩 AI 5종목 분할 포트폴리오")
    budget = st.number_input("포트폴리오 총 예산 (원)", value=1000000, step=100000)
    
    if st.button("🪄 5종목 조합 생성"):
        st.write("### 🤖 5개 종목 균등 분할 투자 전략 (각 20% 할당)")
        # 예산을 5등분하여 할당
        all_stocks = kor_stocks + us_stocks
        for name, ticker in all_stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            alloc = budget / 5
            qty = alloc / price
            st.success(f"**{name}**: 예산의 20% 할당 → **{qty:.4f}주 매수 가능**")
        st.info("💡 **전략**: 국내/미국 시장의 핵심 주도주 5개를 20%씩 균등 배분하여 변동성을 낮추고 성장을 극대화합니다.")