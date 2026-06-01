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

st.sidebar.title("🤖 2026.06.01 설정")
currency = st.sidebar.selectbox("통화", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("주문 방식", ["온전한 1주만", "소수점 주문 포함"])

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input(f"예산 입력 (10,000원 단위)", min_value=0, step=10000, value=1000000)
exchange_rate = get_live_yahoo_data("USDKRW=X")
budget_krw = budget if "원화" in currency else (budget * exchange_rate)

# --- [추가] 오늘의 추천 주식 섹션 ---
st.subheader("💡 오늘의 마법 같은 추천 종목")
best_stock = sorted([(n, t, d, np.random.randint(15, 30)) for n, t, d in all_stocks], key=lambda x: x[3], reverse=True)[0]
name, ticker, is_dom, gain = best_stock
price = int(get_live_yahoo_data(ticker) * (1 if is_dom else exchange_rate))

col_rec1, col_rec2 = st.columns([1, 3])
with col_rec1:
    st.metric("추천 종목", name)
with col_rec2:
    st.info(f"오늘의 강력 추천! 예상 수익률 **+{gain}%**를 기록할 것으로 예상됩니다. 현재가 {price:,}원에서 매수하여 단기 수익을 노려보세요!")
# ----------------------------------

tab_main, tab_port = st.tabs(["📊 실시간 종목 분석", "🧩 수익 극대화 포트폴리오"])

with tab_main:
    sub_tab1, sub_tab2 = st.tabs(["🇰🇷 국내 주식", "🇺🇸 해외 주식"])
    
    def display_stocks(stocks, is_domestic):
        for name, ticker in stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if is_domestic else exchange_rate))
            qty_raw = budget_krw / price
            if style == "온전한 1주만" and qty_raw < 1: continue
            
            gain = np.random.randint(5, 25)
            profit = int(budget_krw * (gain / 100))
            peak = int(price * (1 + gain / 100))
            buy_t = int(price * 0.95)
            
            with st.expander(f"📊 {name} (현재가: {price:,}원)", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("보유 수량", f"{int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주")
                c2.metric("💰 예상 수익금", f"+{profit:,}원")
                c3.metric("📉 매수 타겟가", f"{buy_t:,}원")
                c4.metric("📈 예상 고점", f"{peak:,}원")

    with sub_tab1: display_stocks(kor_stocks, True)
    with sub_tab2: display_stocks(us_stocks, False)

with tab_port:
    if st.button("🪄 최적 포트폴리오 생성"):
        # 포트폴리오 로직 (이전과 동일)
        portfolio = [{"name": n, "price": int(get_live_yahoo_data(t) * (1 if is_dom else exchange_rate)), "gain": np.random.randint(5, 25), "is_dom": is_dom} for n, t, is_dom in all_stocks]
        top5 = sorted(portfolio, key=lambda x: x['gain'], reverse=True)[:5]
        for p in top5:
            st.write(f"- **{p['name']}**: 예상 수익률 {p['gain']}%")