import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(layout="wide", page_title="🔮 서윤의 주식 마법사 PRO v4.5")

# 1. 고도화된 AI 분석 로직
@st.cache_data(ttl=600)
def get_full_analysis(ticker, is_dom, budget, rate):
    try:
        t = yf.Ticker(ticker)
        df = t.history(period="6mo")
        if len(df) < 20: return None
        
        curr = float(df['Close'].iloc[-1])
        ma5, ma20 = df['Close'].rolling(5).mean().iloc[-1], df['Close'].rolling(20).mean().iloc[-1]
        std = df['Close'].rolling(20).std().iloc[-1]
        vol_chg = ((df['Volume'].iloc[-1] / df['Volume'].tail(20).mean()) - 1) * 100
        
        # AI 점수 및 예산 적합도
        score = int((ma5 > ma20)*40 + (curr > ma20)*20 + (vol_chg > 0)*20 + 20)
        fit_score = max(0, 100 - abs((budget * 0.2) - (curr * (1 if is_dom else rate))) / (budget * 0.2) * 100)
        
        # AI 추정치
        low = curr * (1 - (std/curr)*1.2); high = curr * (1 + (std/curr)*1.5)
        qty = int(budget / (curr if is_dom else curr * rate))
        
        return {
            "price": curr, "score": score, "fit": fit_score, "low": low, "high": high,
            "qty": qty, "cash": budget - (qty * (curr if is_dom else curr * rate)),
            "ret5": (df['Close'].iloc[-1]/df['Close'].iloc[-5]-1)*100,
            "ret20": (df['Close'].iloc[-1]/df['Close'].iloc[-20]-1)*100,
            "vol": vol_chg, "risk": "높음" if std/curr > 0.05 else "보통",
            "trend": "상승" if ma5 > ma20 else "하락"
        }
    except: return None

# 2. UI 구성
st.title("🔮 서윤의 주식 마법사 PRO v4.5")
budget = st.sidebar.number_input("투자 예산 (KRW)", value=1000000, step=10000)
rate = 1380 

# 데이터 분석
KOR = [("삼성전자", "005930.KS"), ("SK하이닉스", "000660.KS"), ("현대차", "005380.KS"), ("NAVER", "035420.KS"), ("LG에너지솔루션", "373220.KS")]
US = [("NVIDIA", "NVDA"), ("Palantir", "PLTR"), ("Tesla", "TSLA"), ("Apple", "AAPL"), ("SoFi", "SOFI")]

def display_card(name, ticker, is_dom):
    res = get_full_analysis(ticker, is_dom, budget, rate)
    if not res or res['qty'] == 0: return None
    
    # 카드형 UI
    with st.container(border=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader(name)
            st.metric("현재가", f"{'₩' if is_dom else '$'}{res['price']:.2f}")
            st.write(f"**AI 점수:** {res['score']}점 (적합도 {res['fit']:.0f}점)")
            st.write(f"**의견:** {'🔥 강력매수' if res['score']>80 else '👍 매수'}")
        with col2:
            c1, c2, c3 = st.columns(3)
            c1.metric("예상 수익률", f"+{((res['high']-res['price'])/res['price']*100):.1f}%")
            c2.metric("구매 가능", f"{res['qty']}주")
            c3.metric("남은 현금", f"{res['cash']:,.0f}원")
            st.caption(f"선정 이유: {res['trend']} 추세, 5일 수익률 {res['ret5']:.1f}%, 위험도 {res['risk']}")
    return (name, (res['score'] + res['fit']) / 2)

tab1, tab2 = st.tabs(["🚀 국내/해외 맞춤 TOP 5", "🧩 상세 분석 대시보드"])

with tab1:
    col1, col2 = st.columns(2)
    for i, (label, stocks, dom) in enumerate([("🇰🇷 국내", KOR, True), ("🇺🇸 해외", US, False)]):
        with (col1 if i==0 else col2):
            st.subheader(f"{label} 추천 TOP 5")
            results = []
            for n, t in stocks:
                val = display_card(n, t, dom)
                if val: results.append(val)
            results.sort(key=lambda x: x[1], reverse=True)

with tab2:
    st.info("개별 종목 정밀 분석 차트 및 지표를 확인하세요.")
    # (차트 시각화 확장 가능)