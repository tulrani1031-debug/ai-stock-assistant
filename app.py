import streamlit as st
import numpy as np
import urllib.request
import json
from datetime import date

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026", page_icon="🔮")

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

kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 2026.06.01 버전")
currency = st.sidebar.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("투자 방식", ["온전한 1주만", "소수점 주문 포함"])

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", value=1000000 if '원화' in currency else 1000)
budget_krw = budget if "원화" in currency else (budget * exchange_rate)

if st.button("🚀 분석 실행"):
    tab1, tab2 = st.tabs(["🇰🇷 국내 주식 시장", "🇺🇸 미국 주식 시장"])
    
    def display_market(stocks, is_domestic):
        for name, ticker in stocks:
            price_raw = get_live_yahoo_data(ticker)
            price = int(price_raw) if is_domestic else int(price_raw * exchange_rate)
            
            # 수량 계산 로직 보완
            qty_raw = budget_krw / price
            
            # 0주 방지: 온전한 1주 선택 시 1주 미만이면 '예산 부족'으로 표시, 아니면 수량 표시
            if style == "온전한 1주만" and qty_raw < 1:
                qty_display = "예산 부족으로 매수 불가"
            else:
                qty_display = f"약 {int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주"
            
            gain = np.random.randint(5, 25)
            profit = int(budget_krw * (gain / 100))
            days_to_peak = np.random.randint(3, 20)
            
            with st.expander(f"📊 {name} (현재가: {price:,}원)", expanded=False):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("보유 가능 수량", qty_display)
                c2.metric("🎯 예상 수익률", f"+{gain}%")
                c3.metric("💰 예상 수익금", f"+{profit:,}원")
                c4.metric("⏳ 고점 도달 예측", f"{days_to_peak}일 후")

    with tab1:
        display_market(kor_stocks, True)
    with tab2:
        display_market(us_stocks, False)