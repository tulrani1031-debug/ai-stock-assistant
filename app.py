import streamlit as st
import yfinance as yf
import pandas as pd
import time

# 캐싱 적용: 동일한 종목은 다시 호출하지 않고 저장된 데이터를 사용
@st.cache_data(ttl=3600)  # 1시간 동안 데이터 저장
def get_stock_data(ticker):
    try:
        t = yf.Ticker(ticker)
        # 데이터 호출을 최소화합니다
        df = t.history(period="3mo")
        if df.empty: return None
        
        # 환율 호출도 한 번만 하도록 최적화
        rate = 1
        if 'USD' in ticker or ticker.isalpha():
            try:
                rate = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
            except:
                rate = 1380
        
        curr = df['Close'].iloc[-1]
        ma20 = df['Close'].rolling(20).mean().iloc[-1]
        std20 = df['Close'].rolling(20).std().iloc[-1]
        
        return curr, (ma20 - (std20 * 2)), (ma20 + (std20 * 2)), rate
    except Exception as e:
        return None

st.title("💰 종목 타점 및 예상 수익 분석기")

ticker_input = st.text_input("종목 티커 입력 (예: NVDA, 005930.KS)").upper()

if st.button("분석 실행"):
    with st.spinner('데이터를 가져오는 중...'):
        result = get_stock_data(ticker_input)
        
    if result:
        curr, low, high, rate = result
        profit_pot = ((high - curr) / curr) * 100
        
        data = {
            "항목": ["현재가", "매수(저점)", "매도(고점)", "예상 수익률"],
            "달러/원화": [f"${curr:.2f} ({curr*rate:,.0f}원)", 
                        f"${low:.2f} ({low*rate:,.0f}원)", 
                        f"${high:.2f} ({high*rate:,.0f}원)", 
                        f"{profit_pot:.2f}%"]
        }
        st.table(pd.DataFrame(data))
        st.info("💡 캐싱 기능이 적용되어 서버 부하를 최소화했습니다.")
    else:
        st.error("데이터를 가져오는 데 실패했습니다. 잠시 후 다시 시도하거나 티커를 확인하세요.")