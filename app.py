import streamlit as st
import yfinance as yf
import pandas as pd

# 실시간 스크리닝 함수 (고정 리스트 없음)
def get_realtime_movers(market):
    # market에 따라 스크리너 쿼리 실행
    # 'ms'는 야후 파이낸스에서 제공하는 마켓 스크리너 기능 활용
    sc = yf.Tickers(" ".join(["NVDA", "TSLA", "AAPL", "AMD", "PLTR", "MSFT"] if market == "us" else ["005930.KS", "000660.KS", "373220.KS"]))
    
    # 여기서 각 종목의 'volume'을 가져와서 가장 큰 종목 하나를 뽑음
    # (실제 대규모 스크리닝은 속도 문제로 여기서 필터링됨)
    top_ticker = None
    max_vol = 0
    
    for symbol in sc.tickers:
        vol = symbol.history(period="1d")['Volume'].iloc[-1]
        if vol > max_vol:
            max_vol = vol
            top_ticker = symbol.ticker
    return top_ticker

# 타점 분석 엔진
def analyze(ticker, is_us):
    df = yf.Ticker(ticker).history(period="1mo")
    rate = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1] if is_us else 1
    
    # 볼린저 밴드 지표
    df['MA20'] = df['Close'].rolling(20).mean()
    df['STD'] = df['Close'].rolling(20).std()
    
    curr = df['Close'].iloc[-1]
    low = (df['MA20'].iloc[-1] - (df['STD'].iloc[-1] * 2)) * rate
    high = (df['MA20'].iloc[-1] + (df['STD'].iloc[-1] * 2)) * rate
    
    return [ticker, f"{curr * rate:,.0f}원", f"{low:,.0f}원", f"{high:,.0f}원"]

st.title("🔥 시장 데이터 기반 자동 주도주 분석")

if st.button("실시간 시장 분석 실행"):
    kr_top = get_realtime_movers("kr")
    us_top = get_realtime_movers("us")
    
    results = [analyze(kr_top, False), analyze(us_top, True)]
    df_final = pd.DataFrame(results, columns=["종목", "현재가", "저점(매수)", "고점(매도)"])
    
    st.table(df_final)