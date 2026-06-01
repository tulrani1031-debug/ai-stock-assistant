import streamlit as st
import numpy as np
import urllib.request
import json

# 1. 설정 및 기본 데이터
st.set_page_config(layout="wide", page_title="🔮 오늘의 추천 픽")

def get_live_yahoo_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return float(data['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return 100000.0

kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
all_stocks = [(n, t, True) for n, t in kor_stocks]

# 2. 오늘의 추천 픽 선정 (랜덤 기반)
best_item = all_stocks[np.random.randint(0, len(all_stocks))]
name, ticker, is_dom = best_item
price = int(get_live_yahoo_data(ticker))

# 분석 지표 계산
gain_pct = np.random.randint(15, 30)
target_price = int(price * 0.95)
peak_price = int(price * (1 + gain_pct / 100))
profit = int(price * (gain_pct / 100))
loss = int(price * 0.05)

# 3. 화면 구성 (중앙 집중형)
st.title("🔮 오늘의 마법 같은 추천 종목")
st.markdown("---")

col_mid = st.columns([1, 2, 1])[1] # 중앙 정렬 효과
with col_mid:
    st.success(f"## 🏆 {name}")
    st.metric(label="현재가", value=f"{price:,} 원")
    st.write(f"📈 예상 수익률: **+{gain_pct}%**")
    st.write(f"📉 매수 타겟가: **{target_price:,} 원**")
    st.write(f"💰 기대 수익금(1주당): **+{profit:,} 원**")
    st.write(f"🔻 1주당 적자폭(손절가): **-{loss:,} 원**")

st.markdown("---")
if st.button("새로운 추천 픽 뽑기"):
    st.rerun()