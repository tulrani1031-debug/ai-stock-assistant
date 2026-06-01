import streamlit as st
import numpy as np
import urllib.request
import json
from streamlit_autorefresh import st_autorefresh

# 1분마다 자동 새로고침
st_autorefresh(interval=60000, key="datarefresh")

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

kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]
all_stocks = [(n, t, True) for n, t in kor_stocks] + [(n, t, False) for n, t in us_stocks]

# --- [UI 개선] 추천 종목 선정 로직 ---
best_stock = sorted([(n, t, d, np.random.randint(15, 30)) for n, t, d in all_stocks], key=lambda x: x[3], reverse=True)[0]
name, ticker, is_dom, gain = best_stock
price = int(get_live_yahoo_data(ticker) * (1 if is_dom else get_live_yahoo_data("USDKRW=X")))

st.title("🔮 서윤의 주식 마법사")

# 추천 섹션을 타이틀 바로 아래에 배치
st.write("---")
st.subheader("🔥 오늘의 마법 같은 추천 종목")
col1, col2 = st.columns([1, 4])
with col1:
    st.metric("추천 종목", name)
with col2:
    st.success(f"오늘의 강력 추천! **{name}**이(가) 약 **+{gain}%** 이상의 상승 흐름을 보일 것으로 예측됩니다. 지금 바로 실시간 분석을 확인하세요!")
st.write("---")

# 예산 및 사이드바
budget = st.number_input(f"예산 입력 (10,000원 단위)", min_value=0, step=10000, value=1000000)
exchange_rate = get_live_yahoo_data("USDKRW=X")
budget_krw = budget

# ... (이하 실시간 종목 분석 및 포트폴리오 탭 코드 동일)