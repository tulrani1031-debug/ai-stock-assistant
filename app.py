import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 호출 제한을 우회하기 위한 데이터 가져오기 로직
def get_safe_data(ticker):
    # 세션 기반 호출로 RateLimit 우회 시도
    session = yf.shared.get_session()
    t = yf.Ticker(ticker, session=session)
    df = t.history(period="1mo")
    return df

# 2. 이름 기반 티커 검색 (오류 방지용 예외처리 강화)
def search_ticker_safe(name):
    try:
        # 검색 대신 직접 매칭을 우선하고, 실패 시에만 제한적인 검색 실행
        if name in ["삼성전자", "005930"]: return "005930.KS"
        search = yf.Search(name)
        if search.results: return search.results[0]['symbol']
    except: return None
    return None

st.title("🔥 타협 없는 실시간 타점 분석기")

name_input = st.text_input("종목명 입력 (예: 삼성전자, 엔비디아)")

if st.button("강제 분석 실행"):
    with st.spinner('서버 우회 및 실시간 분석 중...'):
        ticker = search_ticker_safe(name_input)
        if ticker:
            df = get_safe_data(ticker)
            if not df.empty:
                curr = df['Close'].iloc[-1]
                ma20 = df['Close'].rolling(20).mean().iloc[-1]
                std20 = df['Close'].rolling(20).std().iloc[-1]
                
                low = ma20 - (std20 * 2)
                high = ma20 + (std20 * 2)
                
                st.write(f"### 분석 완료: {ticker}")
                st.metric("현재가", f"{curr:,.0f}")
                st.write(f"매수 타점: {low:,.0f} | 매도 타점: {high:,.0f}")
                
                # 기술적 지표 시각화 (이해를 돕기 위한 밴드 구성)