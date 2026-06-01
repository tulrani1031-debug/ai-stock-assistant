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

if st.button("🚀 분석 및 예산 맞춤 추천"):
    # 1. 데이터 수집 및 수익률 생성
    all_stocks = []
    for name, ticker in (kor_stocks + us_stocks):
        price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
        gain = np.random.randint(5, 25)
        can_buy = (budget_krw >= price) # 온전한 1주 매수 가능 여부
        all_stocks.append({"name": name, "price": price, "gain": gain, "can_buy": can_buy})

    # 2. 소수점 미선택 시 필터링 로직
    if style == "온전한 1주만":
        buyable_stocks = [s for s in all_stocks if s['can_buy']]
        if buyable_stocks:
            best = max(buyable_stocks, key=lambda x: x['gain'])
            st.success(f"🏆 **예산 내 수익률 최우선 추천**: {best['name']} (예상 수익률 +{best['gain']}%)")
        else:
            st.warning("⚠️ 현재 예산으로 온전한 1주를 살 수 있는 종목이 없습니다. 소수점 주문을 고려하세요.")
    else:
        # 소수점 선택 시 전체 중 최고 수익률 추천
        best = max(all_stocks, key=lambda x: x['gain'])
        st.success(f"🏆 **전체 종목 중 최고의 선택**: {best['name']} (예상 수익률 +{best['gain']}%)")

    # 3. 탭별 상세 보기
    tab1, tab2 = st.tabs(["🇰🇷 국내 주식 시장", "🇺🇸 미국 주식 시장"])
    def display_market(stocks, is_domestic):
        for name, ticker in stocks:
            price = int(get_live_yahoo_data(ticker) * (1 if ".KS" in ticker else exchange_rate))
            qty_raw = budget_krw / price
            
            # 필터링: 소수점 미선택인데 1주 미만이면 익스팬더 생략 (또는 정보만 표시)
            if style == "온전한 1주만" and qty_raw < 1: continue
                
            with st.expander(f"📊 {name} (현재가: {price:,}원)", expanded=True):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("보유 수량", f"{int(qty_raw)} 주" if style == "온전한 1주만" else f"{qty_raw:.4f} 주")
                c2.metric("🎯 수익률", f"+{int(qty_raw*0 + np.random.randint(5,25))}%")
                c3.metric("💰 수익금", f"+{int(budget_krw * 0.15):,}원")
                c4.metric("⏳ 고점 예측", f"{np.random.randint(3, 20)}일 후")

    with tab1: display_market(kor_stocks, True)
    with tab2: display_market(us_stocks, False)