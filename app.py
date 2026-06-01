import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 주식 마법사 복구 모드")

st.title("🔮 데이터 강제 로딩 테스트")

def safe_get_data(ticker_symbol):
    try:
        # Ticker 객체를 직접 생성하여 더 안정적으로 호출
        ticker = yf.Ticker(ticker_symbol)
        df = ticker.history(period="3mo")
        if df.empty:
            return None
        return df
    except Exception as e:
        return f"에러 발생: {e}"

# 테스트할 종목
test_stocks = [("삼성전자", "005930.KS"), ("NVIDIA", "NVDA")]

for name, symbol in test_stocks:
    data = safe_get_data(symbol)
    if isinstance(data, pd.DataFrame):
        st.success(f"{name} 데이터 로딩 성공!")
        st.line_chart(data['Close'])
    else:
        st.error(f"{name} 로딩 실패: {data}")