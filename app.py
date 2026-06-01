import streamlit as st
import numpy as np
import yfinance as yf
from streamlit_autorefresh import st_autorefresh

st_autorefresh(interval=60000, key="datarefresh")
st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026")

# 1. 데이터 호출 최적화
@st.cache_data(ttl=300)
def get_stock_analysis(ticker):
    try:
        # 데이터가 없을 경우를 대비해 기간을 6개월로 늘림
        df = yf.download(ticker, period="6mo", interval="1d", progress=False)
        if df.empty or len(df) < 20: return None
        
        # 컬럼명이 튜플로 들어오는 경우 방지 (최신 yfinance 대응)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
            
        close = df["Close"]
        current = float(close.iloc[-1])
        ma5 = float(close.tail(5).mean())
        ma20 = float(close.tail(20).mean())

        score = (40 if ma5 > ma20 else 0) + (30 if current > ma20 else 0)
        grade = "🔥 강력매수" if score >= 60 else ("🤔 관망" if score >= 30 else "❌ 비추천")

        return {"price": current, "score": score, "grade": grade, "ma5": ma5, "ma20": ma20, "chart": close}
    except Exception as e:
        return None

# 종목 리스트
stocks = [("삼성전자", "005930.KS"), ("NVIDIA", "NVDA"), ("Tesla", "TSLA")]

st.title("🔮 서윤의 주식 마법사")

# 2. 데이터 확인 (강제 출력)
for name, ticker in stocks:
    analysis = get_stock_analysis(ticker)
    if analysis:
        st.success(f"{name} 데이터를 성공적으로 불러왔습니다.")
        st.metric("현재가", f"{analysis['price']:,.0f}원")
        st.line_chart(analysis["chart"])
    else:
        st.error(f"{name} ({ticker}) 데이터를 가져올 수 없습니다. 인터넷 연결이나 종목 코드를 확인하세요.")