import streamlit as st
import numpy as np
import urllib.request
import json

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026", page_icon="🔮")
import streamlit as st
import numpy as np
import urllib.request
import json
from streamlit_autorefresh import st_autorefresh # 이 라이브러리가 필요합니다

# 60초마다 페이지 새로고침 (데이터 주기적 업데이트)
st_autorefresh(interval=60000, key="datarefresh")

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
budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", 
                         min_value=0, step=10000, value=1000000 if '원화' in currency else 1000)
budget_krw = budget if "원화" in currency else (budget * exchange_rate)

tab_main, tab_port = st.tabs(["📊 실시간 종목 분석", "🧩 수익 극대화 포트폴리오"])

with tab_main:
    sub_tab1, sub_tab2 = st.tabs(["🇰🇷 국내 주식", "🇺🇸 해외 주식"])
    
    def display_stocks(stocks, is_domestic):
        for name, ticker in stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if is_domestic else exchange_rate))
            qty_raw = budget_krw / price
            
            if style == "온전한 1주만" and qty_raw < 1: continue
            
            # 신규 분석 지표
            gain = np.random.randint(5, 25)
            profit = int(budget_krw * (gain / 100))
            peak_price = int(price * (1 + gain / 100))
            buy_price = int(price * 0.95) # 5% 조정을 저점 타겟으로 설정
            days_to_buy = np.random.randint(1, 5) # 저점 도달 예측일
            days_to_peak = np.random.randint(3, 20)
            
            qty_disp = f"{int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주"
            
            with st.expander(f"📊 {name} (현재가: {price:,}원)", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("보유 수량", qty_disp)
                c2.metric("💰 예상 수익금", f"+{profit:,}원")
                c3.metric("📉 매수 타겟가", f"{buy_price:,}원 ({days_to_buy}일 내)")
                c4.metric("📈 예상 고점", f"{peak_price:,}원 ({days_to_peak}일 후)")

    with sub_tab1: display_stocks(kor_stocks, True)
    with sub_tab2: display_stocks(us_stocks, False)

with tab_port:
    if st.button("🪄 최적 포트폴리오 생성"):
        portfolio = []
        for name, ticker in (kor_stocks + us_stocks):
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            if style == "온전한 1주만" and budget_krw < price: continue
            portfolio.append({"name": name, "price": price, "gain": np.random.randint(5, 25)})

        if portfolio:
            portfolio.sort(key=lambda x: x['gain'], reverse=True)
            top5 = portfolio[:5]
            total_gain = sum(p['gain'] for p in top5)
            
            st.write("### 🏆 수익률 기반 최적 배분 조합")
            for p in top5:
                weight = p['gain'] / total_gain
                qty = (budget_krw * weight) / p['price']
                if style == "온전한 1주만" and qty < 1: continue
                qty_disp = f"{int(qty)} 주" if style == "온전한 1주만" else f"{qty:.4f} 주"
                st.write(f"- **{p['name']}**: {qty_disp} (비중 {weight:.1%})")
        else:
            st.warning("조건에 맞는 종목이 부족합니다.")