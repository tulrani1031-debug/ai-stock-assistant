import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 이름으로 티커 자동 검색
def search_ticker(name):
    # 야후 파이낸스 검색 기능 활용
    search_results = yf.Search(name)
    results = search_results.results
    if results:
        # 가장 유사한 상위 1개 티커 반환
        return results[0]['symbol'], results[0]['shortname']
    return None, None

# 2. 분석 엔진 (고점/저점 도달 시기 예측)
def analyze_stock(ticker):
    df = yf.Ticker(ticker).history(period="6mo")
    if df.empty: return None
    
    curr = df['Close'].iloc[-1]
    ma20 = df['Close'].rolling(20).mean().iloc[-1]
    std20 = df['Close'].rolling(20).std().iloc[-1]
    
    low = ma20 - (std20 * 2)
    high = ma20 + (std20 * 2)
    
    # 도달 예상 기간 (변동성 기반 단순 예측)
    # 현재 가격이 하단/상단에서 얼마나 떨어져 있는지 계산
    dist_to_low = (curr - low) / curr * 100
    dist_to_high = (high - curr) / curr * 100
    
    return curr, low, high, dist_to_low, dist_to_high

st.title("🔍 자동 종목 검색 & 타점 분석기")

name_input = st.text_input("주식 이름을 입력하세요 (예: 삼성전자, 엔비디아)")

if st.button("분석 실행"):
    if name_input:
        ticker, actual_name = search_ticker(name_input)
        if ticker:
            st.write(f"### 검색 결과: **{actual_name} ({ticker})**")
            curr, low, high, d_low, d_high = analyze_stock(ticker)
            
            # 테이블로 정리
            data = {
                "구분": ["현재가", "매수 타점(저점)", "매도 타점(고점)"],
                "가격": [f"{curr:,.2f}", f"{low:,.2f}", f"{high:,.2f}"]
            }
            st.table(pd.DataFrame(data))
            
            # 타점 예측 설명
            st.write(f"📈 **분석:** 현재 주가에서 저점까지는 약 **{d_low:.1f}%** 하락이 필요하며, 고점까지는 **{d_high:.1f}%** 상승 여력이 있습니다.")
            st.info("💡 타점 도달은 과거 6개월간의 변동성 데이터를 바탕으로 한 기술적 수치입니다.")
        else:
            st.error("해당 이름으로 주식을 찾을 수 없습니다. 정확한 이름을 입력해주세요.")