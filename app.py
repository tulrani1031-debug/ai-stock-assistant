import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 기술적 분석 엔진 (저점/고점 판별)
def analyze_tech(ticker_symbol):
    t = yf.Ticker(ticker_symbol)
    df = t.history(period="1mo")
    if len(df) < 20: return None
    
    # 볼린저 밴드 계산 (고점/저점 판단)
    df['MA20'] = df['Close'].rolling(window=20).mean()
    df['STD'] = df['Close'].rolling(window=20).std()
    df['Upper'] = df['MA20'] + (df['STD'] * 2)
    df['Lower'] = df['MA20'] - (df['STD'] * 2)
    
    current_price = df['Close'].iloc[-1]
    
    # 분석 로직: 저점(하단 밴드 근접), 고점(상단 밴드 근접)
    if current_price <= df['Lower'].iloc[-1]:
        return "저점(매수 기회)", "반등 가능성 높음"
    elif current_price >= df['Upper'].iloc[-1]:
        return "고점(매도 기회)", "조정 가능성 높음"
    return "관망", "추세 확인 필요"

# 2. UI 레이아웃
st.title("🚀 실시간 시장 주도주 & 타점 분석기")

# 종목 입력 (원하는 종목 혹은 대형주 리스트)
ticker_input = st.text_input("분석할 종목 코드를 입력하세요 (예: 005930.KS, NVDA)")

if st.button("분석 실행"):
    res = analyze_tech(ticker_input)
    if res:
        st.subheader(f"종목: {ticker_input}")
        st.metric("현재 분석 상태", res[0])
        st.write(f"**AI 의견:** {res[1]}")
    else:
        st.error("데이터를 가져올 수 없습니다.")