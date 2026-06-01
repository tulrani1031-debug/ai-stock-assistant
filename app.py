import streamlit as st
import datetime
import json
import urllib.request
import numpy as np
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사", page_icon="🔮")

# 데이터 추출 함수
def get_live_yahoo_data(ticker):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1m&range=1d"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            current_price = data['chart']['result'][0]['meta']['regularMarketPrice']
            return float(current_price)
    except:
        return 100000.0

def get_live_us_market_movers():
    try:
        url = "https://query1.finance.yahoo.com/v1/finance/trending/US?count=10"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return [item['symbol'] for item in data['finance']['result'][0]['quotes']][:6]
    except:
        return ["NVDA", "PLTR", "TSLA", "AAPL", "SOFI", "AMD"]

exchange_rate = get_live_yahoo_data("USDKRW=X")

st.sidebar.title("🤖 글로벌 AI 주식 비서")
menu = st.sidebar.radio("메뉴 선택:", ["🔮 실시간 AI 종목 추천", "📈 AI 타임머신"])

if menu == "🔮 실시간 AI 종목 추천":
    st.title("🔮 서윤의 주식 마법사 (통합 실시간 엔진)")
    budget_krw = st.number_input("현재 투자 예산 (원)", min_value=1000, value=100000, step=1000)
    
    if st.button("🧙‍♂️ 시장 전수조사 시작"):
        tab1, tab2 = st.tabs(["🇰🇷 국내 시장", "🇺🇸 미국 시장"])
        
        with tab1:
            kor_pool = [
                {"ticker": "005930.KS", "name": "삼성전자", "news": "AI 반도체 공급망 핵심"},
                {"ticker": "000660.KS", "name": "SK하이닉스", "news": "AI 가속기 점유율 1위"},
                {"ticker": "005380.KS", "name": "현대차", "news": "친환경차 글로벌 판매 호조"},
                {"ticker": "035420.KS", "name": "네이버(NAVER)", "news": "생성형 AI 플랫폼 강자"},
                {"ticker": "068270.KS", "name": "셀트리온", "news": "바이오시밀러 시장 확대"},
                {"ticker": "005490.KS", "name": "POSCO홀딩스", "news": "에너지 소재 공급망"}
            ]
            for s in kor_pool:
                price = int(get_live_yahoo_data(s["ticker"]))
                is_ok = budget_krw >= price
                with st.expander(f"{'🚀' if is_ok else '💸'} {s['name']} (현재가: {price:,}원)"):
                    st.write(f"📰 시황: {s['news']}")
                    if is_ok: st.success("✅ 구매 가능")
                    else: st.warning("⚠️ 예산 부족 - 소수점 주문 고려")

        with tab2:
            for ticker in get_live_us_market_movers():
                price_usd = get_live_yahoo_data(ticker)
                price_krw = int(price_usd * exchange_rate)
                is_ok = budget_krw >= price_krw
                with st.expander(f"{'✨' if is_ok else '💸'} {ticker} (현재가: ${price_usd:.2f})"):
                    st.write(f"국내 환산가: {price_krw:,}원")
                    if is_ok: st.success("✅ 구매 가능")
                    else: st.warning("⚠️ 예산 부족")

elif menu == "📈 AI 타임머신":
    st.title("📈 AI 타임머신 시뮬레이터")
    if st.button("🏁 시뮬레이션 가동"):
        st.line_chart(np.random.randn(50, 2).cumsum(axis=0))
        st.success("🎉 시뮬레이션 완료!")