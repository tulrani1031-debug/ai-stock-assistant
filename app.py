import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 v2.0")

# 1. 환율 및 데이터 분석 함수
@st.cache_data(ttl=3600)
def get_exchange_rate():
    return float(yf.Ticker("USDKRW=X").history(period="1d")["Close"].iloc[-1])

@st.cache_data(ttl=600)
def analyze_stock(ticker, is_domestic):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="3mo")
        if len(df) < 20: return None
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        ret5 = (df['Close'].iloc[-1] / df['Close'].iloc[-5] - 1) * 100
        ret20 = (df['Close'].iloc[-1] / df['Close'].iloc[-20] - 1) * 100
        vol_chg = ((df['Volume'].iloc[-1] / df['Volume'].tail(20).mean()) - 1) * 100
        
        score = (40 if ma5 > ma20 else 0) + (30 if ret20 > 0 else 0) + (20 if vol_chg > 0 else 0) + (10 if ret5 > 0 else 0)
        risk = "높음" if df['Close'].std() / curr > 0.05 else "보통"
        
        return {"price": curr, "score": score, "ma5": ma5, "ma20": ma20, "ret5": ret5, "ret20": ret20, "vol": vol_chg, "risk": risk}
    except: return None

# 2. 종목 리스트 (확장된 후보군)
kor_tickers = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("셀트리온", "068270.KS"), ("기아", "000270.KS"), ("LG에너지솔루션", "373220.KS"), ("POSCO홀딩스", "005490.KS"), ("삼성바이오로직스", "207940.KS"), ("LG화학", "051910.KS")]
us_tickers = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI"), ("Microsoft", "MSFT"), ("Google", "GOOGL"), ("Amazon", "AMZN"), ("AMD", "AMD"), ("Meta", "META")]

# 3. 사이드바 및 예산
st.sidebar.title("💰 투자 예산 설정")
budget = st.sidebar.number_input("예산 (원)", value=1000000)
rate = get_exchange_rate()

# 4. 분석 수행
data_dict = {}
for name, ticker in (kor_tickers + us_tickers):
    res = analyze_stock(ticker, ".KS" in ticker)
    if res: data_dict[name] = {**res, "ticker": ticker, "is_dom": ".KS" in ticker}

# 5. 메인 레이아웃
st.title("🔮 서윤의 주식 마법사 PRO v2.0")
tab1, tab2, tab3 = st.tabs(["🚀 AI TOP 5 추천", "📊 종목 비교", "🧩 포트폴리오"])

with tab1:
    for cat, tickers in [("국내", kor_tickers), ("해외", us_tickers)]:
        st.subheader(f"{'🇰🇷' if cat=='국내' else '🇺🇸'} {cat} TOP 5")
        sorted_list = sorted([k for k in data_dict if k in [x[0] for x in tickers]], key=lambda x: data_dict[x]['score'], reverse=True)[:5]
        
        for idx, name in enumerate(sorted_list):
            d = data_dict[name]
            curr_price = d['price'] if d['is_dom'] else d['price'] * rate
            qty = int(budget / curr_price) if d['is_dom'] else int((budget/rate) / d['price'])
            
            with st.expander(f"{idx+1}위 {name} - AI {d['score']}점 ({'강력매수' if d['score']>80 else '매수'})"):
                c1, c2, c3 = st.columns(3)
                c1.metric("현재가", f"{'₩' if d['is_dom'] else '$'}{d['price']:.2f}")
                c2.metric("구매 가능 수량", f"{qty}주")
                c3.metric("AI 분석", f"수익률 {d['ret20']:.1f}%")
                st.write(f"**선정 이유:** MA5/MA20 추세 양호, 최근 20일 수익률 {d['ret20']:.1f}%, 거래량 변동률 {d['vol']:.1f}%")

with tab2:
    st.subheader("⚔️ 종목 비교 배틀")
    c1, c2 = st.columns(2)
    s1 = c1.selectbox("종목 1", list(data_dict.keys()))
    s2 = c2.selectbox("종목 2", list(data_dict.keys()))
    if st.button("배틀 결과 확인"):
        d1, d2 = data_dict[s1], data_dict[s2]
        st.write(f"### 승자: {'종목 1' if d1['score'] > d2['score'] else '종목 2'}")
        st.table(pd.DataFrame([d1, d2], index=[s1, s2])[['score', 'ret20', 'risk']])

with tab3:
    st.subheader("💰 AI 포트폴리오 제안")
    total_score = sum(d['score'] for d in data_dict.values())
    for name, d in data_dict.items():
        st.write(f"**{name}**: 비중 {(d['score']/total_score)*100:.1f}%")