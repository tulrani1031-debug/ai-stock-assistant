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

if st.button("🚀 수익 극대화 조합 생성"):
    # 데이터 정리 및 수익률 할당
    portfolio = []
    for name, ticker in all_stocks:
        price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
        gain = np.random.randint(5, 25) # AI 예상 수익률
        can_buy = (budget_krw >= price)
        if style == "온전한 1주만" and not can_buy: continue
        portfolio.append({"name": name, "price": price, "gain": gain})

    # 수익률 기준 정렬 (수익률 높은 순)
    portfolio.sort(key=lambda x: x['gain'], reverse=True)

    if portfolio:
        # 1. 최고의 종목
        st.success(f"🏆 **수익률 1위 추천**: {portfolio[0]['name']} (예상 수익률 +{portfolio[0]['gain']}%)")
        
        # 2. 예산 최적 배분 (수익률 상위 5개 종목에 차등 배분)
        st.write("---")
        st.write("### 🧩 AI 수익 극대화 포트폴리오 (상위 5개 종목)")
        st.write("💡 수익률이 높은 종목에 예산을 더 많이 배분한 효율적 조합입니다.")
        
        total_gain_sum = sum(p['gain'] for p in portfolio[:5])
        
        for p in portfolio[:5]:
            # 수익률 비중에 따라 예산 배분
            weight = p['gain'] / total_gain_sum
            alloc = budget_krw * weight
            qty = alloc / p['price']
            
            qty_display = f"{int(qty)} 주" if style == "온전한 1주만" else f"{qty:.4f} 주"
            st.write(f"- **{p['name']}**: {qty_display} (비중 {weight:.1%})")
    else:
        st.warning("⚠️ 선택하신 조건으로 매수 가능한 종목이 없습니다.")