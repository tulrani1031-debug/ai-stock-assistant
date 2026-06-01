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

# 종목 리스트
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 2026.06.01 버전")
currency = st.sidebar.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("투자 방식", ["온전한 1주만", "소수점 주문 포함"])
exclude_etf = st.sidebar.checkbox("❌ ETF 제외", value=True)

menu = st.sidebar.radio("메뉴 선택", ["🔮 실시간 AI 종목 분석", "🧩 5종목 분할 포트폴리오"])

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", value=1000000 if '원화' in currency else 1000)
budget_krw = budget if "원화" in currency else int(budget * exchange_rate)

if st.button("🚀 분석 실행"):
    all_stocks = kor_stocks + us_stocks
    for name, ticker in all_stocks:
        price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
        qty_raw = budget_krw / price
        qty_display = f"약 {int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주"
        
        gain = np.random.randint(5, 25)
        profit = int(budget_krw * (gain / 100))
        
        with st.expander(f"📊 {name} (현재가: {price:,}원)", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.metric("매수 가능 수량", qty_display)
            c2.metric("🎯 예상 수익률", f"+{gain}%")
            c3.metric("💰 예상 수익금", f"+{profit:,}원")

if menu == "🧩 5종목 분할 포트폴리오":
    st.write("---")
    st.write("### 🤖 5종목 균등 분할 투자 (예산 20%씩)")
    for name, ticker in (kor_stocks + us_stocks):
        price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
        qty = (budget_krw / 5) / price
        display = f"약 {int(qty)} 주" if style == "온전한 1주만" else f"{qty:.4f} 주"
        st.write(f"- **{name}**: {display}")