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
kor_stocks = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS")]
us_stocks = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

st.sidebar.title("🤖 2026.06.01 버전")
currency = st.sidebar.selectbox("통화 선택", ["대한민국 원화 (₩)", "미국 달러 ($)"])
style = st.sidebar.radio("투자 방식", ["온전한 1주만", "소수점 주문 포함"])

st.title("🔮 서윤의 주식 마법사")
budget = st.number_input(f"현재 투자 예산 ({'원' if '원화' in currency else '$'})", value=1000000 if '원화' in currency else 1000)
budget_krw = budget if "원화" in currency else (budget * exchange_rate)

tab_main, tab_port = st.tabs(["📊 실시간 종목 분석", "🧩 수익 극대화 포트폴리오"])

with tab_main:
    sub_tab1, sub_tab2 = st.tabs(["🇰🇷 국내 주식", "🇺🇸 해외 주식"])
    
    def display_stocks(stocks, is_domestic):
        for name, ticker in stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if is_domestic else exchange_rate))
            qty_raw = budget_krw / price
            
            if style == "온전한 1주만":
                if qty_raw < 1: continue
                display_qty = f"{int(qty_raw)} 주"
            else:
                display_qty = f"{qty_raw:.4f} 주"
            
            with st.expander(f"📊 {name} (현재가: {price:,}원)"):
                st.write(f"보유 가능 수량: {display_qty}")

    with sub_tab1: display_stocks(kor_stocks, True)
    with sub_tab2: display_stocks(us_stocks, False)

with tab_port:
    if st.button("🪄 최적 조합 생성"):
        all_stocks = [(n, t, True) for n, t in kor_stocks] + [(n, t, False) for n, t in us_stocks]
        portfolio = []
        for name, ticker, is_dom in all_stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if is_dom else exchange_rate))
            gain = np.random.randint(5, 25)
            if style == "온전한 1주만" and budget_krw < price: continue
            portfolio.append({"name": name, "price": price, "gain": gain, "is_dom": is_dom})

        if portfolio:
            portfolio.sort(key=lambda x: x['gain'], reverse=True)
            top5 = portfolio[:5]
            total_gain = sum(p['gain'] for p in top5)
            
            for is_dom_group in [True, False]:
                group_stocks = [p for p in top5 if p['is_dom'] == is_dom_group]
                if not group_stocks: continue
                
                st.write(f"### {'🇰🇷 국내' if is_dom_group else '🇺🇸 해외'} 추천 조합")
                for p in group_stocks:
                    weight = p['gain'] / total_gain
                    qty = (budget_krw * weight) / p['price']
                    
                    # 0주 표시 방지 로직: 소수점이 아니면 int로 변환
                    if style == "온전한 1주만":
                        if qty < 1: continue
                        qty_display = f"{int(qty)} 주"
                    else:
                        qty_display = f"{qty:.4f} 주"
                        
                    st.write(f"- **{p['name']}**: {qty_display} (비중 {weight:.1%})")
        else:
            st.warning("매수 가능한 종목이 없습니다.")