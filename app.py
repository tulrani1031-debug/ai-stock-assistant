import streamlit as st
import yfinance as yf
import pandas as pd

def get_data(ticker):
    t = yf.Ticker(ticker)
    df = t.history(period="3mo")
    if df.empty: return None
    
    # 환율 정보
    rate = yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1] if 'USD' in ticker or ticker.isalpha() else 1
    
    # 볼린저 밴드 계산
    df['MA20'] = df['Close'].rolling(20).mean()
    df['STD'] = df['Close'].rolling(20).std()
    low = (df['MA20'] - (df['STD'] * 2)).iloc[-1]
    high = (df['MA20'] + (df['STD'] * 2)).iloc[-1]
    curr = df['Close'].iloc[-1]
    
    return curr, low, high, rate

st.title("💰 종목 타점 및 예상 수익 분석기")

ticker_input = st.text_input("종목 티커를 입력하세요 (예: NVDA, 005930.KS)").upper()

if st.button("분석 실행"):
    result = get_data(ticker_input)
    if result:
        curr, low, high, rate = result
        
        # 수익률 계산
        profit_pot = ((high - curr) / curr) * 100
        
        data = {
            "항목": ["현재가", "매수(저점)", "매도(고점)", "예상 수익률"],
            "달러($/원)": [f"${curr:.2f}", f"${low:.2f}", f"${high:.2f}", f"{profit_pot:.2f}%"],
            "원화(KRW)": [f"{curr*rate:,.0f}원", f"{low*rate:,.0f}원", f"{high*rate:,.0f}원", "-"]
        }
        st.table(pd.DataFrame(data))
        st.info(f"💡 현재가 대비 고점 도달 시 약 {profit_pot:.2f}%의 수익이 예상됩니다.")
    else:
        st.error("종목 정보를 찾을 수 없습니다. 티커를 확인하세요.")