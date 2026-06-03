import streamlit as st
import yfinance as yf
import pandas as pd

# 환율 정보 (실시간 데이터로 갱신)
def get_usd_to_krw():
    try:
        return yf.Ticker("USDKRW=X").history(period="1d")['Close'].iloc[-1]
    except:
        return 1380 # 비상시 고정 환율

# 분석 엔진
def analyze_stock(ticker_symbol, is_us=False):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="1mo")
    
    # 지표 계산
    df['MA20'] = df['Close'].rolling(20).mean()
    df['STD'] = df['Close'].rolling(20).std()
    df['Upper'] = df['MA20'] + (df['STD'] * 2)
    df['Lower'] = df['MA20'] - (df['STD'] * 2)
    
    curr = df['Close'].iloc[-1]
    
    # 환율 변환
    if is_us:
        rate = get_usd_to_krw()
        curr_krw = curr * rate
    else:
        curr_krw = curr
        
    return {
        "종목": ticker_symbol,
        "현재가": f"{curr_krw:,.0f}원",
        "저점(매수타점)": f"{df['Lower'].iloc[-1] * (rate if is_us else 1):,.0f}원",
        "고점(매도타점)": f"{df['Upper'].iloc[-1] * (rate if is_us else 1):,.0f}원"
    }

st.title("🔥 실시간 급등 후보 종목 추천")

# 분석 대상 (시장 주도주)
domestic = "005930.KS" # 삼성전자 예시
overseas = "NVDA"      # 엔비디아 예시

data = [analyze_stock(domestic), analyze_stock(overseas, is_us=True)]
df_res = pd.DataFrame(data)

st.table(df_res)
st.warning("⚠️ 이 데이터는 실시간 기술적 지표 기준입니다. 투자의 책임은 본인에게 있습니다.")