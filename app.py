import streamlit as st
import numpy as np
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 2026")

# 1. AI 데이터 분석 함수
@st.cache_data(ttl=600)
def get_analysis(ticker):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="3mo")
        if df.empty: return None
        close = df["Close"]
        current = float(close.iloc[-1])
        ma5, ma20 = close.tail(5).mean(), close.tail(20).mean()
        vol = df["Volume"].iloc[-1]
        vol_avg = df["Volume"].tail(20).mean()
        
        score = int((ma5 > ma20)*40 + (current > ma20)*30 + (vol > vol_avg)*20 + (current > close.iloc[-5])*10)
        return {"price": current, "score": score, "ma5": ma5, "ma20": ma20, "vol_chg": (vol/vol_avg-1)*100, "vol": vol}
    except: return None

# 데이터 준비
stocks = [("삼성전자", "005930.KS"), ("NVIDIA", "NVDA"), ("Tesla", "TSLA"), ("SK하이닉스", "000660.KS"), ("Palantir", "PLTR"), ("SoFi", "SOFI")]
data_map = {name: get_analysis(ticker) for name, ticker in stocks}
valid_data = {k: v for k, v in data_map.items() if v}

# 1. 오늘의 1등 주식
top_stock = max(valid_data, key=lambda k: valid_data[k]['score'])
st.title("🔮 서윤의 주식 마법사 PRO")
c1, c2 = st.columns([1, 2])
with c1:
    st.metric("🏆 오늘의 1등 추천", top_stock, f"{valid_data[top_stock]['score']}점")
    st.subheader("추천 : 강력매수" if valid_data[top_stock]['score'] > 80 else "매수")

# 2. 지금 사도 되는가?
if st.button("🚨 지금 사도 될까?"):
    score = valid_data[top_stock]['score']
    st.info("매수 추천" if score > 70 else ("관망 추천" if score > 40 else "고점 주의"))

# 3. 상승 확률 & 4. 숨은 보석
col1, col2 = st.columns(2)
with col1:
    st.subheader("📈 삼성전자 상승 확률")
    st.progress(0.8) # 예시 80%
    st.write("████████░░ 80%")
with col2:
    st.subheader("💎 오늘의 보석주")
    gem = min(valid_data, key=lambda k: valid_data[k]['price'])
    st.success(f"{gem} (AI {valid_data[gem]['score']}점, 저평가 매력)")

# 5. 종목 배틀
st.divider()
st.subheader("⚔️ 종목 배틀 (삼성 vs 하이닉스)")
if st.button("배틀 시작"):
    a, b = valid_data["삼성전자"]["score"], valid_data["SK하이닉스"]["score"]
    winner = "SK하이닉스" if b > a else "삼성전자"
    st.write(f"### AI 승자 : {winner} ({max(a,b)} : {min(a,b)})")

# 6, 7. 시뮬레이터 & 랜덤픽
c1, c2 = st.columns(2)
with c1:
    st.subheader("🤑 100만원 투자 시뮬레이터")
    st.write(f"1개월 후 예상: {int(1000000 * 1.08):,}원")
with c2:
    st.subheader("🎰 AI 랜덤 픽")
    if st.button("오늘의 한방픽"):
        st.write(f"🎯 **{np.random.choice(list(valid_data.keys()))}**")

# 8, 9, 10. 성적표 & 급등탐지기 & TOP 5
st.divider()
st.subheader("👑 오늘 가장 살만한 종목 TOP 5")
sorted_stocks = sorted(valid_data.items(), key=lambda x: x[1]['score'], reverse=True)
for i, (name, val) in enumerate(sorted_stocks[:5]):
    st.write(f"{i+1}위. **{name}** - {val['score']}점")

st.sidebar.subheader("🚀 급등 탐지기")
for name, val in valid_data.items():
    if val['vol_chg'] > 50:
        st.sidebar.error(f"🚨 {name} 거래량 +{val['vol_chg']:.0f}%")