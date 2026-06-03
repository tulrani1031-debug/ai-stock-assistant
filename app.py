import streamlit as st
import yfinance as yf
import pandas as pd

# 안정적인 데이터 호출 함수
def get_stock_data(ticker_symbol):
    try:
        t = yf.Ticker(ticker_symbol)
        hist = t.history(period="5d")
        if hist.empty: return None, 0
        return t, hist['Volume'].iloc[-1]
    except:
        return None, 0

def analyze(ticker_symbol, is_us):
    t, vol = get_stock_data(ticker_symbol)
    if t is None: return None
    
    df = t.history(period="1mo")
    rate = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1] if is_us else 1
    
    curr = df['Close'].iloc[-1]
    # 볼린저 밴드 계산
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    std20 = df['Close'].rolling(20).std().iloc[-1]
    
    low = (ma20 - (std20 * 2)) * rate
    high = (ma20 + (std20 * 2)) * rate
    
    return [ticker_symbol, f"{curr * rate:,.0f}원", f"{low:,.0f}원", f"{high:,.0f}원"]

st.title("🔥 실시간 주도주 분석기")

if st.button("시장 분석 실행"):
    with st.spinner('데이터를 분석 중입니다...'):
        kr_list = ["005930.KS", "000660.KS", "373220.KS"]
        us_list = ["NVDA", "TSLA", "AAPL"]
        
        # 가장 거래량이 많은 종목 찾기
        best_kr = max(kr_list, key=lambda x: get_stock_data(x)[1])
        best_us = max(us_list, key=lambda x: get_stock_data(x)[1])
        
        res = [analyze(best_kr, False), analyze(best_us, True)]
        st.table(pd.DataFrame(res, columns=["종목", "현재가", "저점(매수)", "고점(매도)"]))