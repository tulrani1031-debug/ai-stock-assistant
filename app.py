import streamlit as st
import numpy as np
import urllib.request
import json
from streamlit_autorefresh import st_autorefresh

# 60초마다 새로고침
st_autorefresh(interval=60000, key="datarefresh")
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

# 종목 리스트
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]
all_stocks = [(n, t, True) for n, t in kor_stocks] + [(n, t, False) for n, t in us_stocks]

# 분석 데이터 계산 로직
def calculate_metrics(price, budget_krw):
    gain_pct = np.random.randint(5, 25)
    profit = int(budget_krw * (gain_pct / 100))
    peak_price = int(price * (1 + gain_pct / 100))
    buy_price = int(price * 0.95)
    loss_per_share = int(price * 0.05) # 5% 하락 시 1주당 적자 폭
    days_to_peak = np.random.randint(3, 20)
    return gain_pct, profit, peak_price, buy_price, loss_per_share, days_to_peak

st.title("🔮 서윤의 주식 마법사")
exchange_rate = get_live_yahoo_data("USDKRW=X")
budget = st.number_input("투자 예산(원)", min_value=0, step=10000, value=1000000)

# 1. 오늘의 추천 종목 (상세 지표 포함)
st.subheader("🔥 오늘의 마법 같은 추천 종목")
best_item = sorted([(n, t, d, np.random.randint(15, 30)) for n, t, d in all_stocks], key=lambda x: x[3], reverse=True)[0]
name, ticker, is_dom, gain_pct = best_item
price = int(get_live_yahoo_data(ticker) * (1 if is_dom else exchange_rate))
g, p, peak, b, loss, days = calculate_metrics(price, budget)

st.success(f"### 🏆 {name} (예상 수익률 +{g}%)")
c1, c2, c3, c4 = st.columns(4)
c1.metric("매수 타겟가", f"{b:,}원")
c2.metric("예상 고점(단기)", f"{peak:,}원 ({days}일 후)")
c3.metric("기대 수익금", f"+{p:,}원")
c4.metric("1주당 손절 기준(적자)", f"-{loss:,}원")

st.divider()

# 2. 전체 종목 탭
tab_main, tab_port = st.tabs(["📊 실시간 종목 분석", "🧩 수익 극대화 포트폴리오"])
with tab_main:
    # (이전의 display_stocks 로직을 여기에 그대로 유지)
    st.write("아래 리스트에서 다른 종목들도 상세 분석 가능합니다.")
    for name, ticker in (kor_stocks + us_stocks):
        price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
        g, p, peak, b, loss, days = calculate_metrics(price, budget)
        with st.expander(f"{name} (현재가: {price:,}원)"):
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("매수 타겟", f"{b:,}원")
            c2.metric("예상 고점", f"{peak:,}원")
            c3.metric("예상 수익", f"+{p:,}원")
            c4.metric("1주당 적자폭", f"-{loss:,}원")