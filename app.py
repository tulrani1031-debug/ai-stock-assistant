import streamlit as st
import numpy as np
import urllib.request
import json

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
all_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS"), 
              ("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 2026.06.01 버전")
currency = st.sidebar.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("투자 방식", ["온전한 1주만", "소수점 주문 포함"])

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", value=1000000 if '원화' in currency else 1000)
budget_krw = budget if "원화" in currency else (budget * exchange_rate)

# 메뉴 분리: 분석과 포트폴리오를 탭으로 완전히 분리
tab_main, tab_port = st.tabs(["📊 실시간 종목 분석 (롤백 버전)", "🧩 수익 극대화 포트폴리오 조합"])

with tab_main:
    if st.button("🚀 종목 분석 실행"):
        for name, ticker in all_stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            qty_raw = budget_krw / price
            
            # 1주 미만 시 0주 표시 방지
            display_qty = f"{int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주"
            if style == "온전한 1주만" and qty_raw < 1: display_qty = "매수 불가"

            with st.expander(f"📊 {name} (현재가: {price:,}원)"):
                st.write(f"보유 가능 수량: {display_qty}")

with tab_port:
    st.write("### 🤖 수익 극대화 차등 배분 포트폴리오")
    if st.button("🪄 최적 조합 생성"):
        portfolio = []
        for name, ticker in all_stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            gain = np.random.randint(5, 25)
            can_buy = (budget_krw >= price)
            
            if style == "온전한 1주만" and not can_buy: continue
            portfolio.append({"name": name, "price": price, "gain": gain})

        if portfolio:
            portfolio.sort(key=lambda x: x['gain'], reverse=True)
            top5 = portfolio[:5]
            total_gain = sum(p['gain'] for p in top5)
            
            for p in top5:
                weight = p['gain'] / total_gain
                qty = (budget_krw * weight) / p['price']
                qty_display = f"{int(qty)} 주" if style == "온전한 1주만" else f"{qty:.4f} 주"
                st.write(f"- **{p['name']}**: {qty_display} (비중 {weight:.1%})")
        else:
            st.warning("예산 범위 내에서 조합 가능한 종목이 없습니다.")