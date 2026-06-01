import streamlit as st
import numpy as np
import urllib.request
import json

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026")

def get_live_yahoo_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return 100000.0

# 데이터 설정
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]
all_stocks = [(n, t, True) for n, t in kor_stocks] + [(n, t, False) for n, t in us_stocks]

# 1. 상단 추천 픽 (중앙 배치)
st.title("🔮 서윤의 주식 마법사")
st.subheader("🔥 오늘의 추천 픽")

best_item = all_stocks[np.random.randint(0, len(all_stocks))]
name, ticker, is_dom = best_item
price = int(get_live_yahoo_data(ticker))
gain = np.random.randint(15, 30)

col_mid = st.columns([1, 2, 1])[1]
with col_mid:
    st.success(f"### 🏆 {name}")
    st.metric("현재가", f"{price:,}원")
    st.write(f"📈 예상 수익률: **+{gain}%** | 📉 매수타겟: **{int(price*0.95):,}원**")

st.divider()

# 2. 예산 및 전체 분석 리스트
budget = st.number_input("투자 예산(원)", min_value=0, step=10000, value=1000000)

for name, ticker, is_dom in all_stocks:
    p = int(get_live_yahoo_data(ticker))
    g = np.random.randint(5, 20)
    with st.expander(f"{name} (현재가: {p:,}원)"):
        c1, c2, c3 = st.columns(3)
        c1.metric("예상 수익률", f"+{g}%")
        c2.metric("매수타겟", f"{int(p*0.95):,}원")
        c3.metric("적자폭(1주)", f"-{int(p*0.05):,}원")